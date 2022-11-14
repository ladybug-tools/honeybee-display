"""Test the Aperture to_vis_set method."""
from ladybug_geometry.geometry3d import Point3D, Face3D
from honeybee.aperture import Aperture
from ladybug_display.geometry3d import DisplayFace3D
from ladybug_display.visualization import VisualizationSet, ContextGeometry


def test_aperture_to_vis_set():
    """Test the default output of Aperture.to_vis_set()."""
    pts_1 = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(5, 0, 3), Point3D(5, 0, 0))
    aperture = Aperture('RectangleWindow', Face3D(pts_1))
    aperture.louvers_by_count(3, 0.2, 0.1, 5)
    vis_set = aperture.to_vis_set()

    assert isinstance(vis_set, VisualizationSet)
    assert len(vis_set) == 1
    assert isinstance(vis_set[0], ContextGeometry)
    for geo in vis_set[0]:
        assert isinstance(geo, DisplayFace3D)
