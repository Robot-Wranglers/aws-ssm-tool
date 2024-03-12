<table width=100%>
  <tr>
    <td colspan=2><strong>
    aws-ssm-tool
      </strong>&nbsp;&nbsp;&nbsp;&nbsp;
    </td>
  </tr>
  <tr>
    <td width=15%><img src=https://raw.githubusercontent.com/Robot-Wranglers/ssm-tool/master/img/icon.png style="width:150px"></td>
    <td>
    SSM tool is a small helper for interacting with Amazon Simple Systems Manager, focusing on secrets storage/retrieval.
    <br/><br/>
    <a href=https://pypi.python.org/pypi/aws-ssm-tool/><img src="https://img.shields.io/pypi/l/aws-ssm-tool.svg"></a>
    <a href=https://pypi.python.org/pypi/aws-ssm-tool/><img src="https://badge.fury.io/py/aws-ssm-tool.svg"></a>
    <a href="https://github.com/https://github.com/Robot-Wranglers/ssm-tool/actions/workflows/python-test.yml"><img src="https://github.com/https://github.com/Robot-Wranglers/ssm-tool/actions/workflows/python-test.yml/badge.svg"></a>
    </td>
  </tr>
</table>

---------------------------------------------------------------------------------

<div class="toc">
<ul>
<li><a href="#overview">Overview</a></li>
<li><a href="#installation">Installation</a></li>
<li><a href="#usage">Usage</a></li>
</ul>
</div>


---------------------------------------------------------------------------------

## Overview

The [AWS SSM Parameter-Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html) is great, but can be awkward to work with via the `awscli` tool.  This project provides the `ssm` tool as an alternative interface with simple CRUD.  It also supports moving or copying trees of multiple parameters, and performing those operations across multiple AWS profiles.

See [setup.cfg](setup.cfg) to find the latest info about required versions of boto.  There are other dependencies, including the popular [click](#) library for CLI support and [rich](#) for pretty output.

See the [Usage section](#usage) for more details.

---------------------------------------------------------------------------------

## Installation

See [pypi](https://pypi.org/project/ssm-tool) for available releases.

```
pip install aws-ssm-tool
```

---------------------------------------------------------------------------------

## Usage

After installation, you can invoke this tool as either `ssm` or `python -m ssm`.

Usage info follows:

```bash

$ ssm --help

Usage: ssm [OPTIONS] COMMAND [ARGS]...

  SSM tool, a small helper for interacting with Amazon Simple Systems Manager
  for secrets storage/retrieval.

Options:
  --help  Show this message and exit.

Commands:
  copy       copy a secret
  delete     delete secret (keeping a local-backup is default)
  get-many   get many secrets from specified hierarchy/namespace
  list       list parameters with prefixes below the given path
  move       move a secret
  move-many  move a whole path of secrets
  put-many   put many secrets
  read       get a secret
  stat       reports status, including account details and metadata...
  update     put a secret
  ls         ALIAS for `list`
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

See [the integration tests](https://github.com/Robot-Wranglers/ssm-tool/tree/master/tests/integration/test.sh) for more examples.

---------------------------------------------------------------------------------
