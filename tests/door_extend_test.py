"""Test the Shade to_vis_set method."""
from ladybug_geometry.geometry3d import Point3D, Face3D
from honeybee.shade import Shade
from ladybug_display.geometry3d import DisplayFace3D
from ladybug_display.visualization import VisualizationSet, ContextGeometry


def test_shade_to_vis_set():
    """Test the default output of Shade.to_vis_set()."""
    pts = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(1, 0, 3), Point3D(1, 0, 0))
    shade = Shade('TestShade', Face3D(pts))
    vis_set = shade.to_vis_set()

    assert isinstance(vis_set, VisualizationSet)
    assert len(vis_set) == 1
    assert isinstance(vis_set[0], ContextGeometry)
    for geo in vis_set[0]:
        assert isinstance(geo, DisplayFace3D)
