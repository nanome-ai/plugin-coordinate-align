import nanome
from nanome.api import Plugin, PluginInstance
from nanome.util import Logs


class HelloNanomePlugin(PluginInstance):

    def on_run(self):
        message = "Hello Nanome!"
        self.send_notification(nanome.util.enums.NotificationTypes.success, message)
        Logs.message(message)


# Create Plugin, and attach specific PluginInstance to it.
if __name__ == "__main__":
    # Information describing the plugin
    name = 'Hello Nanome'
    description = "Send a notification that says `Hello Nanome`"
    category = 'Demo'
    has_advanced = False
    Plugin.setup(name, description, category, has_advanced, HelloNanomePlugin)