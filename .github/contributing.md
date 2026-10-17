# Contributing

## Set up

Clone the repository, enter it, and install the tools and the locked Python
dependencies:

```sh
git clone https://github.com/totallynotdavid/cronbach-lab.git
cd cronbach-lab
mise install
mise run install
```

The project uses Python 3.11 or newer. `mise.toml` pins Python, uv, gitleaks and
oxfmt.

## Check a change

Run the repository check before submitting a change. It never writes tracked
files:

```sh
mise run check
```

This runs `lint` (ruff, oxfmt for Markdown, YAML and JSON, and gitleaks),
`typecheck` (mypy in strict mode), `test` (pytest) and `build`. Run
`mise run fix` first to apply the safe ruff fixes and the formatters. To run one
part, use its task: `mise run lint`, `mise run typecheck`, `mise run test` or
`mise run build`.

The R comparison tests run when `Rscript` and the `psych` package are available.
Otherwise, those tests are skipped. Run the comparison directly with
[the usage instructions](../docs/usage.md#compare-python-with-r).

## Submit a change

Open an issue before a change that is not straightforward. Keep a change
focused, add a behavior test for code changes, and update the document that owns
any changed workflow or contract. Open a pull request with the checks you ran
and a short description of the result.
