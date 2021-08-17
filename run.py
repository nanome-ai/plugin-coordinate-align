from nanome.api import Plugin
from plugin_align_tool.AlignTool import AlignToolPlugin


if __name__ == "__main__":
    # Information describing the plugin
    name = 'Align Tool'
    description = 'Override the 3D local coordinate space of a complex to be relative to a reference complex'
    category = 'Align'
    has_advanced = False
    Plugin.setup(name, description, category, has_advanced, AlignToolPlugin)
