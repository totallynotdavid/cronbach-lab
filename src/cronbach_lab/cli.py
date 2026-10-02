"""Command line: run the scenarios, or write the R cross-check datasets."""

import argparse
from pathlib import Path

from .datasets import write_datasets
from .report import write_findings, write_plots
from .scenarios import run_all


def main(argv=None):
    parser = argparse.ArgumentParser(prog="cronbach-lab", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    run = commands.add_parser(
        "run", help="run every scenario; write CSV, PNGs, findings.md and datasets"
    )
    run.add_argument("--out", type=Path, default=Path("results"))
    run.add_argument("--reps", type=int, default=1000, help="replicates per setting")
    run.add_argument("--seed", type=int, default=1)

    data = commands.add_parser("datasets", help="write only the R cross-check datasets")
    data.add_argument("--out", type=Path, default=Path("results/datasets"))
    data.add_argument("--seed", type=int, default=1)

    args = parser.parse_args(argv)
    if args.command == "datasets":
        write_datasets(args.out, args.seed)
        return

    args.out.mkdir(parents=True, exist_ok=True)
    results = run_all(args.reps, args.seed)
    results.to_csv(args.out / "results.csv", index=False)
    write_plots(results, args.out / "plots")
    write_findings(results, args.reps, args.out / "findings.md")
    write_datasets(args.out / "datasets", args.seed)
    print(f"wrote {args.out}/results.csv, plots/, findings.md, datasets/")
