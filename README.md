<!--- This is a markdown file.  Comments look like this --->

<table width=100%>
  <tr>
    <td colspan=2><strong>
    aws-ssm-tool
      </strong>&nbsp;&nbsp;&nbsp;&nbsp;
      <small><small>
      </small></small>
    </td>
  </tr>
  <tr>
    <td width=15%><img src=img/icon.png style="width:150px"></td>
    <td>
    Helper for interacting with SSM
    </td>
  </tr>
</table>

  * [Overview](#overview)
  * [Installation](#installation)
  * [Usage](#usage)


---------------------------------------------------------------------------------

## Overview

The [AWS SSM Parameter-Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html) is great, but can be awkward to work with via the `awscli` tool.  This project provides the `ssm` tool as an alternative interface with simple CRUD.

See [setup.cfg](setup.cfg) to find the latest info about required versions of boto.

See the [Usage section](#usage) for more details

---------------------------------------------------------------------------------

## Installation

See [pypi](https://pypi.org/project/aws-ssm-tool/) for available releases.

```
pip install aws-ssm-tool
```

---------------------------------------------------------------------------------

## Usage

After installation, you can invoke this tool as either `ssm` or `python -m ssm`.  
Usage info follows:

```
$ ssm --help

Usage: ssm [OPTIONS] COMMAND [ARGS]...

  Tool for accessing secrets

Options:
  --help  Show this message and exit.

Commands:
  copy       copy a secret
  delete     delete secret (keeping a local-backup is default)
  get-many   get many secrets from hierarchy/namespace
  list       list prefixes below the given path
  move       move a secret
  move-many  move a whole path of secrets
  put-many   put many secrets
  read       get a secret
  update     put a secret
  cp         ALIAS for `copy`
  get        ALIAS for `read`
  get-path   ALIAS for `get-many`
  ls         ALIAS for `list`
  move-path  ALIAS for `move-many`
  mv         ALIAS for `move`
  mv-many    ALIAS for `move-many`
  mv-path    ALIAS for `move-many`
  put        ALIAS for `update`
  put-path   ALIAS for `put-many`
  rm         ALIAS for `delete`
  set        ALIAS for `update`
```

---------------------------------------------------------------------------------
