# Installation

This guide covers the installation of OSeMOSYS-RDM and its dependencies.

## Prerequisites

Before installing OSeMOSYS-RDM, ensure you have the following:

### Required Software

- **Python 3.10+**: Required for all execution modes
- **Conda (Miniconda or Anaconda)**: **Required.** The runner `run.py` is built around Conda — it creates the environment, installs every dependency, and executes all pipeline commands through `conda run`. The script aborts immediately if `conda` is not available on the PATH. See [Step 0: Install Conda](#step-0-install-conda-miniconda-or-anaconda) below.
- **At least one solver** installed and available in PATH:
  - [GLPK](https://www.gnu.org/software/glpk/) (free, **required** for preprocessing)
  - [CBC](https://github.com/coin-or/Cbc) (free)
  - [CPLEX](https://www.ibm.com/products/ilog-cplex-optimization-studio) (commercial)
  - [Gurobi](https://www.gurobi.com/) (commercial)

### Optional Software

- **Git**: Recommended but not required. The pipeline can run without Git installed.
- **DVC remote storage**: Required if you want to share large artifacts across machines.

## Step 0: Install Conda (Miniconda or Anaconda)

Because `run.py` orchestrates everything through Conda, you must have a Conda
distribution installed **before** doing anything else. If you don't already
have one, **Miniconda** is the recommended lightweight option; **Anaconda** also
works if you prefer the full distribution.

### Install Miniconda (recommended)

1. Download the installer for your platform. The
   [Miniconda documentation](https://www.anaconda.com/docs/getting-started/miniconda/main)
   describes the options, or grab the installer directly (no registration) from
   the [Miniconda installer archive](https://repo.anaconda.com/miniconda/).
   - **Windows:** choose the latest 64-bit `Miniconda3-latest-Windows-x86_64.exe`.
2. Run the installer and accept the defaults. On Windows you do **not** need to
   add Conda to the system PATH — use the dedicated prompt described below.

> Prefer the full distribution? Install
> [Anaconda](https://www.anaconda.com/download) instead. Everything below works
> the same way.

### Open the Anaconda / Miniconda Prompt (Windows)

On Windows, the `conda` command is only on the PATH inside the dedicated prompt
that the installer creates. **Always run `run.py` from that prompt**, otherwise
the script will stop with:

```text
Required tool 'conda' not found in PATH. Please open an Anaconda/Miniconda Prompt or install the tool.
```

To open it:

1. Press the Windows key and type **"Anaconda Prompt"** (or **"Miniconda
   Prompt"**).
2. Launch it — the title bar shows `(base)`, indicating Conda is active.
3. Use this prompt for every command in this guide (`conda ...`,
   `python run.py ...`).

On macOS/Linux, Conda is initialized in your normal shell after running
`conda init`; restart the terminal and confirm with `conda --version`.

### Verify Conda is available

```bash
conda --version
```

You should see something like `conda 24.x.x`. Once this works, continue with the
installation methods below.

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
3. Initialize DVC if needed
4. Execute the complete pipeline

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

## Solver Installation

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
