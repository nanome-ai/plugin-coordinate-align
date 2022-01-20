from nanome.api import Plugin
from plugin_align_tool.AlignTool import AlignToolPlugin


if __name__ == "__main__":
    # Information describing the plugin
    name = 'Coordinate Align'
    description = 'Override the 3D coordinates of a complex to be relative to a reference complex'
    category = 'Alignment'
    has_advanced = False
    Plugin.setup(name, description, category, has_advanced, AlignToolPlugin)
