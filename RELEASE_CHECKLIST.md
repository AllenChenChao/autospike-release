# Public Release Checklist

Use this checklist before pushing the public repository.

- Confirm the package name, project name, and CLI name are final.
- Replace `LICENSE` with the selected public license.
- Search for private paths, credentials, internal server names, and unpublished notes.
- Confirm no private datasets, checkpoints, or large generated results are included.
- Run `python examples/quickstart.py`.
- Run `python -m autospike demo --output-dir outputs/demo`.
- Run tests.
- Create the public GitHub repository from this directory only.
- Do not copy the private repository `.git` directory or commit history.
