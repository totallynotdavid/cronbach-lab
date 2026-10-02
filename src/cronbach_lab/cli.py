"""Command line: run the scenarios, or write the R cross-check datasets."""

import argparse
from pathlib import Path

from .datasets import draw_datasets, write_datasets
from .excel import write_workbooks
from .report import write_findings, write_plots
from .scenarios import run_all


def main(argv=None):
    parser = argparse.ArgumentParser(prog="cronbach-lab", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    run = commands.add_parser(
        "run", help="run every scenario; write CSV, PNGs, findings.md, datasets and workbooks"
    )
    run.add_argument("--out", type=Path, default=Path("results"))
    run.add_argument("--reps", type=int, default=1000, help="replicates per setting")
    run.add_argument("--seed", type=int, default=1)

    data = commands.add_parser("datasets", help="write only the R cross-check datasets")
    data.add_argument("--out", type=Path, default=Path("results/datasets"))
    data.add_argument("--seed", type=int, default=1)

    args = parser.parse_args(argv)
    if args.command == "datasets":
        write_datasets(args.out, draw_datasets(args.seed)[0])
        return

    args.out.mkdir(parents=True, exist_ok=True)
    results = run_all(args.reps, args.seed)
    results.to_csv(args.out / "results.csv", index=False)
    write_plots(results, args.out / "plots")
    write_findings(results, args.reps, args.out / "findings.md")
    datasets, age_dataset = draw_datasets(args.seed)
    write_datasets(args.out / "datasets", datasets)
    write_workbooks(args.out / "xlsx", datasets, age_dataset)
    print(f"wrote {args.out}/results.csv, plots/, findings.md, datasets/, xlsx/")
