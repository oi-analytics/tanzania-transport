# Tanzania World Bank project

To contain project-specific scripts and workflows, with the intention of
relying on other packages or projects for core functionality.

Extract the contents of `Assembled_Tanzania_data.7z` to a directory named
`./data` adjacent to this README. (On Windows, right click > 7-Zip > Extract
Here, then rename to `data`.)

Run `make all` to generate outputs. Or without make (or if Makefile is
incomplete), run each script in `./scripts`, e.g.
`python scripts/calculate_rail_length.py`

## Python requirements

Recommended option is to use a [miniconda](https://conda.io/miniconda.html)
environment to work in for this project, relying on conda to handle some of the
trickier library dependencies.

```bash
# Create a conda environment for the project
conda create --name tanzania python=3.6
activate tanzania

# Install cartopy and packaged dependencies
conda install -c conda-forge cartopy
# Install gdal and library dependencies
conda install gdal
# Install remaining packages
pip install -r requirements.txt
```
