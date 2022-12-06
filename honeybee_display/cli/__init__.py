"""honeybee-display commands."""
import click
import sys
import os
import logging
import json
import pickle

from honeybee.model import Model
from honeybee.cli import main

_logger = logging.getLogger(__name__)


# command group for all display extension commands.
@click.group(help='honeybee display commands.')
@click.version_option()
def display():
    pass


@display.command('model-to-vis')
@click.argument('model-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option(
    '--color-by', '-c', help='Text for the property that dictates the colors of '
    'the Model geometry. Choose from: type, boundary_condition, none. '
    'If none, only a wireframe of the Model will be generated, assuming the '
    '--exclude-wireframe option is not uses. None is useful when the primary purpose of '
    'the visualization is to display results in relation to the Model '
    'geometry or display some room_attr or face_attr as an AnalysisGeometry '
    'or Text labels.', type=str, default='type', show_default=True)
@click.option(
    '--wireframe/--exclude-wireframe', ' /-xw', help='Flag to note whether a '
    'ContextGeometry dedicated to the Model Wireframe (in DisplayLineSegment3D) should '
    'be included in the output VisualizationSet.', default=True, show_default=True)
@click.option(
    '--mesh/--faces', help='Flag to note whether the colored model geometries should '
    'be represented with joined DisplayMesh3D objects instead of '
    'a list of DisplayFace3D objects. Meshes can usually be rendered '
    'faster and they scale well for large models but all geometry is triangulated '
    '(meaning that their wireframe in certain platforms might not appear ideal). '
    'Also, merging the geometry into a single mesh means interfaces cannot support '
    'the selection of individual Face3D geometries.', default=True, show_default=True)
@click.option(
    '--show-color-by/--hide-color-by', ' /-hcb', help='Flag to note whether the '
    'color-by geometry should be hidden or shown by default. Hiding the color-by '
    'geometry is useful when the primary purpose of the visualization is to display '
    'grid-data or room/face attributes but it is still desirable to have the option '
    'to turn on the geometry.', default=True, show_default=True)
@click.option(
    '--room-attr', '-r', help='An optional text string of an attribute that the Model '
    'Rooms have, which will be used to construct a visualization of this attribute '
    'in the resulting VisualizationSet. Multiple instances of this option can be passed '
    'and a separate VisualizationData will be added to the AnalysisGeometry that '
    'represents the attribute in the resulting VisualizationSet (or a separate '
    'ContextGeometry layer if room_text_labels is True). Room attributes '
    'input here can have . that separates the nested attributes from '
    'one another. For example, properties.energy.program_type.',
    type=click.STRING, multiple=True, default=None, show_default=True)
@click.option(
    '--face-attr', '-f', help='An optional text string of an attribute that the Model '
    'Faces have, which will be used to construct a visualization of this attribute in '
    'the resulting VisualizationSet. Multiple instances of this option can be passed and'
    ' a separate VisualizationData will be added to the AnalysisGeometry that '
    'represents the attribute in the resulting VisualizationSet (or a separate '
    'ContextGeometry layer if face_text_labels is True). Face attributes '
    'input here can have . that separates the nested attributes from '
    'one another. For example, properties.energy.construction.',
    type=click.STRING, multiple=True, default=None, show_default=True)
@click.option(
    '--color-attr/--text-attr', help='Flag to note whether to note whether the '
    'input room-attr and face-attr should be expressed as a colored AnalysisGeometry '
    'or a ContextGeometry as text labels.', default=True, show_default=True)
@click.option(
    '--grid-display-mode', '-m', help='Text that dictates how the ContextGeometry '
    'for Model SensorGrids should display in the resulting visualization. The Default '
    'option will draw sensor points whenever there is no grid_data_path and will not '
    'draw them at all when grid data is provided, assuming the AnalysisGeometry of '
    'the grids is sufficient. Choose from: Default, Points, Wireframe, Surface, '
    'SurfaceWithEdges, None.',
    type=str, default='Default', show_default=True)
@click.option(
    '--hide-grid/--show-grid', ' /-sg', help='Flag to note whether the SensorGrid '
    'ContextGeometry should be hidden or shown by default.',
    default=True, show_default=True)
@click.option(
    '--grid-data', '-g', help='An optional path to a folder containing data that '
    'aligns with the SensorGrids in the model. Any sub folder within this path '
    'that contains a grids_into.json (and associated CSV files) will be '
    'converted to an AnalysisGeometry in the resulting VisualizationSet. '
    'If a vis_metadata.json file is found within this sub-folder, the '
    'information contained within it will be used to customize the '
    'AnalysisGeometry. Note that it is acceptable if data and '
    'grids_info.json exist in the root of this grid_data_path. Also '
    'note that this argument has no impact if honeybee-radiance is not '
    'installed and SensorGrids cannot be decoded.',
    default=None, show_default=True,
    type=click.Path(file_okay=False, dir_okay=True, resolve_path=True))
@click.option(
    '--grid-data-display-mode', '-dm', help='Text to set the display_mode of the '
    'AnalysisGeometry that is generated from the grid_data_path above. Note '
    'that this has no effect if there are no meshes associated with the model '
    'SensorGrids. Choose from: Surface, SurfaceWithEdges, Wireframe, Points',
    type=str, default='Surface', show_default=True)
@click.option(
    '--output-format', '-of', help='Text for the output format of the resulting '
    'VisualizationSet File (.vsf). Choose from: vsf, pkl, vtkjs. Note that vsf .'
    'refers to the JSON version of the VisualizationSet file. Also not that '
    'ladybug-vtk must be installed in order for the vtkjs option to be usable. '
    'The vtkjs option also requires an explicit --output-file to be specified.',
    type=str, default='vsf', show_default=True)
@click.option(
    '--output-file', help='Optional file to output the JSON string of '
    'the config object. By default, it will be printed out to stdout',
    type=click.File('w'), default='-', show_default=True)
def model_to_vis_set(
        model_file, color_by, wireframe, mesh, show_color_by,
        room_attr, face_attr, color_attr, grid_display_mode, hide_grid,
        grid_data, grid_data_display_mode, output_format, output_file):
    """Get a JSON object with all configuration information"""
    try:
        model_obj = Model.from_file(model_file)
        room_attr = None if len(room_attr) == 0 or room_attr[0] == '' else room_attr
        face_attr = None if len(face_attr) == 0 or face_attr[0] == '' else face_attr
        text_labels = not color_attr
        hide_color_by = not show_color_by
        vis_set = model_obj.to_vis_set(
            color_by=color_by, include_wireframe=wireframe, use_mesh=mesh,
            hide_color_by=hide_color_by, room_attr=room_attr, face_attr=face_attr,
            room_text_labels=text_labels, face_text_labels=text_labels,
            grid_display_mode=grid_display_mode, hide_grid=hide_grid,
            grid_data_path=grid_data, grid_data_display_mode=grid_data_display_mode)
        output_format = output_format.lower()
        if output_format in ('vsf', 'json'):
            output_file.write(json.dumps(vis_set.to_dict()))
        elif output_format == 'pkl':
            if output_file.name != '<stdout>':
                out_folder, out_file = os.path.split(output_file.name)
                vis_set.to_pkl(out_file, out_folder)
            else:
                output_file.write(pickle.dumps(vis_set.to_dict()))
        elif output_format == 'vtkjs':
            assert output_file.name != '<stdout>', \
                'Must specify an --output-file to use --output-format vtkjs.'
            out_folder, out_file = os.path.split(output_file.name)
            try:
                if out_file.endswith('.vtkjs'):
                    out_file = out_file[:-6]
                vis_set.to_vtkjs(output_folder=out_folder, file_name=out_file)
            except AttributeError as ae:
                raise AttributeError(
                    'Ladybug-vtk must be installed in order to use --output-format '
                    'vtkjs.\n{}'.format(ae))
        else:
            raise ValueError('Unrecognized output-format "{}".'.format(output_format))
    except Exception as e:
        _logger.exception('Failed to translate Model to VisualizationSet.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


# add display sub-group to honeybee CLI
main.add_command(display)
