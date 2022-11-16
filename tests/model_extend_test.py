"""Test the Model to_vis_set method."""
from ladybug_display.geometry3d import DisplayMesh3D, DisplayLineSegment3D, \
    DisplayText3D
from ladybug_display.visualization import VisualizationSet, \
    ContextGeometry, AnalysisGeometry, VisualizationData
from honeybee.model import Model


def test_default_to_vis_set():
    """Test the default output of Model.to_vis_set()."""
    model_json = './tests/json/single_family_home.hbjson'
    parsed_model = Model.from_hbjson(model_json)
    vis_set = parsed_model.to_vis_set()

    assert isinstance(vis_set, VisualizationSet)
    assert len(vis_set) == 7
    for geo_obj in vis_set[:-1]:
        assert isinstance(geo_obj, ContextGeometry)
        assert isinstance(geo_obj[0], DisplayMesh3D)
    assert isinstance(vis_set[-1], ContextGeometry)
    assert vis_set[-1].display_name == 'Wireframe'
    assert isinstance(vis_set[-1][0], DisplayLineSegment3D)

    vis_set = parsed_model.to_vis_set(include_wireframe=False)
    assert len(vis_set) == 6
    for geo_obj in vis_set:
        assert isinstance(geo_obj, ContextGeometry)
        assert isinstance(geo_obj[0], DisplayMesh3D)

    vis_set = parsed_model.to_vis_set('none')
    assert len(vis_set) == 1
    for geo_obj in vis_set:
        assert isinstance(geo_obj, ContextGeometry)
        assert isinstance(geo_obj[0], DisplayLineSegment3D)

    vis_set = parsed_model.to_vis_set('boundary_condition', include_wireframe=False)
    print(len(vis_set))
    assert len(vis_set) == 4
    for geo_obj in vis_set:
        assert isinstance(geo_obj, ContextGeometry)
        assert isinstance(geo_obj[0], DisplayMesh3D)

    vis_set = parsed_model.to_vis_set_wireframe()
    assert len(vis_set) == 1
    for geo_obj in vis_set:
        assert isinstance(geo_obj, ContextGeometry)
        assert isinstance(geo_obj[0], DisplayLineSegment3D)


def test_room_attr_to_vis_set():
    """Test the room attribute argument of Model.to_vis_set()."""
    model_json = './tests/json/single_family_home.hbjson'
    parsed_model = Model.from_hbjson(model_json)
    vis_set = parsed_model.to_vis_set('none', room_attr='floor_area')

    assert isinstance(vis_set[0], AnalysisGeometry)
    assert isinstance(vis_set[0][0], VisualizationData)
    assert len(vis_set[0][0].values) == 7

    vis_set = parsed_model.to_vis_set(
        'none', room_attr='floor_area', room_text_labels=True)
    assert isinstance(vis_set[0], ContextGeometry)
    assert len(vis_set[0]) == 7
    for item in vis_set[0]:
        assert isinstance(item, DisplayText3D)


def test_face_attr_to_vis_set():
    """Test the face attribute argument of Model.to_vis_set()."""
    model_json = './tests/json/single_family_home.hbjson'
    parsed_model = Model.from_hbjson(model_json)
    vis_set = parsed_model.to_vis_set('none', face_attr='area')

    assert isinstance(vis_set[0], AnalysisGeometry)
    assert isinstance(vis_set[0][0], VisualizationData)
    assert len(vis_set[0][0].values) == 100

    vis_set = parsed_model.to_vis_set(
        'none', face_attr='area', face_text_labels=True)
    assert isinstance(vis_set[0], ContextGeometry)
    assert len(vis_set[0]) == 100
    for item in vis_set[0]:
        assert isinstance(item, DisplayText3D)
