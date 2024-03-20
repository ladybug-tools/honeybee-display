[![Build Status](https://github.com/ladybug-tools/honeybee-display/workflows/CI/badge.svg)](https://github.com/ladybug-tools/honeybee-display/actions)

[![Python 3.10](https://img.shields.io/badge/python-3.10-orange.svg)](https://www.python.org/downloads/release/python-3100/) [![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/) [![Python 2.7](https://img.shields.io/badge/python-2.7-green.svg)](https://www.python.org/downloads/release/python-270/) [![IronPython](https://img.shields.io/badge/ironpython-2.7-red.svg)](https://github.com/IronLanguages/ironpython2/releases/tag/ipy-2.7.8/)

# honeybee-display

Adds methods and a CLI to translate honeybee objects to VisualizationSets.

## Installation

```console
pip install -U honeybee-display
```

If you want to also include all dependencies needed to produce VTK visualizations
from honeybee Models use.

```console
pip install -U honeybee-display[full]
```

To check if the command line interface is installed correctly use `honeybee-display --help`

## QuickStart

```python
import honeybee_display

```

## [API Documentation](http://ladybug-tools.github.io/honeybee-display/docs)

## Local Development

1. Clone this repo locally
```console
git clone git@github.com:ladybug-tools/honeybee-display

# or

git clone https://github.com/ladybug-tools/honeybee-display
```
2. Install dependencies:
```console
cd honeybee-display
pip install -r dev-requirements.txt
pip install -r requirements.txt
```

3. Run Tests:
```console
python -m pytest tests/
```

4. Generate Documentation:
```console
sphinx-apidoc -f -e -d 4 -o ./docs ./honeybee_display
sphinx-build -b html ./docs ./docs/_build/docs
```
