# -*- coding: utf-8 -*-
"""
Postprocessing Wrapper for DVC Pipeline

This script executes the postprocessing stage that aggregates and concatenates
results from all RDM futures into final CSV files.

This script calls 1_output_dataset_creator.py which consolidates parquet outputs
from the experiment stage into final CSV files in src/Results/.

Usage:
    python scripts/run_postprocess.py

Manual execution:
    This script can be run independently to regenerate aggregated results.

DVC integration:
    Called automatically by DVC when executing the 'postprocess' stage.

Author: AFR_RDM Team
"""

import os
import sys
import json
import time
from pathlib import Path

def generate_metrics(results_dir, metrics_file):
    """
    Generate metrics JSON file for DVC tracking.
    Tracks number of output CSV files and their sizes.
    """
    metrics = {
        "stage": "postprocess",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "output_files": 0,
        "total_size_mb": 0.0,
        "files_list": []
    }

    # Count and measure output files
    if results_dir.exists():
        csv_files = list(results_dir.glob('*.csv'))
        metrics["output_files"] = len(csv_files)

        for csv_file in csv_files:
            size_mb = csv_file.stat().st_size / (1024 * 1024)
            metrics["total_size_mb"] += size_mb
            metrics["files_list"].append({
                "filename": csv_file.name,
                "size_mb": round(size_mb, 2)
            })

    # Round total size
    metrics["total_size_mb"] = round(metrics["total_size_mb"], 2)

    # Write metrics
    metrics_file.parent.mkdir(parents=True, exist_ok=True)
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"✓ Metrics written to {metrics_file}")
    print(f"  - Output CSV files: {metrics['output_files']}")
    print(f"  - Total size: {metrics['total_size_mb']} MB")

def main():
    """Main execution function"""
    print("=" * 70)
    print("AFR_RDM - Postprocessing (Results Aggregation)")
    print("=" * 70)

    # Paths
    project_root = Path(__file__).parent.parent
    experiment_dir = project_root / 'src' / 'workflow' / '1_Experiment'
    postprocess_script = experiment_dir / '1_output_dataset_creator.py'
    results_dir = project_root / 'src' / 'Results'
    metrics_file = project_root / 'src' / 'workflow' / '3_Postprocessing' / 'postprocess_metrics.json'
    interface_path = project_root / 'src' / 'Interface_RDM.xlsx'

    # Verify postprocessing script exists
    if not postprocess_script.exists():
        print(f"❌ Error: {postprocess_script} not found")
        sys.exit(1)

    # Read parameters from Interface_RDM.xlsx
    import pandas as pd
    setup_df = pd.read_excel(interface_path, sheet_name='Setup')
    region = str(setup_df.at[0, 'Region'])

    start_time = time.time()

    try:
        print(f"📂 Experiment directory: {experiment_dir}")
        print(f"📄 Script: {postprocess_script.name}")
        print(f"🔧 Region: {region}")
        print()

        # Change to src directory (script expects to be run from there)
        original_dir = os.getcwd()
        os.chdir(project_root / 'src')

        print("🚀 Executing 1_output_dataset_creator.py...")
        print("-" * 70)

        # Execute the postprocessing script as subprocess with region parameter
        import subprocess
        result = subprocess.run(
            [sys.executable, str(postprocess_script), region],
            check=True,
            capture_output=False
        )

        print("-" * 70)

        # Change back to original directory
        os.chdir(original_dir)

        # Ensure Results directory exists (even if empty) for DVC
        results_dir.mkdir(parents=True, exist_ok=True)

        # Aggregate per-future objective values into a single CSV in Results/
        # (written by z_auxiliar_code._save_future_objective during solving, so the
        # objective function value survives even if the terminal is closed).
        try:
            import glob
            import pandas as pd
            obj_roots = [
                experiment_dir / 'Executables',
                experiment_dir / 'Experimental_Platform' / 'Futures',
            ]
            obj_files = []
            for root in obj_roots:
                obj_files.extend(glob.glob(str(root / '**' / '*_objective.csv'), recursive=True))
            if obj_files:
                obj_df = pd.concat([pd.read_csv(f) for f in obj_files], ignore_index=True)
                obj_df['_fid'] = pd.to_numeric(obj_df['Future.ID'], errors='coerce')
                obj_df = obj_df.sort_values(['Strategy', '_fid']).drop(columns='_fid')
                obj_out = results_dir / 'objectives_futures.csv'
                obj_df.to_csv(obj_out, index=False)
                print(f"✓ Objective values written to {obj_out} ({len(obj_df)} solves)")
            else:
                print("ℹ️  No per-future objective files found to aggregate.")
        except Exception as e:
            print(f"⚠️  Could not aggregate objective values: {e}")

        # Generate metrics
        elapsed_time = time.time() - start_time
        print(f"\n⏱️  Execution time: {elapsed_time:.2f} seconds")

        generate_metrics(results_dir, metrics_file)

        print("\n✅ Postprocessing completed successfully!")

    except Exception as e:
        print(f"\n❌ Error during postprocessing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
