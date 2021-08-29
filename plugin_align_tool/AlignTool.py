import nanome
from nanome.api import AsyncPluginInstance
from nanome.api.ui import DropdownItem, LayoutNode
from nanome.util import async_callback, Logs, ComplexUtils
from nanome.util.enums import NotificationTypes
from os import path


BASE_PATH = path.dirname(f'{path.realpath(__file__)}')
MENU_PATH = path.join(BASE_PATH, 'menu.json')


class AlignMenu:

    def __init__(self, plugin):
        self.plugin = plugin
        self._menu = nanome.ui.Menu.io.from_json(MENU_PATH)

        self.list_reference = self._menu.root.find_node('list_reference').get_content()
        self.list_targets = self._menu.root.find_node('list_targets').get_content()
        self.btn_submit = self._menu.root.find_node('btn_align').get_content()
        self.btn_submit.register_pressed_callback(self.submit_form)

    def render(self, complex_list):
        """Populate complex dropdowns with complexes.

        complex_list: List of shallow complexes
        """
        self._menu.enabled = True

        # Set up reference complex buttons
        btn_list = self.create_complex_btns(complex_list)
        for ln_btn in btn_list:
            btn = ln_btn.get_children()[0].get_content()
            btn.register_pressed_callback(self.reference_complex_clicked)
        self.list_reference.items = btn_list

        # Set up target complex buttons
        self.list_targets.items = self.create_complex_btns(complex_list)
        self.plugin.update_menu(self._menu)

    def reference_complex_clicked(self, clicked_btn):
        # Only one reference complex can be selected at a time.
        if clicked_btn.selected:
            for ln_btn in self.list_reference.items:
                btn = ln_btn.get_children()[0].get_content()
                if btn.selected and btn._content_id != clicked_btn._content_id:
                    btn.selected = False
        self.plugin.update_content(self.list_reference)

    def create_complex_btns(self, complex_list):
        btn_list = []
        for comp in complex_list:
            # Slightly annoying, but to fix z-index issues,
            # we need to add two layoutnodes around the button
            ln = LayoutNode()
            ln2 = ln.create_child_node()
            ln2.forward_dist = 0.004
            btn = ln2.add_new_toggle_switch(comp.full_name)
            btn.complex_index = comp.index
            ln2.set_content(btn)
            btn_list.append(ln)
        return btn_list

    def create_dropdown_items(self, complexes):
        """Generate list of dropdown items corresponding to provided complexes."""
        complex_ddis = []
        for struct in complexes:
            ddi = DropdownItem(struct.full_name)
            ddi.complex_index = struct.index
            complex_ddis.append(ddi)
        return complex_ddis

    @async_callback
    async def submit_form(self, btn):
        reference_index = next(iter([
            item.get_children()[0].get_content().complex_index
            for item in self.list_reference.items
            if item.get_children()[0].get_content().selected
        ]), None)
        if not reference_index:
            self.plugin.send_notification(NotificationTypes.error, "Please Select a Reference complex")
            return

        target_indices = [
            item.get_children()[0].get_content().complex_index
            for item in self.list_targets.items
            if item.get_children()[0].get_content().selected
        ]
        if not target_indices:
            self.plugin.send_notification(NotificationTypes.error, "Please Select one or more target complexes.")
            return

        default_text = "Align"
        processing_text = "Aligning..."
        self.btn_submit.text.value.set_all(processing_text)
        self.btn_submit.unusable = True
        self.plugin.update_content(self.btn_submit)
        await self.plugin.align_complexes(reference_index, target_indices)

        # Deselect buttons after alignment done
        self.deselect_buttons(self.list_reference)
        self.deselect_buttons(self.list_targets)
        # Reset submit button text
        self.btn_submit.text.value.set_all(default_text)
        self.btn_submit.unusable = False
        self.plugin.update_content(self.btn_submit)

    def deselect_buttons(self, ui_list):
        """Deselect all buttons in the provided UIList object."""
        btn_list = [item.get_children()[0].get_content() for item in ui_list.items]
        for btn in btn_list:
            btn.selected = False
        self.plugin.update_content(ui_list)


class AlignToolPlugin(AsyncPluginInstance):

    @async_callback
    async def on_run(self):
        self.menu = AlignMenu(self)
        complex_list = await self.request_complex_list()
        self.menu.render(complex_list)

    async def align_complexes(self, reference_index, target_indices):
        Logs.message("Starting Alignment.")
        complexes = await self.request_complexes([reference_index, *target_indices])
        reference = next(comp for comp in complexes if comp.index == reference_index)
        targets = [comp for comp in complexes if comp.index != reference_index]

        for target in targets:
            Logs.debug(f"Aligning {target.full_name} to {reference.full_name}")
            Logs.debug(f'{target.full_name} Starting Position: {target.position._positions}')
            ComplexUtils.align_to(target, reference)
            Logs.debug(f'{target.full_name} Final Position: {target.position._positions}')
            target.boxed = True

        reference.boxed = True
        await self.update_structures_deep([reference, *targets])
        self.send_notification(NotificationTypes.success, "Complexes aligned!")
        Logs.message("Alignment Completed.")

    @async_callback
    async def on_complex_list_updated(self, complexes):
        self.menu.render(complexes)

    @async_callback
    async def on_complex_added(self):
        complexes = await self.request_complex_list()
        await self.menu.render(complexes)

    @async_callback
    async def on_complex_removed(self):
        complexes = await self.request_complex_list()
        await self.menu.render(complexes)
