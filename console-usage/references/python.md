# Python: uv, uvx, and Single-File Scripts

Never install into the system interpreter, and never assume the ambient `python3` has the required packages or version.
uv supplies both: an interpreter it can download and an environment created on demand.

## Running Code

```bash
uv run script.py                       # resolves inline metadata, then runs
uv run --script script.py              # force script mode for a file without a .py suffix
uv run --with rich script.py           # add a dependency for this invocation only
uv run -m pytest                       # run a module inside the project environment
uv run --frozen -m pytest              # refuse to update the lockfile
uv run --offline script.py             # fail rather than reach the network
```

The flag order is `uv run --script script.py`. `uv --script run` is not a valid invocation.

## Tools Without Installation

```bash
uvx ruff format .                      # run a tool in a throwaway environment
uvx ruff@0.14.2 check .                # pin the tool version
uvx --from 'huggingface_hub[cli]' hf download org/model
```

`uvx` is `uv tool run`. Use it for one-off linting, formatting, and conversion work so that nothing is added to the
project or to the user's home directory beyond the shared cache.

## Projects

```bash
uv python pin 3.13                     # write .python-version
uv venv                                # create .venv using the pinned version
uv add requests                        # add a dependency and update uv.lock
uv sync --frozen                       # install exactly what the lockfile says
uv lock --check                        # verify the lockfile matches pyproject.toml
uv export --format requirements-txt    # for a consumer that cannot read the lockfile
```

In continuous integration prefer `uv sync --frozen` and `uv run --frozen`, which fail on a stale lockfile rather than
quietly resolving something new.

## PEP 723 Single-File Scripts

Inline metadata makes a script self-contained: dependencies, and optionally the interpreter version, live in a comment
block that uv reads before execution.

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "requests<3",
#   "rich",
# ]
# ///

import requests
from rich.pretty import pprint

resp = requests.get("https://peps.python.org/api/peps.json", timeout=10)
resp.raise_for_status()
data = resp.json()
pprint([(number, pep["title"]) for number, pep in list(data.items())[:10]])
```

```bash
uv run fetch-peps.py                   # environment built from the block above
uv add --script fetch-peps.py httpx    # append a dependency to the block
uv lock --script fetch-peps.py         # write fetch-peps.py.lock for reproducibility
```

Prefer this form for every throwaway script an agent writes. It documents its own requirements, it cannot be broken by
an unrelated change to the project environment, and it leaves no virtual environment behind.

## Edge Cases and Mistakes

- **`pip install` in a session.** Almost always wrong. On a managed distribution it fails outright, and where it
  succeeds it mutates an interpreter shared by other software. Use `uv add`, `uv run --with`, or `uvx`.
- **`python script.py` fails on an import that is present in the lockfile.** The command bypassed the environment. Use
  `uv run`, which activates it.
- **The script has no inline metadata and needs a package.** `uv run --with pkg script.py` for one run, or
  `uv add --script script.py pkg` to record it.
- **CI resolves different versions than the developer did.** A missing `--frozen`. Add it to every CI invocation, and
  commit `uv.lock`.
- **No network in the sandbox.** `uv run --offline` fails fast with a clear message instead of retrying a download.
  Pre-warm the cache when the environment allows it.
- **A tool is needed repeatedly in one session.** `uvx` re-resolves per invocation; `uv tool install ruff` is the
  persistent form, but it writes to the user's home directory, so ask first.
- **The requested interpreter is absent.** `uv python install 3.13` downloads it, which is a network operation and a
  write outside the project; mention it before running it.
- **A `requirements.txt`-only project.** `uv pip install -r requirements.txt` inside `uv venv` works and keeps the
  system interpreter untouched. Offer to migrate; do not migrate unasked.
