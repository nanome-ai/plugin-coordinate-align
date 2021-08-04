from nanome.api import Plugin
from plugin import AlignPlugin

if __name__ == "__main__":
    # Information describing the plugin
    name = 'Align Tool'
    description = "Set complex matrix to be in relation to reference complex."
    category = 'Align'
    has_advanced = False
    Plugin.setup(name, description, category, has_advanced, AlignPlugin)
