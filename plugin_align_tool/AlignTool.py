import nanome
from nanome.api import AsyncPluginInstance
from nanome.api.structure import Complex
from nanome.api.ui import DropdownItem
from nanome.util import async_callback, Logs, ComplexUtils
from nanome.util.enums import NotificationTypes
from os import path


BASE_PATH = path.dirname(f'{path.realpath(__file__)}')
MENU_PATH = path.join(BASE_PATH, 'menu.json')
CONFIRMATION_MENU_PATH = path.join(BASE_PATH, 'confirmation_menu.json')
BACK_ICON = path.join(BASE_PATH, 'BackIcon.png')


class ConfirmMenu:
    """Menu that pops up after successful align."""

    def __init__(self, plugin):
        self.plugin = plugin
        self._menu = nanome.ui.Menu.io.from_json(CONFIRMATION_MENU_PATH)
        self._menu.index = 220  # arbitrary

    @property
    def lbl_message(self):
        return self._menu.root.find_node('lbl_message').get_content()

    @property
    def btn_ok(self):
        return self._menu.root.find_node('btn_ok').get_content()

    @classmethod
    def create(cls, plugin):
        menu = cls(plugin)
        menu.btn_ok.register_pressed_callback(menu.close_menu)
        return menu

    def render(self, reference_name, target_names):
        # Render menu from json again, so that placeholders can be replaced
        self.update_label(reference_name, target_names)
        self._menu.enabled = True
        self.plugin.update_menu(self._menu)

    def update_label(self, reference_name, target_names):
        message = self.lbl_message.text_value
        reference_name = reference_name
        target_names = ', '.join(target_names)

        replacement_dict = {
            "{{reference_complex}}": reference_name,
            "{{target_complexes}}": target_names
        }
        new_message = message
        for key, value in replacement_dict.items():
            new_message = new_message.replace(key, value)
        self.lbl_message.text_value = new_message

    def close_menu(self, btn):
        self._menu.enabled = False
        self.plugin.update_menu(self._menu)


class AlignMenu:

    def __init__(self, plugin):
        self.plugin = plugin
        self._menu = nanome.ui.Menu.io.from_json(MENU_PATH)

        self.dd_reference = self._menu.root.find_node('dd_reference').get_content()
        self.dd_reference.register_item_clicked_callback(self.reference_complex_clicked)

        self.dd_targets = self._menu.root.find_node('dd_targets').get_content()
        self.dd_targets.register_item_clicked_callback(self.multi_select_dropdown)

        self.btn_submit = self._menu.root.find_node('btn_align').get_content()
        self.ln_recent = self._menu.root.find_node('Recent')
        self.lbl_recent = self._menu.root.find_node('lbl_recent').get_content()
        self.btn_recent = self._menu.root.find_node('btn_recent').get_content()
        self.btn_undo_recent = self._menu.root.find_node('btn_undo_recent').get_content()
        self.btn_undo_recent.register_pressed_callback(self.undo_recent_alignment)
        self.btn_submit.register_pressed_callback(self.submit_form)

    def enable(self):
        self._menu.enabled = True
        self.plugin.update_menu(self._menu)

    def render(self, complex_list):
        """Populate complex dropdowns with complexes.

        complex_list: List of shallow complexes
        """
        self.complexes = complex_list
        # Set up reference complex buttons
        self.dd_reference.items = self.create_complex_dropdown_items(complex_list)

        # Set up target complex buttons
        self.dd_targets.items = self.create_complex_dropdown_items(complex_list)
        for item in self.dd_targets.items:
            item.close_on_selected = False

        self.btn_undo_recent.icon.value.set_all(BACK_ICON)
        self.plugin.update_content(self.dd_targets, self.dd_reference, self.btn_undo_recent)

    def multi_select_dropdown(self, dropdown, item):
        if not hasattr(dropdown, '_selected_items'):
            dropdown._selected_items = []

        selected_items = dropdown._selected_items
        if item not in selected_items:
            selected_items.append(item)
        else:
            selected_items.remove(item)
            item.selected = False

        for ddi in selected_items:
            ddi.selected = True

        dropdown.permanent_title = ','.join([ddi.name for ddi in selected_items])
        dropdown.use_permanent_title = len(selected_items) > 1
        self.plugin.update_content(dropdown)

    def reference_complex_clicked(self, dropdown, ddi):
        # Only one reference complex can be selected at a time.
        if ddi.selected:
            for item in self.dd_reference.items:
                if item.selected and item.name != ddi.name:
                    item.selected = False
        self.plugin.update_content(self.dd_reference)

    def create_complex_dropdown_items(self, complex_list):
        ddi_list = []
        for comp in complex_list:
            ddi = DropdownItem(comp.full_name)
            ddi.complex_index = comp.index
            ddi_list.append(ddi)
        return ddi_list

    def create_dropdown_items(self, complexes):
        """Generate list of dropdown items corresponding to provided complexes."""
        complex_ddis = []
        for struct in complexes:
            ddi = DropdownItem(struct.full_name)
            ddi.complex_index = struct.index
            complex_ddis.append(ddi)
        return complex_ddis

    @staticmethod
    def alignment_string(reference_name, target_names):
        target_names = ', '.join(target_names)
        return f"Ref: {reference_name} - Aligned: {target_names}"

    @async_callback
    async def submit_form(self, btn):
        reference_index = next(iter([
            item.complex_index for item in self.dd_reference.items if item.selected
        ]), None)
        if not reference_index:
            self.plugin.send_notification(NotificationTypes.error, "Please Select a Reference complex")
            return

        target_indices = [item.complex_index for item in self.dd_targets.items if item.selected]
        if not target_indices:
            self.plugin.send_notification(NotificationTypes.error, "Please Select one or more target complexes.")
            return

        default_text = "Align"
        processing_text = "Aligning..."
        self.btn_submit.text.value.set_all(processing_text)
        self.btn_submit.unusable = True
        self.plugin.update_content(self.btn_submit)
        await self.plugin.align_complexes(reference_index, target_indices)

        self.setup_recents(reference_index, target_indices)

        # Deselect buttons after alignment done
        self.deselect_buttons(self.dd_reference)
        self.deselect_buttons(self.dd_targets)
        # Reset submit button text
        self.btn_submit.text.value.set_all(default_text)
        self.btn_submit.unusable = False
        self.btn_submit.selected = False
        self.plugin.update_content(self.btn_submit)

        self.dd_targets.permanent_title = 'None'
        self.dd_targets.use_permanent_title = False
        self.dd_targets._selected_items = []
        self.plugin.update_content(self.dd_targets)

        # Create and render confirmation menu
        reference_name = next(comp.full_name for comp in self.complexes if comp.index == reference_index)
        target_names = [comp.full_name for comp in self.complexes if comp.index in target_indices]
        self.confirm_menu = ConfirmMenu.create(self.plugin)
        self.confirm_menu.render(reference_name, target_names)

    def deselect_buttons(self, dropdown):
        """Deselect all buttons in the provided UIList object."""
        for item in dropdown.items:
            item.selected = False
        self.plugin.update_content(dropdown)

    def setup_recents(self, reference_index, target_indices):
        """Write label describing the most recent alignment done."""
        self.ln_recent.enabled = True
        # get complex_names.
        reference_name = next(comp.full_name for comp in self.complexes if comp.index == reference_index)
        target_names = [comp.full_name for comp in self.complexes if comp.index in target_indices]

        label = self.alignment_string(reference_name, target_names)
        if len(label) > 40:
            full_label = label
            label = f'{label[:37]}...'
            self.btn_recent.tooltip.content = full_label
        else:
            self.btn_recent.tooltip.content = ''

        self.lbl_recent.text_value = label
        self.plugin.update_node(self.ln_recent)
        # Set up undo btn with most recent changes.
        self.btn_undo_recent.previous_target_indices = target_indices

    @async_callback
    async def undo_recent_alignment(self, btn):
        comps_to_undo = [comp for comp in self.complexes if comp.index in btn.previous_target_indices]
        for comp in comps_to_undo:
            # to undo alignment, use old_position + rotation as "reference_complex" to reset origin
            fake_reference = Complex()
            fake_reference.position = comp.old_position
            fake_reference.rotation = comp.old_rotation
            ComplexUtils.align_to(comp, fake_reference)
            # reset position and rotation
            ComplexUtils.reset_transform(comp)

        await self.plugin.update_structures_deep(comps_to_undo)
        label = self.lbl_recent.text_value
        Logs.message(f'Alignment {label} undone')
        self.lbl_recent.text_value = ''
        self.ln_recent.enabled = False
        self.plugin.update_node(self.ln_recent)


class AlignToolPlugin(AsyncPluginInstance):

    def start(self):
        self.menu = AlignMenu(self)

    @async_callback
    async def on_run(self):
        complex_list = await self.request_complex_list()
        self.menu.render(complex_list)
        self.menu.enable()

    async def align_complexes(self, reference_index, target_indices):
        Logs.message("Starting Alignment.")
        complexes = await self.request_complexes([reference_index, *target_indices])
        reference = next(comp for comp in complexes if comp.index == reference_index)
        targets = [comp for comp in complexes if comp.index != reference_index]

        for target in targets:
            Logs.debug(f"Aligning {target.full_name} to {reference.full_name}")
            Logs.debug(f'{target.full_name} Starting Position: {target.position._positions}')
            ComplexUtils.align_to(target, reference)
            target.set_surface_needs_redraw()
            Logs.debug(f'{target.full_name} Final Position: {target.position._positions}')

        # reference.boxed = True
        # make sure complex list on menu contains most recent complexes
        self.menu.complexes = complexes
        await self.update_structures_deep([*targets])
        Logs.message("Alignment Completed.")

    @async_callback
    async def on_complex_list_updated(self, complexes):
        self.menu.render(complexes)

    @async_callback
    async def on_complex_added(self):
        complexes = await self.request_complex_list()
        self.menu.render(complexes)

    @async_callback
    async def on_complex_removed(self):
        complexes = await self.request_complex_list()
        self.menu.render(complexes)
