import nanome
from nanome.api import Plugin, AsyncPluginInstance
from nanome.util import async_callback, Logs, ComplexUtils
from nanome.util.enums import NotificationTypes


class AlignPlugin(AsyncPluginInstance):

    @async_callback
    async def on_run(self):
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
