"""Test the Room to_vis_set method."""
from ladybug_geometry.geometry3d import Point3D, Face3D, Polyface3D
from honeybee.room import Room
from ladybug_display.geometry3d import DisplayFace3D
from ladybug_display.visualization import VisualizationSet, ContextGeometry


def test_room_to_vis_set():
    """Test the default output of Room.to_vis_set()."""
    bound_pts = [Point3D(0, 0), Point3D(3, 0), Point3D(3, 3), Point3D(0, 3)]
    hole_pts = [Point3D(1, 1, 0), Point3D(2, 1, 0), Point3D(2, 2, 0), Point3D(1, 2, 0)]
    face = Face3D(bound_pts, None, [hole_pts])
    polyface = Polyface3D.from_offset_face(face, 3)
    room = Room.from_polyface3d('DonutZone', polyface)
    vis_set = room.to_vis_set()

    assert isinstance(vis_set, VisualizationSet)
    assert len(vis_set) == 1
    assert isinstance(vis_set[0], ContextGeometry)
    for geo in vis_set[0]:
        assert isinstance(geo, DisplayFace3D)
