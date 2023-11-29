import math
from nanome.api import shapes
from nanome.util import enums, Vector3, Color

class ComplexGraph:

    def __init__(self, plugin, comp_id):
        self._plugin = plugin
        self.comp_id = comp_id
        self.x_axis = None
        self.y_axis = None
        self.z_axis = None
        self.x_labels = []
        self.y_labels = []
        self.z_labels = []

    # def __del__(self):
    #     graph_components = [
    #         shp for shp in
    #         [self.x_axis, self.y_axis, self.z_axis,
    #         *self.x_labels, *self.y_labels, *self.z_labels]
    #         if shp is not None
    #     ]
    #     shapes.Shape.destroy_multiple(graph_components)

    async def render(self):
        [comp] = await self._plugin.request_complexes([self.comp_id])
        x_min = math.floor(min([atom.position.x for atom in comp.atoms]))
        x_max = math.ceil(max([atom.position.x for atom in comp.atoms]))
        x_start = Vector3(min(x_min, 0), 0, 0)
        x_end = Vector3(max(x_max, 0), 0, 0)
        self.x_axis = self.draw_axis(x_start, x_end, comp)
        self.x_labels = self.draw_labels(self.x_axis)
        
        y_min = math.floor(min([atom.position.y for atom in comp.atoms]))
        y_max = math.ceil(max([atom.position.y for atom in comp.atoms]))
        y_start = Vector3(0, min(y_min, 0), 0)
        y_end = Vector3(0, max(y_max, 0), 0)
        self.y_axis = self.draw_axis(y_start, y_end, comp)
        self.y_labels = self.draw_labels(self.y_axis)
        
        z_min = math.floor(min([atom.position.z for atom in comp.atoms]))
        z_max = math.ceil(max([atom.position.z for atom in comp.atoms]))
        z_start = Vector3(0, 0, min(z_min, 0))
        z_end = Vector3(0, 0, max(z_max, 0))
        self.z_axis = self.draw_axis(z_start, z_end, comp)
        self.z_labels = self.draw_labels(self.z_axis)
        await shapes.Shape.upload_multiple([
            self.x_axis,
            self.y_axis,
            self.z_axis,
            *self.x_labels,
            *self.y_labels,
            *self.z_labels
        ])
    
    @staticmethod
    def draw_axis(start: Vector3, end: Vector3, comp):
        # Draw line between spheres.
        axis = shapes.Line()
        axis.thickness = 0.5
        axis.dash_distance = 0
        axis.color = Color.White()
        anchor1, anchor2 = axis.anchors
        anchor1.anchor_type = enums.ShapeAnchorType.Complex
        anchor1.target = comp.index
        anchor1.local_offset = start
        anchor2.anchor_type = enums.ShapeAnchorType.Complex
        anchor2.target = comp.index
        anchor2.local_offset = end
        return axis
    
    @staticmethod
    def draw_labels(axis_line):
        """Add labels to axis line."""
        anchor1, anchor2 = axis_line.anchors
        label1 = shapes.Label()
        label1.text = f'({int(anchor1.local_offset.x)}, {int(anchor1.local_offset.y)}, {int(anchor1.local_offset.z)})'
        label1.anchors = [anchor1]
        label2 = shapes.Label()
        label2.text = f'({int(anchor2.local_offset.x)}, {int(anchor2.local_offset.y)}, {int(anchor2.local_offset.z)})'
        label2.anchors = [anchor2]
        return [label1, label2]
