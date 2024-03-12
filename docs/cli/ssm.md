
[tooltip-module-entrypoints]: ## "Module Entrypoints"
[tooltip-package-entrypoints]: ## "Console Script Entrypoint"

[Docs](../) *↔* [CLI](README.md) *↔* [Console Scripts](README.md#console-scripts) *↔* **Module Entrypoints**

---------------------------------------------------


## [**ℳ**][tooltip-module-entrypoints] ssm

[**[Module]**](README.md#module-entrypoints) `ssm` publishes a command line interface (*[source](/src/ssm/__main__.py)*).

Example usage:

```bash
$ python -mssm --help

Usage: python -m ssm [OPTIONS] COMMAND [ARGS]...

  SSM tool, a small helper for interacting with Amazon Simple Systems Manager
  for secrets storage/retrieval.

Options:
  --help  Show this message and exit.

Commands:
  copy       copies a secret from given source to destination
  delete     deletes secret (keeping a local-backup is default)
  get-many   gets many secrets from specified hierarchy/namespace
  list       Lists parameters with prefixes below the given path.
  list-dirs  lists subpaths (i.e.
  move       moves a secret from src to dest
  move-many  moves a whole path of secrets to a new location
  put-many   put many secrets
  read       reads a secret
  stat       reports status, including account details and metadata...
  update     updates secret in given location with new value
  cp         ALIAS for `copy`
  get        ALIAS for `read`
  get-path   ALIAS for `get-many`
  ls         ALIAS for `list`
  ls-dirs    ALIAS for `list-dirs`
  move-path  ALIAS for `move-many`
  mv         ALIAS for `move`
  mv-many    ALIAS for `move-many`
  mv-path    ALIAS for `move-many`
  put        ALIAS for `update`
  put-path   ALIAS for `put-many`
  rm         ALIAS for `delete`
  set        ALIAS for `update`
  st         ALIAS for `stat`
```