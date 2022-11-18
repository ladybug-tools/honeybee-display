"""honeybee-display commands."""
import click
import sys
import logging
import json

from honeybee.model import Model
from honeybee.cli import main

_logger = logging.getLogger(__name__)


# command group for all display extension commands.
@click.group(help='honeybee display commands.')
@click.version_option()
def display():
    pass


@display.command('model')
@click.argument('model-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option(
    '--color-by', '-c', help=' Text for the property that dictates the colors of '
    'the Model geometry. If none, only a wireframe of the Model will be generated, '
    'assuming include_wireframe is True. This is useful when the primary purpose of '
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
    '(meaning that their wireframe in certain platforms might not appear ideal) '
    'and they cannot support the selection of individual Face3D geometries '
    'in the resulting visualization.', default=True, show_default=True)
@click.option(
    '--room-attr', '-r', help='An optional text string of an attribute that the Model '
    'Rooms have, which will be used to construct a visualization of this attribute '
    'in the resulting VisualizationSet. This can also be a list of attribute strings '
    'and a separate VisualizationData will be added to the AnalysisGeometry that '
    'represents the attribute in the resulting VisualizationSet (or a separate '
    'ContextGeometry layer if room_text_labels is True). Room attributes '
    'input here can have . that separates the nested attributes from '
    'one another. For example, properties.energy.program_type.',
    type=click.STRING, multiple=True, default=None, show_default=True)
@click.option(
    '--face-attr', '-f', help='An optional text string of an attribute that the Model '
    'Faces have, which will be used to construct a visualization of this attribute in '
    'the resulting VisualizationSet. This can also be a list of attribute strings and '
    'a separate VisualizationData will be added to the AnalysisGeometry that '
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
    '--output-format', '-of', help=' Text for the output format of the resulting '
    'VisualizationSet File (.vsf). Choose from', type=str, default='json',
    show_default=True)
@click.option(
    '--output-file', help='Optional file to output the JSON string of '
    'the config object. By default, it will be printed out to stdout',
    type=click.File('w'), default='-', show_default=True)
def config(model_file, color_by, wireframe, mesh, room_attr, face_attr, 
           color_attr, grid_data, output_file):
    """Get a JSON object with all configuration information"""
    try:
        model_obj = Model.from_file(model_file)
        room_attr = None if len(room_attr) == 0 else room_attr
        face_attr = None if len(face_attr) == 0 else face_attr
        text_labels = not color_attr
        vis_set = model_obj.to_vis_set(
            color_by=color_by, include_wireframe=wireframe, use_mesh=mesh,
            room_attr=room_attr, face_attr=face_attr,
            room_text_labels=text_labels, face_text_labels=text_labels,
            grid_data=grid_data)
        output_file.write(json.dumps(vis_set.to_dict()))
    except Exception as e:
        _logger.exception('Failed to translate Model to VisualizationSet.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


# add display sub-group to honeybee CLI
main.add_command(display)
