"""Test the Face to_vis_set method."""
from ladybug_geometry.geometry3d import Point3D, Face3D, Plane
from honeybee.face import Face
from honeybee.aperture import Aperture
from honeybee.door import Door
from ladybug_display.geometry3d import DisplayFace3D
from ladybug_display.visualization import VisualizationSet, ContextGeometry


def test_face_to_vis_set():
    """Test the default output of Face.to_vis_set()."""
    face_face3d = Face3D.from_rectangle(10, 10, Plane(o=Point3D(0, 0, 3)))
    ap_face3d = Face3D.from_rectangle(2, 2, Plane(o=Point3D(2, 2, 3)))
    dr_face3d = Face3D.from_rectangle(2, 2, Plane(o=Point3D(7, 7, 3)))
    face = Face('Test_Roof', face_face3d)
    aperture = Aperture('Test_Skylight', ap_face3d)
    door = Door('Test_Trap_Door', dr_face3d)
    face.add_aperture(aperture)
    face.add_door(door)
    vis_set = face.to_vis_set()

    assert isinstance(vis_set, VisualizationSet)
    assert len(vis_set) == 1
    assert isinstance(vis_set[0], ContextGeometry)
    for geo in vis_set[0]:
        assert isinstance(geo, DisplayFace3D)
