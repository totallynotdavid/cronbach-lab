# Contributing

## Set up

Clone the repository, enter it, and install the locked Python dependencies:

```sh
git clone https://github.com/totallynotdavid/cronbach-lab.git
cd cronbach-lab
uv sync
```

The project uses Python 3.11 or newer. `mise.toml` pins Python and uv for
contributors who use mise.

## Check a change

Run the repository check before submitting a change:

```sh
mise run check
```

This runs `ruff check` and `pytest`. To run each part separately:

```sh
uv run ruff check
uv run ruff format --line-length 100
uv run pytest
```

The R comparison tests run when `Rscript` and the `psych` package are available.
Otherwise, those tests are skipped. Run the comparison directly with
[the usage instructions](../docs/usage.md#compare-python-with-r).

## Submit a change

Open an issue before a change that is not straightforward. Keep a change
focused, add a behavior test for code changes, and update the document that owns
any changed workflow or contract. Open a pull request with the checks you ran
and a short description of the result.
