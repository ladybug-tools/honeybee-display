"""Test cli."""
import os
import time
from click.testing import CliRunner

from ladybug.commandutil import run_command_function
from honeybee_display.cli import model_to_vis_set_cli, model_to_vis_set


def test_model_to_vis_set_shade_mesh():
    input_model = './tests/json/model_with_shade_mesh.hbjson'
    output_vis = './tests/json/model_with_shade_mesh.html'
    runner = CliRunner()
    t0 = time.time()
    cmd_args = [input_model, '--output-format', 'html', '--output-file', output_vis]
    result = runner.invoke(model_to_vis_set_cli, cmd_args)
    run_time = time.time() - t0
    assert result.exit_code == 0
    assert run_time < 10
    assert os.path.isfile(output_vis)
    os.remove(output_vis)


def test_model_to_vis_set():
    """Test the model_to_vis_set function that runs within the CLI."""
    input_model = './tests/json/single_family_home.hbjson'
    cmd_args = [input_model]
    cmd_options = {'--output-format': 'vtkjs'}
    vtkjs_str = run_command_function(model_to_vis_set, cmd_args, cmd_options)

    assert isinstance(vtkjs_str, str)
    assert len(vtkjs_str) > 1000

    cmd_options = {
        '--color-by': 'type',
        '--output-format': 'html',
        '--room-attr': 'display_name',
        '--text-attr': ''
    }
    output_vis = './tests/json/single_family_home.html'
    cmd_options['--output-file'] = output_vis
    run_command_function(model_to_vis_set, cmd_args, cmd_options)
    assert os.path.isfile(output_vis)
    os.remove(output_vis)
