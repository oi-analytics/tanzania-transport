# Tanzania World Bank project

To contain project-specific scripts and workflows, with the intention of
relying on other packages or projects for core functionality.

Download the `Infrastructure` and `tanzania_flood` folders from OneDrive to a
directory named `./data` adjacent to this README.

Run each script in `./scripts`, e.g. `python scripts/calculate_rail_length.py`

The intention is that `make all` will generate all outputs, but this is
currently incomplete.

## Python requirements

Recommended option is to use a [miniconda](https://conda.io/miniconda.html)
environment to work in for this project, relying on conda to handle some of the
trickier library dependencies.

```bash
# Create a conda environment for the project
conda create --name tanzania python=3.6
activate tanzania

# Add conda-forge channel for extra packages
conda config --add channels conda-forge

# Install packages
conda install --file requirements.txt
pip install pyshp  # Required for cartopy but not otherwise automatically loaded
```

## Other requirements

`osmium-tool` is handy for handling `.osm.pbf` files. The
[docs](http://osmcode.org/osmium-tool/manual.html) have installation/build
instructions.
