import nanome
from nanome.api import Plugin, AsyncPluginInstance
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
        # self.btn_calculate.register_pressed_callback(self.submit_form)

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
        self.plugin.update_menu(self._menu)
        return

class AlignPlugin(AsyncPluginInstance):

    @async_callback
    async def on_run(self):
        self.menu = AlignMenu(self)
        complex_list = await self.request_complex_list()
        self.menu.render(complex_list)

    async def align_complexes(self):
        complex_list = await self.request_complex_list()
        complexes = await self.request_complexes([comp.index for comp in complex_list])
        if len(complexes) < 2:
            self.send_notification(NotificationTypes.error, "Requires two or more complexes.")    
        reference = complexes[0]
        comp = complexes[1]
        self.send_notification(NotificationTypes.message, f"Aligning {comp.name} to {reference.name}")    
        ComplexUtils.align_to(comp, reference)
        await self.update_structures_deep([comp])
        self.send_notification(NotificationTypes.success, f"Complexes aligned!")    
