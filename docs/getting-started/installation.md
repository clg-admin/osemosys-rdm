# Installation

This guide covers the installation of OSeMOSYS-RDM and its dependencies.

## Prerequisites

Before installing OSeMOSYS-RDM, ensure you have the following:

### Required Software

- **Python 3.10+**: Required for all execution modes
- **Conda/Miniconda/Anaconda**: Required for DVC automation (optional for manual execution)
- **At least one solver** installed and available in PATH:
  - [GLPK](https://www.gnu.org/software/glpk/) (free, **required** for preprocessing)
  - [CBC](https://github.com/coin-or/Cbc) (free)
  - [CPLEX](https://www.ibm.com/products/ilog-cplex-optimization-studio) (commercial)
  - [Gurobi](https://www.gurobi.com/) (commercial)

### Optional Software

- **Git**: Recommended but not required. The pipeline can run without Git installed.
- **DVC remote storage**: Required if you want to share large artifacts across machines.

## Installation Methods

### Option 1: Automated Setup (Recommended)

The simplest way to get started is to clone the repository and run the automated setup:

```bash
# Clone the repository
git clone https://github.com/clg-admin/osemosys-rdm.git
cd osemosys-rdm

# Run the pipeline (this will automatically set up the environment)
python run.py exp
```

The automated setup will:

1. Create a Conda environment named `OSeMOSYS-RDM-env`
2. Install all required dependencies (pandas, numpy, DVC, etc.)
3. Install the **GLPK and CBC solvers automatically** (both are declared in `environment.yaml` as the conda-forge packages `glpk` and `coincbc`)
4. Initialize DVC if needed
5. Execute the complete pipeline

```{note}
Because GLPK and CBC are part of `environment.yaml`, the automated setup (and any
`conda env create -f environment.yaml`) installs both solvers for you. You only need
to install solvers manually if you set up the environment **without** conda — for
example with `pip install -r requirements.txt` — or if you want a commercial solver
(CPLEX/Gurobi). See [Solver Installation](#solver-installation) below.
```

### Option 2: Manual Setup

For more control over the installation process:

```bash
# Clone the repository
git clone https://github.com/clg-admin/osemosys-rdm.git
cd osemosys-rdm

# Create and activate the conda environment
conda env create -f environment.yaml
conda activate OSeMOSYS-RDM-env

# Alternatively, install with pip
pip install -r requirements.txt
```

```{important}
The two installation paths differ in how solvers are handled:

- **conda** (`conda env create -f environment.yaml`): GLPK and CBC are installed
  automatically, since they are listed in `environment.yaml`.
- **pip** (`pip install -r requirements.txt`): GLPK and CBC are **not** installed —
  they are not pip packages. You must install them manually (see
  [Solver Installation](#solver-installation)).
```

## Solver Installation

```{note}
If you set up the environment with conda (the automated setup or
`conda env create -f environment.yaml`), **GLPK and CBC are already installed** and you
can skip this section. The steps below are only needed for non-conda installs (e.g. pip)
or for commercial solvers (CPLEX/Gurobi).
```

```{important}
This workflow is designed and tested for **Windows only**. Linux and macOS support has not been verified and is not recommended at this time.
```

### GLPK (Required)

GLPK is required for preprocessing.

**Windows:**
Download from [GLPK for Windows](https://sourceforge.net/projects/winglpk/) and add to PATH.

**Conda (Recommended):**
```bash
conda install -c conda-forge glpk
```

### CBC (Free, Optional)

CBC often provides better performance than GLPK for larger problems.

**Windows:**
Free versions of CBC for Windows can be downloaded from:
- [COIN-OR CBC Downloads](https://www.coin-or.org/download/binary/Cbc/)
- Recommended version: **Cbc-master-win64-msvc17** (2021-04-27, ~23MB)

After downloading, extract and add the executable to your system PATH.

**Conda (Alternative):**
```bash
conda install -c conda-forge coincbc
```

### Commercial Solvers

For CPLEX or Gurobi:

1. Obtain a license (academic licenses are often available for free)
2. Install following the vendor's instructions
3. Ensure the solver executable is in your system PATH

## Verifying Installation

After installation, verify everything is working:

```bash
# Check Python version
python --version

# Check solver availability
glpsol --version

# Check DVC installation
dvc --version

# Run a quick test
python run.py exp --help
```

## Troubleshooting

### Common Issues

**Solver not found**

If you get a "solver not found" error:

1. Verify the solver is installed: `glpsol --version` or `cbc -version`
2. Check that the solver is in your PATH
3. For commercial solvers, verify the license is valid

**Environment issues**

If you encounter environment problems:

```bash
# Remove and recreate the environment
conda env remove -n OSeMOSYS-RDM-env
conda env create -f environment.yaml
```

**Import errors**

If you get import errors for Python packages:

```bash
# Reinstall dependencies
conda activate OSeMOSYS-RDM-env
pip install -r requirements.txt
```

## Next Steps

Once installation is complete:

1. Read the [Quickstart Guide](quickstart.md) to run your first analysis
2. Learn about [Configuration](configuration.md) options
3. Explore the [Workflow Overview](../user-guide/workflow-overview.md)
