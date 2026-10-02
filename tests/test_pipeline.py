import shutil
import subprocess
from pathlib import Path

import pandas as pd
import pytest

from cronbach_lab.cli import main
from cronbach_lab.datasets import draw_datasets, write_datasets

CROSSCHECK = Path(__file__).parents[1] / "r" / "crosscheck.R"


def r_has_psych():
    if shutil.which("Rscript") is None:
        return False
    probe = subprocess.run(["Rscript", "-e", "library(psych)"], capture_output=True, check=False)
    return probe.returncode == 0


def test_run_writes_csv_plots_and_findings(tmp_path):
    out = tmp_path / "out"
    main(["run", "--out", str(out), "--reps", "5"])

    results = pd.read_csv(out / "results.csv")
    assert set(results.scenario) == {
        "loading_items",
        "sample_size",
        "response_shape",
        "satisfaccion",
        "multidimensional",
        "age_groups",
        "bad_items",
        "bootstrap_interval",
        "profiles",
        "profiles_same_loading",
        "response_style",
    }
    assert results.share_ge_0_7.between(0, 1).all()
    assert (results.p2_5 <= results.p97_5).all()

    pngs = sorted(p.name for p in (out / "plots").glob("*.png"))
    assert "loading_items.png" in pngs and len(pngs) == 11
    assert all((out / "plots" / p).stat().st_size > 1000 for p in pngs)

    assert len(list((out / "xlsx").glob("*_alpha*.xlsx"))) == 14

    findings = (out / "findings.md").read_text()
    pooled = results[results.setting == "pooled, 13 items as is"].iloc[0]
    squeezed = " ".join(findings.split())
    assert f"| pooled, 13 items as is | {pooled.mean_alpha:.2f} |" in squeezed
    assert "5 replicates per setting" in squeezed
    assert "## 9. Location profiles: lima and california" in findings
    lima = results[results.setting == "marketing sensorial, lima"].iloc[0]
    assert f"| marketing sensorial | {lima.mean_alpha:.2f} (" in squeezed


@pytest.mark.skipif(not r_has_psych(), reason="Rscript with the psych package is not installed")
def test_r_psych_agrees_with_python(tmp_path):
    write_datasets(tmp_path, draw_datasets()[0])
    done = subprocess.run(
        ["Rscript", str(CROSSCHECK), str(tmp_path)], capture_output=True, text=True, check=False
    )
    assert done.returncode == 0, done.stdout + done.stderr
    assert "OK: 9 datasets agree" in done.stdout


@pytest.mark.skipif(not r_has_psych(), reason="Rscript with the psych package is not installed")
def test_r_crosscheck_fails_when_python_value_is_wrong(tmp_path):
    write_datasets(tmp_path, draw_datasets()[0])
    reference = pd.read_csv(tmp_path / "python_alpha.csv")
    reference.loc[0, "raw_alpha"] += 1e-3
    reference.to_csv(tmp_path / "python_alpha.csv", index=False)
    done = subprocess.run(
        ["Rscript", str(CROSSCHECK), str(tmp_path)], capture_output=True, text=True, check=False
    )
    assert done.returncode == 1
    assert "FAIL" in done.stdout
