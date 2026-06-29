# DVC Integration for OSeMOSYS-RDM

This document explains how to use the DVC (Data Version Control) pipeline automation for the OSeMOSYS-RDM project.

## Overview

The DVC integration provides:
- **Automated environment setup**: Creates and manages Conda environment
- **Dependency management**: Automatically installs all required packages
- **Pipeline automation**: Executes the complete OSeMOSYS-RDM workflow
- **Reproducibility**: Ensures consistent results across different machines
- **Data versioning**: Tracks large data files without storing them in Git

## Quick Start

### Prerequisites

- **Conda/Miniconda/Anaconda**: Required for DVC automation (optional for manual execution)
- **Python 3.10+**: Required for all execution modes
- **Solvers**: At least one solver (GLPK, CBC, CPLEX, or Gurobi) installed and in PATH

### First Time Setup (DVC Automation)

1. Open a terminal (Anaconda Prompt on Windows)
2. Navigate to the OSeMOSYS-RDM directory
3. Run the pipeline:

```bash
python run.py
```

This will automatically:
- Create a Conda environment named `OSeMOSYS-RDM-env`
- Install all dependencies (pandas, numpy, DVC, etc.)
- Initialize DVC if needed
- Execute the complete pipeline

### Manual Execution (Without DVC)

You can also execute each stage manually without DVC automation:

**Option 1: Run complete workflow (original method)**
```bash
cd src
python RUN_RDM.py
```

**Option 2: Run individual stages**
```bash
# Execute base future only
python scripts/run_base_future.py

# Execute RDM experiment only
python scripts/run_rdm_experiment.py

# Execute postprocessing
python scripts/run_postprocess.py

# Execute PRIM analysis (two stages)
python scripts/run_prim_files_creator.py
python scripts/run_prim_analysis.py
```

**Note**: Manual execution requires:
- Dependencies installed: `pip install -r requirements.txt`
- Proper configuration in `Interface_RDM.xlsx`

### Running the Pipeline

**Execute full pipeline:**
```bash
python run.py
```

**Force re-execution of all stages:**
```bash
python run.py --force
```

**Skip pulling from remote storage:**
```bash
python run.py --skip-pull
```

**Use custom environment name:**
```bash
python run.py --env-name MyCustomEnv
```

## Pipeline Stages

The `dvc.yaml` file defines the following stages:

### 1. Preprocess
- **Input**: `Interface_RDM.xlsx`, scenario files
- **Output**: Model structure file
- **Description**: Extracts model structure and prepares data

### 2. Base Future
- **Input**: Model structure, scenarios
- **Output**: Base future results (Future 0)
- **Description**: Executes baseline scenario

### 3. RDM Experiment
- **Input**: Model structure, uncertainty table
- **Output**: Multiple future scenarios
- **Description**: Runs RDM with uncertainty analysis

### 4. Postprocess
- **Input**: Experimental platform results
- **Output**: Aggregated CSV files in `Results/`
- **Description**: Consolidates results from all futures

### 5. PRIM Analysis
- **Input**: Aggregated results
- **Output**: PRIM analysis outputs
- **Description**: Performs scenario discovery with PRIM

## DVC Commands

### Check pipeline status
```bash
conda run -n OSeMOSYS-RDM-env dvc status
```

### View pipeline DAG
```bash
conda run -n OSeMOSYS-RDM-env dvc dag
```

### Execute specific stage
```bash
conda run -n OSeMOSYS-RDM-env dvc repro base_future
```

### Pull data from remote
```bash
conda run -n OSeMOSYS-RDM-env dvc pull
```

### Push data to remote
```bash
conda run -n OSeMOSYS-RDM-env dvc push
```

## Configuring Remote Storage

To share data with your team, configure a DVC remote:

### Local Directory
```bash
conda run -n OSeMOSYS-RDM-env dvc remote add -d myremote /path/to/storage
```

### Google Drive
```bash
conda run -n OSeMOSYS-RDM-env dvc remote add -d gdrive gdrive://folder_id
conda run -n OSeMOSYS-RDM-env dvc remote modify gdrive gdrive_acknowledge_abuse true
```

### Amazon S3
```bash
conda run -n OSeMOSYS-RDM-env dvc remote add -d s3remote s3://mybucket/path
```

### Azure Blob Storage
```bash
conda run -n OSeMOSYS-RDM-env dvc remote add -d azure azure://container/path
```

## Parameters Tracking

DVC tracks parameters from `Interface_RDM.xlsx`:

- **Setup sheet**: Solver, Run_Base_Future, Run_RDM, Region, etc.
- **Uncertainty_Table**: All uncertainty parameters for RDM

Changes to these parameters will trigger re-execution of dependent stages.

## Metrics

The pipeline generates metrics files (as tracked in `dvc.yaml`):
- `src/workflow/1_Experiment/base_future_metrics.json`: Base future metrics
- `src/workflow/1_Experiment/rdm_experiment_metrics.json`: RDM experiment metrics
- `src/workflow/3_Postprocessing/postprocess_metrics.json`: Postprocessing metrics
- `src/workflow/4_PRIM/prim_files_creator_metrics.json`: PRIM files-creator metrics
- `src/workflow/4_PRIM/prim_analysis_metrics.json`: PRIM analysis metrics

View metrics:
```bash
conda run -n OSeMOSYS-RDM-env dvc metrics show
```

## Troubleshooting

### Environment issues
If you encounter environment problems, recreate it:
```bash
conda env remove -n OSeMOSYS-RDM-env
python run.py
```

### DVC not initialized
If DVC is not initialized:
```bash
conda run -n OSeMOSYS-RDM-env dvc init
```

### Missing dependencies
The `run.py` script automatically checks and installs missing dependencies.
If manual installation is needed:
```bash
conda activate OSeMOSYS-RDM-env
pip install -r requirements.txt
```

### Solver not found
Ensure your solver (GLPK/CBC/CPLEX/Gurobi) is:
1. Installed on your system
2. Available in your PATH
3. Properly licensed (for commercial solvers)

## Files Structure

```
osemosys-rdm/
├── run.py                  # Main runner script
├── dvc.yaml               # Pipeline definition
├── environment.yaml       # Conda environment specification
├── requirements.txt       # Python dependencies (pip)
├── .dvcignore            # Files to ignore in DVC
├── .dvc/                 # DVC internal files (auto-generated)
├── scripts/              # DVC wrapper scripts (pipeline stages)
├── tests/                # Unit tests
├── Results/              # Aggregated outputs (CSV/Parquet)
├── PRIM_Input/           # Isolated experiment platform consumed by PRIM
└── src/
    ├── Interface_RDM.xlsx  # Main configuration file
    ├── RUN_RDM.py        # Legacy execution script
    └── workflow/         # Pipeline scripts (incl. 5_OSeMOSYS_models/)
```

## Best Practices

1. **Commit dvc.yaml and .dvc files**: These track your pipeline and data versions
2. **Use remotes for large files**: Don't store GB-sized files in Git
3. **Document parameter changes**: Use descriptive commit messages
4. **Review dvc.lock**: This file ensures reproducibility
5. **Regular pushes**: Push to remote after successful runs

## Integration with Git

DVC works alongside Git:
- **Git tracks**: Code, pipeline definitions (.yaml), small config files
- **DVC tracks**: Large data files, model outputs, results

Typical workflow:
```bash
# 1. Make changes to code or configuration
# 2. Run pipeline
python run.py

# 3. Review changes
dvc status
git status

# 4. Commit to Git
git add dvc.yaml dvc.lock src/
git commit -m "Update RDM analysis parameters"

# 5. Push data to DVC remote
dvc push

# 6. Push code to Git
git push
```

## Manual Execution Guide

### When to Use Manual Execution

Manual execution is useful when you need to:
- **Debug individual stages**: Run and test specific parts of the pipeline
- **Develop new features**: Work on modifications without full pipeline overhead
- **No DVC/Conda available**: Execute on systems without these tools
- **Custom workflows**: Run stages in non-standard order or configuration

### Wrapper Scripts

The `scripts/` directory contains wrapper scripts that can be executed independently:

#### 1. Base Future (`scripts/run_base_future.py`)
Executes only the base future (Future 0) scenario.

```bash
python scripts/run_base_future.py
```

**What it does:**
- Temporarily sets `Run_Base_Future=Yes` and `Run_RDM=No` in Interface_RDM.xlsx
- Calls `src/RUN_RDM.py` to execute base scenario
- Generates metrics in `src/workflow/1_Experiment/Executables/metrics.json`
- Restores original configuration automatically

**Output:**
- Base future results in `src/workflow/1_Experiment/Executables/Scenario*_0/`
- CSV files with model outputs

#### 2. RDM Experiment (`scripts/run_rdm_experiment.py`)
Executes the RDM experiment with uncertainty analysis.

```bash
python scripts/run_rdm_experiment.py
```

**What it does:**
- Temporarily sets `Run_Base_Future=No` and `Run_RDM=Yes`
- Generates multiple futures using Latin Hypercube Sampling
- Calls `src/RUN_RDM.py` for RDM execution
- Generates metrics in `src/workflow/1_Experiment/Experimental_Platform/rdm_metrics.json`
- Restores original configuration

**Output:**
- Multiple futures in `src/workflow/1_Experiment/Experimental_Platform/Futures/`
- Parquet files for each future scenario

#### 3. Postprocessing (`scripts/run_postprocess.py`)
Aggregates results from all RDM futures.

```bash
python scripts/run_postprocess.py
```

**What it does:**
- Executes `src/workflow/3_Postprocessing/create_csv_concatenate.py`
- Concatenates results from all futures
- Generates aggregated CSV files
- Creates metrics in `Results/postprocess_metrics.json`

**Output:**
- Aggregated CSV files in `Results/`

#### 4. PRIM Files Creator (`scripts/run_prim_files_creator.py`)
Builds PRIM-ready input files from the experiment platform.

```bash
python scripts/run_prim_files_creator.py
```

**What it does:**
- Reads the isolated experiment platform from `PRIM_Input/` (not `Results/`)
- Executes `src/workflow/4_PRIM/t3f2_prim_files_creator.py`
- Creates PRIM input files for scenario discovery
- Creates metrics in `src/workflow/4_PRIM/prim_files_creator_metrics.json`

**Output:**
- PRIM input files in `src/workflow/4_PRIM/t3b_sdiscovery/experiment_data/`

> **Note:** `PRIM_Input/` must be populated first — it holds a model that may
> have been computed separately from the `exp` pipeline. Import it with
> `python scripts/import_prim_input.py`.

#### 5. PRIM Analysis (`scripts/run_prim_analysis.py`)
Performs scenario discovery analysis.

```bash
python scripts/run_prim_analysis.py
```

**What it does:**
- Executes the PRIM structure, manager, and range-finder scripts under
  `src/workflow/4_PRIM/t3b_sdiscovery/`
- Analyzes the experiment data using PRIM methodology
- Identifies predominant parameter ranges
- Creates metrics in `src/workflow/4_PRIM/prim_analysis_metrics.json`

**Output:**
- `src/workflow/4_PRIM/t3b_sdiscovery/sd_ana_1_exp_1_Experiment.csv`
- `src/workflow/4_PRIM/t3b_sdiscovery/t3f4_predominant_ranges_a1_e1_Experiment.xlsx`

### Debugging Individual Stages

**View generated metrics:**
```bash
# Base future metrics
cat src/workflow/1_Experiment/Executables/metrics.json

# RDM experiment metrics
cat src/workflow/1_Experiment/Experimental_Platform/rdm_metrics.json

# Postprocessing metrics
cat Results/postprocess_metrics.json

# PRIM metrics
cat src/workflow/4_PRIM/prim_files_creator_metrics.json
cat src/workflow/4_PRIM/prim_analysis_metrics.json
```

**Clean outputs before re-running:**
```bash
# Clean base future outputs
rm -rf src/workflow/1_Experiment/Executables/Scenario*_0/

# Clean RDM experiment outputs
rm -rf src/workflow/1_Experiment/Experimental_Platform/Futures/

# Clean postprocessing outputs
rm -rf Results/*.csv

# Clean PRIM outputs
rm -rf src/workflow/4_PRIM/t3b_sdiscovery/experiment_data/*
```

### Comparison: Manual vs DVC Execution

| Feature | Manual Execution | DVC Automation |
|---------|-----------------|----------------|
| Setup | Install dependencies only | Creates full Conda environment |
| Execution | Run individual scripts | Automated pipeline execution |
| Caching | No caching | Intelligent stage caching |
| Dependencies | Manual tracking | Automatic dependency tracking |
| Reproducibility | Requires documentation | Built-in via dvc.lock |
| Debugging | Easy per-stage debugging | Full pipeline or single stage |
| Best for | Development, debugging | Production runs, CI/CD |

### Hybrid Approach

You can mix both approaches:

1. **Develop with manual execution:**
   ```bash
   python scripts/run_base_future.py  # Test changes
   ```

2. **Validate with DVC:**
   ```bash
   python run.py  # Full pipeline validation
   ```

3. **Debug specific stage:**
   ```bash
   dvc repro base_future  # Re-run only one stage
   ```

## Support

For issues or questions:
1. Check this documentation
2. Review DVC official docs: https://dvc.org/doc
3. Check the main README.md for OSeMOSYS-RDM-specific questions
4. For manual execution issues, verify dependencies: `pip list`
