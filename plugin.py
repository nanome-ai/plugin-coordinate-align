import nanome
from nanome.api import Plugin, AsyncPluginInstance
from nanome.api.ui import DropdownItem
from nanome.util import async_callback, Logs, ComplexUtils
from nanome.util.enums import NotificationTypes
from os import environ, path


BASE_PATH = path.dirname(f'{path.realpath(__file__)}')
MENU_PATH = path.join(BASE_PATH, 'menu.json')


class AlignMenu():

    def __init__(self, plugin):
        self.plugin = plugin
        self._menu = nanome.ui.Menu.io.from_json(MENU_PATH)
        self.dd_reference = self._menu.root.find_node('dd_reference').get_content()
        self.dd_complex = self._menu.root.find_node('dd_complex').get_content()
        self.btn_submit = self._menu.root.find_node('btn_align').get_content()
        self.btn_submit.register_pressed_callback(self.submit_form)

    @property
    def index(self):
        return self._menu.index

    @index.setter
    def index(self, value):
        self._menu.index = value

    @property
    def enabled(self):
        return self._menu.enabled

    @enabled.setter
    def enabled(self, value):
        self._menu.enabled = value

    def render(self, complex_list):
        self.enabled = True

        default_reference = None
        default_target = None
        if len(complex_list) >= 2:
            default_reference = complex_list[0]
            default_target = complex_list[1]

        complex_ddis = self.create_dropdown_items(complex_list)
        self.dd_reference.items = self.create_dropdown_items(complex_list)
        self.dd_complex.items = self.create_dropdown_items(complex_list)

        if default_reference:
            for item in self.dd_reference.items:
                if item.complex_index == default_reference.index:
                    item.selected = True
                    break
        if default_target:
            for item in self.dd_complex.items:
                if item.complex_index == default_target.index:
                    item.selected = True
                    break
        self.plugin.update_menu(self._menu)
        return

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
            item.complex_index
            for item in self.dd_reference.items
            if item.selected
        ]))
        target_index = next(iter([
            item.complex_index
            for item in self.dd_complex.items
            if item.selected
        ]))
        await self.plugin.align_complexes(reference_index, target_index)

class AlignPlugin(AsyncPluginInstance):

    @async_callback
    async def on_run(self):
        self.menu = AlignMenu(self)
        complex_list = await self.request_complex_list()
        self.menu.render(complex_list)

    async def align_complexes(self, reference_index, target_index):
        complexes = await self.request_complexes([reference_index, target_index])
        reference = complexes[0]
        comp = complexes[1]
        self.send_notification(NotificationTypes.message, f"Aligning {comp.name} to {reference.name}")    
        ComplexUtils.align_to(comp, reference)
        await self.update_structures_deep([comp])
        self.send_notification(NotificationTypes.success, f"Complexes aligned!")    
