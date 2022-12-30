"""Method to translate a Model to a VisualizationSet."""
import os
import json

from ladybug_geometry.geometry3d import Point3D
from ladybug.datatype.generic import GenericType
from ladybug.color import Color
from ladybug_display.geometry3d import DisplayPoint3D, DisplayLineSegment3D, \
    DisplayFace3D, DisplayMesh3D
from ladybug_display.visualization import VisualizationSet, ContextGeometry, \
    AnalysisGeometry, VisualizationData, VisualizationMetaData
from honeybee.boundarycondition import Outdoors, Ground, Surface
from honeybee.facetype import Wall, RoofCeiling, Floor, AirBoundary
from honeybee.colorobj import ColorRoom, ColorFace

from .colorobj import color_room_to_vis_set, color_face_to_vis_set

TYPE_COLORS = {
    'Wall': Color(230, 180, 60),
    'Roof': Color(128, 20, 20),
    'Floor': Color(128, 128, 128),
    'Air Boundary': Color(255, 255, 200, 100),
    'Interior Wall': Color(230, 215, 150),
    'Ceiling': Color(255, 128, 128),
    'Interior Floor': Color(255, 128, 128),
    'Aperture': Color(64, 180, 255, 100),
    'Door': Color(160, 150, 100),
    'Glass Door': Color(128, 204, 255, 100),
    'Outdoor Shade': Color(120, 75, 190),
    'Context Shade': Color(80, 50, 128),
    'Indoor Shade': Color(159, 99, 255)
}
BC_COLORS = {
    'Outdoors': Color(64, 180, 255),
    'Surface': Color(0, 128, 0),
    'Ground': Color(165, 82, 0),
    'Adiabatic': Color(255, 128, 128),
    'Other': Color(255, 255, 200)
}


def model_to_vis_set(
        model, color_by='type', include_wireframe=True, use_mesh=True,
        hide_color_by=False, room_attr=None, face_attr=None,
        room_text_labels=False, face_text_labels=False,
        room_legend_par=None, face_legend_par=None,
        grid_display_mode='Default', hide_grid=True,
        grid_data_path=None, grid_data_display_mode='Surface'):
    """Translate a Honeybee Model to a VisualizationSet.

    Args:
        model: A Honeybee Model object to be converted to a VisualizationSet.
        color_by: Text that dictates the colors of the Model geometry.
            If none, only a wireframe of the Model will be generated, assuming
            include_wireframe is True. This is useful when the primary purpose of
            the visualization is to display results in relation to the Model
            geometry or display some room_attr or face_attr as an AnalysisGeometry
            or Text labels. (Default: type). Choose from the following:

            * type
            * boundary_condition
            * None

        include_wireframe: Boolean to note whether a ContextGeometry dedicated to
            the Model Wireframe (in DisplayLineSegment3D) should be included
            in the output VisualizationSet. (Default: True).
        use_mesh: Boolean to note whether the colored model geometries should
            be represented with DisplayMesh3D objects (True) instead of DisplayFace3D
            objects (False). Meshes can usually be rendered faster and they scale
            well for large models but all geometry is triangulated (meaning that
            the wireframe in certain platforms might not appear ideal). (Default: True).
        hide_color_by: Boolean to note whether the color_by geometry should be
            hidden or shown by default. Hiding the color-by geometry is useful
            when the primary purpose of the visualization is to display grid_data
            or room/face attributes but it is still desirable to have the option
            to turn on the geometry.
        room_attr: An optional text string of an attribute that the Model Rooms have,
            which will be used to construct a visualization of this attribute in the
            resulting VisualizationSet. This can also be a list of attribute strings and
            a separate VisualizationData will be added to the AnalysisGeometry that
            represents the attribute in the resulting VisualizationSet (or a separate
            ContextGeometry layer if room_text_labels is True). Room attributes
            input here can have '.' that separates the nested attributes from
            one another. For example, 'properties.energy.program_type'.
        face_attr: An optional text string of an attribute that the Model Faces have,
            which will be used to construct a visualization of this attribute in the
            resulting VisualizationSet. This can also be a list of attribute strings and
            a separate VisualizationData will be added to the AnalysisGeometry that
            represents the attribute in the resulting VisualizationSet (or a separate
            ContextGeometry layer if face_text_labels is True). Face attributes
            input here can have '.' that separates the nested attributes from
            one another. For example, 'properties.energy.construction'.
        room_text_labels: A boolean to note whether the input room_attr should
            be expressed as a colored AnalysisGeometry (False) or a ContextGeometry
            as text labels (True). (Default: False).
        face_text_labels: A boolean to note whether the input face_attr should
            be expressed as a colored AnalysisGeometry (False) or a ContextGeometry
            as text labels (True). (Default: False).
        room_legend_par: An optional LegendParameter object to customize the display
            of the room_attr. When room_text_labels is True, only the text_height
            and font will be used to customize the text.
        face_legend_par: An optional LegendParameter object to customize the display
            of the face_attr. When face_text_labels is True, only the text_height
            and font will be used to customize the text.
        grid_display_mode: Text that dictates how the ContextGeometry for Model
            SensorGrids should display in the resulting visualization. The Default
            option will draw sensor points whenever there is no grid_data_path and
            won't draw them at all when grid data is provided, assuming the
            AnalysisGeometry of the grids is sufficient. Choose from the following:

            * Default
            * Points
            * Wireframe
            * Surface
            * SurfaceWithEdges
            * None

        hide_grid: Boolean to note whether the SensorGrid ContextGeometry should be
            hidden or shown by default. (Default: True).
        grid_data_path: An optional path to a folder containing data that aligns
            with the SensorGrids in the model. Any sub folder within this path
            that contains a grids_into.json (and associated CSV files) will be
            converted to an AnalysisGeometry in the resulting VisualizationSet.
            If a vis_metadata.json file is found within this sub-folder, the
            information contained within it will be used to customize the
            AnalysisGeometry. Note that it is acceptable if data and
            grids_info.json exist in the root of this grid_data_path. Also
            note that this argument has no impact if honeybee-radiance is not
            installed and SensorGrids cannot be decoded. (Default: None).
        grid_data_display_mode: Optional text to set the display_mode of the
            AnalysisGeometry that is is generated from the grid_data_path above. Note
            that this has no effect if there are no meshes associated with the model
            SensorGrids. (Default: Surface). Choose from the following:

            * Surface
            * SurfaceWithEdges
            * Wireframe
            * Points

    Returns:
        A VisualizationSet object that represents the model.
    """
    # group the geometries according to typical ContextGeometry layers
    color_by = str(color_by).lower()
    if color_by == 'type':
        # set up a dictionary to hold all geometries
        type_dict = {
            'Wall': [], 'Roof': [], 'Floor': [], 'Air Boundary': [],
            'Interior Wall': [], 'Ceiling': [], 'Interior Floor': [],
            'Aperture': [], 'Door': [], 'Glass Door': [],
            'Outdoor Shade': [], 'Context Shade': [], 'Indoor Shade': []
        }
        # add all faces to the dictionary
        for face in model.faces:
            for ap in face._apertures:
                type_dict['Aperture'].append(ap.geometry)
            for dr in face._doors:
                if dr.is_glass:
                    type_dict['Glass Door'].append(dr.geometry)
                else:
                    type_dict['Door'].append(dr.geometry)
            if isinstance(face.type, AirBoundary):
                type_dict['Air Boundary'].append(face.punched_geometry)
            elif isinstance(face.boundary_condition, (Outdoors, Ground)):
                if isinstance(face.type, Wall):
                    type_dict['Wall'].append(face.punched_geometry)
                elif isinstance(face.type, RoofCeiling):
                    type_dict['Roof'].append(face.punched_geometry)
                elif isinstance(face.type, Floor):
                    type_dict['Floor'].append(face.punched_geometry)
            else:
                if isinstance(face.type, Wall):
                    type_dict['Interior Wall'].append(face.punched_geometry)
                elif isinstance(face.type, RoofCeiling):
                    type_dict['Ceiling'].append(face.punched_geometry)
                elif isinstance(face.type, Floor):
                    type_dict['Interior Floor'].append(face.punched_geometry)
        # add orphaned apertures to the dictionary
        for ap in model._orphaned_apertures:
            type_dict['Aperture'].append(ap.geometry)
        # add all doors to the dictionary
        for dr in model._orphaned_doors:
            if dr.is_glass:
                type_dict['Glass Door'].append(dr.geometry)
            else:
                type_dict['Door'].append(dr.geometry)
        # add all shades to the dictionary
        for shd in model.outdoor_shades:
            if shd.is_detached:
                type_dict['Context Shade'].append(shd.geometry)
            else:
                type_dict['Outdoor Shade'].append(shd.geometry)
        for shd in model.indoor_shades:
            type_dict['Indoor Shade'].append(shd.geometry)
    elif color_by == 'boundary_condition':
        type_dict = {
            'Outdoors': [], 'Surface': [], 'Ground': [], 'Adiabatic': [], 'Other': []}
        # add all faces to the dictionary
        for face in model.faces:
            if isinstance(face.boundary_condition, Outdoors):
                type_dict['Outdoors'].append(face.punched_geometry)
                for ap in face._apertures:
                    type_dict['Outdoors'].append(ap.geometry)
                for dr in face._doors:
                    type_dict['Outdoors'].append(dr.geometry)
            elif isinstance(face.boundary_condition, Surface):
                type_dict['Surface'].append(face.punched_geometry)
                for ap in face._apertures:
                    type_dict['Surface'].append(ap.geometry)
                for dr in face._doors:
                    type_dict['Surface'].append(dr.geometry)
            elif isinstance(face.boundary_condition, Ground):
                type_dict['Ground'].append(face.geometry)
            elif face.boundary_condition.name == 'Adiabatic':
                type_dict['Adiabatic'].append(face.geometry)
            else:
                type_dict['Other'].append(face.geometry)
        # add orphaned apertures to the dictionary
        for ap in model._orphaned_apertures:
            if isinstance(ap.boundary_condition, Outdoors):
                type_dict['Outdoors'].append(ap.geometry)
            else:
                type_dict['Surface'].append(ap.geometry)
        # add all doors to the dictionary
        for dr in model._orphaned_doors:
            if isinstance(dr.boundary_condition, Outdoors):
                type_dict['Outdoors'].append(dr.geometry)
            else:
                type_dict['Surface'].append(dr.geometry)
        # add all shades to the dictionary
        for shd in model.shades:
            type_dict['Other'].append(shd.geometry)
    elif color_by == 'none':
        type_dict = {}
    else:  # unrecognized property for coloring
        msg = 'Unrecognized color_by input "{}" for model_to_vis_set.'.format(color_by)
        raise ValueError(msg)

    # loop through the dictionary and add a ContextGeometry for each group
    geo_objs = []
    for geo_id, geometries in type_dict.items():
        if len(geometries) != 0:
            col = TYPE_COLORS[geo_id] if color_by == 'type' else BC_COLORS[geo_id]
            if use_mesh:
                dis_geos = [DisplayMesh3D(f.triangulated_mesh3d, color=col)
                            for f in geometries]
            else:
                dis_geos = []
                for geo in geometries:
                    dis_geos.append(DisplayFace3D(geo, col))
            con_geo = ContextGeometry(geo_id.replace(' ', '_'), dis_geos)
            if hide_color_by:
                con_geo.hidden = True
            con_geo.display_name = geo_id
            geo_objs.append(con_geo)

    # add room attributes to the VisualizationSet if requested
    if room_attr is not None and len(room_attr) != 0 and len(model.rooms) != 0:
        room_attr = [room_attr] if isinstance(room_attr, str) else room_attr
        if room_text_labels:
            units, tol = model.units, model.tolerance
            for r_attr in room_attr:
                ra_col_obj = ColorRoom(model.rooms, r_attr, room_legend_par)
                geo_objs.append(
                    color_room_to_vis_set(ra_col_obj, False, True, units, tol)[0])
        else:
            ra_col_obj = ColorRoom(model.rooms, room_attr[0], room_legend_par)
            geo_obj = color_room_to_vis_set(ra_col_obj, False, False)[0]
            geo_obj.identifier = 'Room_Attributes'
            geo_obj.display_name = 'Room Attributes'
            for r_attr in room_attr[1:]:
                ra_col_obj = ColorRoom(model.rooms, r_attr, room_legend_par)
                ra_a_geo = color_room_to_vis_set(ra_col_obj, False, False)[0]
                geo_obj.add_data_set(ra_a_geo[0])
            geo_objs.append(geo_obj)

    # add face attributes to the VisualizationSet if requested
    if face_attr is not None and len(face_attr) != 0:
        face_attr = [face_attr] if isinstance(face_attr, str) else face_attr
        faces = []
        for room in model.rooms:
            faces.extend(room.faces)
            faces.extend(room.shades)
        faces.extend(model.orphaned_faces)
        faces.extend(model.orphaned_apertures)
        faces.extend(model.orphaned_doors)
        faces.extend(model.orphaned_shades)
        if len(faces) != 0 :
            if face_text_labels:
                units, tol = model.units, model.tolerance
                for f_attr in face_attr:
                    fa_col_obj = ColorFace(faces, f_attr, face_legend_par)
                    geo_objs.append(
                        color_face_to_vis_set(fa_col_obj, False, True, units, tol)[0])
            else:
                fa_col_obj = ColorFace(faces, face_attr[0], face_legend_par)
                geo_obj = color_face_to_vis_set(fa_col_obj, False, False)[0]
                geo_obj.identifier = 'Face_Attributes'
                geo_obj.display_name = 'Face Attributes'
                for r_attr in face_attr[1:]:
                    fa_col_obj = ColorFace(faces, r_attr, face_legend_par)
                    ra_a_geo = color_face_to_vis_set(fa_col_obj, False, False)[0]
                    geo_obj.add_data_set(ra_a_geo[0])
                geo_objs.append(geo_obj)

    # add the sensor grid geometry if requested
    gdm = grid_display_mode.lower()
    default_exclude = gdm == 'default' and grid_data_path is not None and \
        os.path.isdir(grid_data_path)
    if gdm != 'none' and not default_exclude:
        # get the sensor grids and evaluate whether they have meshes
        try:
            grid_objs = model.properties.radiance.sensor_grids
        except AttributeError:  # honeybee-radiance is not installed
            grid_objs = []
        if len(grid_objs) != 0:
            grid_meshes = [g.mesh for g in grid_objs]
            g_meshes_avail = all(m is not None for m in grid_meshes)
            # create the context geometry for the sensor grids
            dis_geos = []
            if gdm in ('default', 'points') or not g_meshes_avail:
                for grid in grid_objs:
                    for p in grid.positions:
                        dis_geos.append(DisplayPoint3D(Point3D(*p)))
            elif gdm == 'wireframe':
                for mesh in grid_meshes:
                    dis_geos.append(DisplayMesh3D(mesh, display_mode='Wireframe'))
            elif gdm in ('surface', 'surfacewithedges'):
                for mesh in grid_meshes:
                    grey = Color(100, 100, 100)
                    d_mesh = DisplayMesh3D(
                        mesh, color=grey, display_mode=grid_display_mode)
                    dis_geos.append(d_mesh)
            con_geo = ContextGeometry('Sensor_Grids', dis_geos)
            if hide_grid:
                con_geo.hidden = True
            con_geo.display_name = 'Sensor Grids'
            geo_objs.append(con_geo)

    # add grid data if requested
    if grid_data_path is not None and os.path.isdir(grid_data_path):
        # first try to get all of the Model sensor grids
        try:
            grids = {g.full_identifier: g for g in
                     model.properties.radiance.sensor_grids}
        except AttributeError:  # honeybee-radiance is not installed
            grids = {}
        if len(grids) != 0:
            # gather all of the directories with results
            gi_dirs, gi_file = [], 'grids_info.json'
            root_gi_file = os.path.join(grid_data_path, gi_file)
            if os.path.isfile(root_gi_file):
                gi_dirs.append(grid_data_path)
            for sub_f in os.listdir(grid_data_path):
                sub_dir = os.path.join(grid_data_path, sub_f)
                if os.path.isdir(sub_dir):
                    sub_gi_file = os.path.join(sub_dir, gi_file)
                    if os.path.isfile(sub_gi_file):
                        gi_dirs.append(sub_dir)
            # loop through the result directories and load the results
            data_sets = []
            for g_dir in gi_dirs:
                g_values = _read_sensor_grid_result(g_dir)
                meta_file = os.path.join(g_dir, 'vis_metadata.json')
                if os.path.isfile(meta_file):
                    with open(meta_file, 'r') as mf:
                        m_data = json.load(mf)
                    gm_data = VisualizationMetaData.from_dict(m_data)
                    v_data = VisualizationData(
                        g_values, gm_data.legend_parameters,
                        gm_data.data_type, gm_data.unit)
                    data_sets.append(v_data)
                else:
                    generic_type = GenericType(os.path.split(g_dir)[-1], '')
                    v_data = VisualizationData(g_values, data_type=generic_type)
                    data_sets.append(v_data)
            # create the analysis geometry
            if len(data_sets) != 0:
                ex_gi_file = os.path.join(gi_dirs[0], gi_file)
                with open(ex_gi_file) as json_file:
                    grid_list = json.load(json_file)
                grid_objs = [grids[g['full_id']] for g in grid_list]
                grid_meshes = [g.mesh for g in grid_objs]
                if all(m is not None for m in grid_meshes):
                    a_geo = AnalysisGeometry('Grid_Data', grid_meshes, data_sets)
                else:
                    gr_pts = [Point3D(*pos) for gr in grid_objs for pos in gr.positions]
                    a_geo = AnalysisGeometry('Grid_Data', gr_pts, data_sets)
                a_geo.display_name = 'Grid Data'
                a_geo.display_mode = grid_data_display_mode
                geo_objs.append(a_geo)

    # add the wireframe if requested
    if include_wireframe:
        wf_geo = model_to_vis_set_wireframe(model)
        if wf_geo is not None:
            geo_objs.append(wf_geo[0])

    # build the VisualizationSet and return it
    vis_set = VisualizationSet(model.identifier, geo_objs, model.units)
    vis_set.display_name = model.display_name
    return vis_set


def model_to_vis_set_wireframe(model):
    """Get a VisualizationSet with a single ContextGeometry for the model wireframe.

    Args:
        model: A Honeybee Model object to be translated to a wireframe.

    Returns:
        A VisualizationSet with a single ContextGeometry and a list of
        DisplayLineSegment3D for the wireframe of the Model.
    """
    def _process_wireframe(face3d, wireframe, line_width=1):
        """Process the boundary and holes into DisplayLinesegment3D."""
        for seg in face3d.boundary_segments:
            wireframe.append(DisplayLineSegment3D(seg, line_width=line_width))
        if face3d.has_holes:
            for hole in face3d.holes:
                for seg in face3d.boundary_segments:
                    wireframe.append(DisplayLineSegment3D(seg, line_width=line_width))

    # loop through all of the objects and add their wire frames
    wireframe = []
    for face in model.faces:
        _process_wireframe(face.geometry, wireframe, 2)
        for ap in face._apertures:
            _process_wireframe(ap.geometry, wireframe)
        for dr in face._doors:
            _process_wireframe(dr.geometry, wireframe)
    for ap in model._orphaned_apertures:
        _process_wireframe(ap.geometry, wireframe)
    for dr in model._orphaned_doors:
        _process_wireframe(dr.geometry, wireframe)
    for shd in model.indoor_shades:
        _process_wireframe(shd.geometry, wireframe)
    for shd in model.outdoor_shades:
        lw = 2 if shd.is_detached else 1
        _process_wireframe(shd.geometry, wireframe, lw)

    # build the VisualizationSet and return it
    if len(wireframe) == 0:
        return None
    vis_set = VisualizationSet(
        model.identifier, [ContextGeometry('Wireframe', wireframe)])
    vis_set.display_name = model.display_name
    return vis_set


def _read_sensor_grid_result(result_folder):
    """Read results from files that align with sensor grids.

    Args:
        result_folder: Path to the folder containing the results.

    Returns:
        A matrix with each sub-list containing the values for each of the sensor grids.
    """
    # check that the required files are present
    if not os.path.isdir(result_folder):
        raise ValueError('Invalid result folder: %s' % result_folder)
    grid_json = os.path.join(result_folder, 'grids_info.json')
    if not os.path.isfile(grid_json):
        raise ValueError('Result folder contains no grids_info.json.')

    # load the list of grids and gather all of the results
    with open(grid_json) as json_file:
        grid_list = json.load(json_file)
    results = []
    for grid in grid_list:
        grid_id = grid['full_id']
        sensor_count = grid['count']
        try:
            st_ln = grid['start_ln']
        except KeyError:
            # older version of sensor info
            st_ln = 0

        # find the result file and append the results
        result_file = None
        for f in os.listdir(result_folder):
            if f.startswith(grid_id):
                result_file = os.path.join(result_folder, f)
                break
        if result_file is not None:
            with open(result_file) as inf:
                for _ in range(st_ln):
                    next(inf)
                for _ in range(sensor_count):
                    results.append(float(next(inf)))
    return results
