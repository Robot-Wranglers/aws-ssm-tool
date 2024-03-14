<table width=100%>
  <tr>
    <td colspan=2><strong>
    aws-ssm-tool
      </strong>&nbsp;&nbsp;&nbsp;&nbsp;
    </td>
  </tr>
  <tr>
    <td width=15%><img src=https://raw.githubusercontent.com/Robot-Wranglers/aws-ssm-tool/master/img/icon.png style="width:150px"></td>
    <td>
    SSM tool is a small helper for interacting with Amazon Simple Systems Manager, focusing on secrets storage/retrieval.
    </td>
  </tr>
</table>
<a href=https://pypi.python.org/pypi/aws-ssm-tool/><img src="https://img.shields.io/pypi/l/aws-ssm-tool.svg"></a>
<a href=https://pypi.python.org/pypi/aws-ssm-tool/><img src="https://badge.fury.io/py/aws-ssm-tool.svg"></a>
<a href="https://github.com/Robot-Wranglers/aws-ssm-tool/actions/workflows/python-test.yml"><img src="https://github.com/Robot-Wranglers/aws-ssm-tool/actions/workflows/python-test.yml/badge.svg"></a>
<a href="https://hub.docker.com/r/robotwranglers/aws-ssm-tool/tags"><img src="https://img.shields.io/badge/dockerhub--blue.svg?logo=Docker"></a>

---------------------------------------------------------------------------------

<div class="toc">
<ul>
<li><a href="#overview">Overview</a></li>
<li><a href="#installation">Installation</a></li>
<li><a href="#usage">Usage</a></li>
<li><a href="#usage-from-docker">Usage from Docker</a></li>
</ul>
</div>


---------------------------------------------------------------------------------

## Overview

The [AWS SSM Parameter-Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html) is great, but can be awkward to work with via the `awscli` tool.  This project provides the `ssm` tool as an alternative interface with simple CRUD.  It also supports moving or copying trees of multiple parameters, and performing those operations across multiple AWS profiles.

See [setup.cfg](setup.cfg) to find the latest info about required versions of boto.  There are other dependencies, including the popular [click](#) library for CLI support and [rich](#) for pretty output.

See the [Usage section](#usage) for more details.

---------------------------------------------------------------------------------

## Installation

See [pypi](https://pypi.org/project/aws-ssm-tool) for available releases.

```
pip install aws-ssm-tool
```

---------------------------------------------------------------------------------

## Usage

After installation, you can invoke this tool as either `ssm` or `python -m ssm`.

Usage info follows:

Usage info follows:

```bash
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



See [the integration tests](https://github.com/Robot-Wranglers/aws-ssm-tool/tree/master/tests/integration/test.sh) for more examples.

---------------------------------------------------------------------------------

## Usage from Docker

If you want to build locally, see the [Dockerfile in this repo](Dockerfile) and use the [Makefile](Makefile):

```bash
$ make docker-build docker-test
```

If you don't want to build the container yourself, you can pull it like this:

```bash
$ docker pull robotwranglers/aws-ssm-tool
Using default tag: latest
latest: Pulling from robotwranglers/aws-ssm-tool
docker.io/robotwranglers/aws-ssm-tool:latest
```

See a typical invocation below.  The 1st volume is for authenticating with SSM.  The 2nd volume shares the working directory with the container so commands using files (like `ssm put --file ./path/to/file /path/to/key`) can still work.

```bash
$ docker run \
  -v ~/.aws:/root/.aws \
  -v `pwd`:/workspace \
  -w /workspace \
  docker.io/robotwranglers/aws-ssm-tool:latest \
    ssm ls /
```
