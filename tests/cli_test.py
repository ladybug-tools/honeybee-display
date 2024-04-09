"""Test cli."""
import os
import time
from click.testing import CliRunner

from honeybee_display.cli import model_to_vis_set


def test_model_to_vis_set_shade_mesh():
    input_model = './tests/json/model_with_shade_mesh.hbjson'
    output_vis = './tests/json/model_with_shade_mesh.html'
    runner = CliRunner()
    t0 = time.time()
    cmd_args = [input_model, '--output-format', 'html', '--output-file', output_vis]
    result = runner.invoke(model_to_vis_set, cmd_args)
    run_time = time.time() - t0
    assert result.exit_code == 0
    assert run_time < 10
    assert os.path.isfile(output_vis)
    os.remove(output_vis)
