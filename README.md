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
<li><a href="#advanced-features">Advanced Features</a></li>
<li><a href="#shell-completion">Shell Completion</a></li>
<li><a href="#environment-variables">Environment Variables</a></li>
<li><a href="#configuration-file">Configuration File</a></li>
<li><a href="#usage-from-docker">Usage from Docker</a></li>
</ul>
</div>


---------------------------------------------------------------------------------

## Overview

The [AWS SSM Parameter-Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html) is great, but can be awkward to work with via the `awscli` tool.  This project provides the `ssm` tool as an alternative interface with simple CRUD.  It also supports moving or copying trees of multiple parameters, and performing those operations across multiple AWS profiles.

See [setup.cfg](setup.cfg) to find the latest info about required versions of boto.  There are other dependencies, including the popular [click](https://click.palletsprojects.com/) library for CLI support and [rich](https://rich.readthedocs.io/) for pretty output.

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

### Available Commands

#### Core CRUD Operations

| Command | Aliases | Description |
|---------|---------|-------------|
| `list` | `ls` | List parameters below a path |
| `list-dirs` | `ls-dirs` | List directories (non-leaf paths) only |
| `read` | `get` | Read a single parameter value |
| `update` | `put`, `set` | Create or update a parameter |
| `delete` | `rm` | Delete a single parameter |
| `delete-path` | `rm-path` | Delete all parameters under a path |
| `get-many` | `get-path` | Get all parameters under a path |
| `put-many` | `put-path` | Create multiple parameters from a file |

#### Copy/Move Operations

| Command | Aliases | Description |
|---------|---------|-------------|
| `copy` | `cp` | Copy a parameter to a new location |
| `copy-many` | `cp-many`, `cp-path` | Copy all parameters under a path |
| `move` | `mv` | Move a parameter to a new location |
| `move-many` | `mv-many`, `mv-path` | Move all parameters under a path |
| `rename` | `ren` | Rename a parameter (same profile) |

#### Search/Query Operations

| Command | Aliases | Description |
|---------|---------|-------------|
| `search` | `find` | Search parameters by name pattern |
| `grep` | `grep-values` | Search parameters by value content |
| `diff` | `compare` | Compare parameters between paths/profiles |
| `count` | `cnt` | Count parameters under a path |
| `tree` | - | Display parameters in tree format with metadata |
| `stat` | `st` | Show account info and parameter stats |

#### History/Versioning

| Command | Aliases | Description |
|---------|---------|-------------|
| `history` | `hist` | View parameter version history |

#### Tag Management

| Command | Aliases | Description |
|---------|---------|-------------|
| `tags` | `show-tags` | Show tags for a parameter |
| `add-tags` | - | Add tags to a parameter |
| `remove-tags` | - | Remove tags from a parameter |

#### GitOps/Sync Operations

| Command | Aliases | Description |
|---------|---------|-------------|
| `sync-pull` | `pull` | Pull parameters from SSM to a local file |
| `sync-push` | `push` | Push parameters from a local file to SSM |
| `sync-diff` | `sync-status` | Show differences between local file and SSM |

#### Backup/Restore

| Command | Aliases | Description |
|---------|---------|-------------|
| `backup` | - | Create compressed backup with metadata |
| `restore` | - | Restore parameters from backup archive |

#### Environment/Export Operations

| Command | Aliases | Description |
|---------|---------|-------------|
| `env-export` | `env`, `dotenv` | Export as environment variables (.env format) |
| `export-terraform` | - | Export as Terraform resources |
| `k8s-export` | - | Export as Kubernetes Secret manifest |

#### Security Operations

| Command | Aliases | Description |
|---------|---------|-------------|
| `rotate` | - | Rotate a secret with a new random value |
| `generate-secret` | - | Generate a random secret value |
| `rekey` | - | Re-encrypt parameters with a new KMS key |
| `list-by-kms` | `ls-kms` | List parameters by KMS key |

#### Policy Management

| Command | Aliases | Description |
|---------|---------|-------------|
| `get-policy` | - | Get parameter policy (expiration, etc.) |
| `set-policy` | - | Set parameter policy (requires Advanced tier) |

#### Validation

| Command | Aliases | Description |
|---------|---------|-------------|
| `validate` | - | Validate parameters against a schema |
| `lint` | - | Lint a parameters file before pushing |

#### Monitoring/Audit

| Command | Aliases | Description |
|---------|---------|-------------|
| `watch` | - | Watch for changes to parameters |
| `audit` | `audit-log` | Query CloudTrail for SSM access events |

#### CI/CD Integration

| Command | Aliases | Description |
|---------|---------|-------------|
| `inject` | - | Inject SSM values into template files |
| `verify-access` | `check-access` | Verify access to parameters (for CI/CD checks) |
| `put-template` | - | Create parameters from template with variables |

### Common Options

All commands support these options:

- `--profile`: AWS profile to use (default: `default`, or `AWS_PROFILE` env var)
- `--debug`: Enable verbose debug output
- `--quiet` / `-q`: Suppress non-essential output
- `--format`: Output format (`json`, `yaml`, `stdout`, `tree`, `env`)

### Basic Examples

```bash
# List all parameters
ssm ls /

# Read a specific parameter
ssm get /prod/database/password

# Read a specific version
ssm get /prod/database/password --version 3

# Create/update a parameter
ssm put /dev/api/key "my-secret-value"

# Create with specific type (String, SecureString, StringList)
ssm put /config/setting "value" --type String

# Read value from file
ssm put /prod/cert --file ./certificate.pem

# Read value from stdin
echo "secret" | ssm put /prod/secret --stdin

# Copy a parameter
ssm cp /prod/config/key /staging/config/key

# Copy between AWS profiles
ssm cp /prod/secret /staging/secret --src-profile prod --dst-profile staging

# Copy an entire path hierarchy
ssm cp-many /prod/config /staging/config

# Rename a parameter
ssm rename /old/path/key /new/path/key

# Search for parameters by name pattern
ssm search "/prod/*/password"
ssm search "*database*"

# Search for parameters by value content
ssm grep "localhost" --path /dev/
ssm grep --regex "https?://.*\.example\.com" --path /prod/

# Count parameters
ssm count /prod/
ssm count / --by-type

# Compare two paths
ssm diff /prod/config /staging/config
ssm diff /prod/config /staging/config --show-values

# View parameter history
ssm history /prod/secret --max-results 20

# Delete with preview (dry-run)
ssm rm /test/secret --dry-run

# Delete an entire path (with confirmation)
ssm rm-path /test/old-config

# Bulk create from YAML file
ssm put-many /prod/config --file secrets.yaml

# View and manage tags
ssm tags /prod/secret
ssm add-tags /prod/secret --tag env=prod --tag team=backend
ssm remove-tags /prod/secret --key deprecated
```

See [the integration tests](https://github.com/Robot-Wranglers/aws-ssm-tool/tree/master/tests/integration/test.sh) for more examples.

---------------------------------------------------------------------------------

## Advanced Features

### GitOps/Sync Workflow

Manage parameters using a GitOps workflow with local YAML/JSON files:

```bash
# Pull current state from SSM to a local file
ssm sync-pull /prod/config ./config.yaml

# Check what would change before pushing
ssm sync-diff /prod/config ./config.yaml

# Push changes to SSM
ssm sync-push /prod/config ./config.yaml --dry-run
ssm sync-push /prod/config ./config.yaml

# Push and delete parameters not in the file
ssm sync-push /prod/config ./config.yaml --delete-missing
```

### Backup and Restore

Create full backups with metadata and restore them:

```bash
# Create a compressed backup with metadata
ssm backup /prod/ ./backup.json.gz

# Create backup without metadata
ssm backup /prod/ ./backup.json.gz --no-metadata

# Restore from backup (dry-run)
ssm restore ./backup.json.gz --dry-run

# Restore to the same location
ssm restore ./backup.json.gz

# Restore to a different path
ssm restore ./backup.json.gz --target-prefix /staging/

# Restore and overwrite existing parameters
ssm restore ./backup.json.gz --overwrite
```

### Environment Variable Export

Export parameters as environment variables for different use cases:

```bash
# Export as .env file format
ssm env-export /prod/app/ > .env

# Export with a prefix
ssm env-export /prod/app/ --prefix APP_

# Export as Docker --env flags
ssm env-export /prod/app/ --docker
# Output: --env DB_HOST=localhost --env DB_PORT=5432

# Don't quote special characters
ssm env-export /prod/app/ --no-quote
```

### Secret Rotation

Generate and rotate secrets automatically:

```bash
# Generate a random secret (32 chars, alphanumeric)
ssm generate-secret

# Generate with specific options
ssm generate-secret --length 64 --chars all
ssm generate-secret --chars alphanumeric --exclude "0O1l"

# Rotate a secret (generate new value and update)
ssm rotate /prod/api/key --dry-run
ssm rotate /prod/api/key
ssm rotate /prod/api/key --length 64 --chars all
```

### KMS Key Management

Manage encryption keys for your parameters:

```bash
# List parameters encrypted with a specific KMS key
ssm list-by-kms alias/my-key --path /prod/

# Re-encrypt parameters with a new KMS key
ssm rekey /prod/ --from-key alias/old-key --to-key alias/new-key --dry-run
ssm rekey /prod/ --from-key alias/old-key --to-key alias/new-key
```

### Parameter Policies

Set expiration and notification policies (requires Advanced tier):

```bash
# Get current policy
ssm get-policy /prod/temp-token

# Set expiration policy (expires in 90 days)
ssm set-policy /prod/temp-token --expiration-days 90

# Set notification before expiration
ssm set-policy /prod/cert --expiration-days 365 --notify-before-days 30

# Set no-change notification (alert if not updated)
ssm set-policy /prod/rotating-key --no-change-days 7
```

### Watch for Changes

Monitor parameters for changes in real-time:

```bash
# Watch all parameters under a path
ssm watch /prod/

# Watch with custom interval
ssm watch /prod/ --interval 10
```

### Template Support

Create parameters from templates with variable substitution:

```bash
# template.yaml:
# database_url: postgres://{{DB_USER}}:{{DB_PASS}}@{{DB_HOST}}/{{DB_NAME}}
# api_endpoint: https://{{ENVIRONMENT}}.api.example.com

ssm put-template /prod/app/ template.yaml \
    --var DB_USER=admin \
    --var DB_PASS=secret123 \
    --var DB_HOST=db.example.com \
    --var DB_NAME=myapp \
    --var ENVIRONMENT=prod
```

### Validation

Validate parameters against schemas:

```bash
# Check that parameters exist
ssm validate /prod/required-config/ --exists

# Validate against a JSON schema
ssm validate /prod/config/ --schema ./schema.json

# Lint a parameters file before pushing
ssm lint ./config.yaml
```

Schema file example:
```json
{
  "required": ["database_url", "api_key"],
  "parameters": {
    "database_url": {
      "pattern": "^postgres://.*$",
      "minLength": 10
    },
    "log_level": {
      "enum": ["DEBUG", "INFO", "WARNING", "ERROR"]
    }
  }
}
```

### Audit Log

Query CloudTrail for SSM access events:

```bash
# View recent SSM events
ssm audit /

# Filter by time period
ssm audit / --since 24h
ssm audit / --since 7d
ssm audit / --since 2w

# Filter by user
ssm audit / --who admin@example.com

# Filter by action
ssm audit / --action GetParameter
ssm audit / --action PutParameter
```

### CI/CD Integration

Integrate with CI/CD pipelines:

```bash
# Verify access to required parameters (exit 0 if accessible)
ssm verify-access /prod/app/

# Inject SSM values into config files
# config.template: "database: {{SSM:/prod/db/url}}"
ssm inject config.template -o config.yaml

# Export for use in scripts
eval $(ssm env-export /prod/app/)
```

### Terraform Export

Export parameters as Terraform resources:

```bash
# Export to stdout
ssm export-terraform /prod/app/

# Export to a file
ssm export-terraform /prod/app/ -o ssm_parameters.tf
```

### Kubernetes Integration

Export parameters as Kubernetes Secrets:

```bash
# Export as Kubernetes Secret manifest
ssm k8s-export /prod/app/

# With custom name and namespace
ssm k8s-export /prod/app/ --secret-name my-app-secrets --namespace production

# Export to a file
ssm k8s-export /prod/app/ -o k8s-secret.yaml

# Apply directly to cluster
ssm k8s-export /prod/app/ | kubectl apply -f -
```

---------------------------------------------------------------------------------

## Shell Completion

Enable tab completion for your shell:

### Bash

```bash
# Add to ~/.bashrc
eval "$(_SSM_COMPLETE=bash_source ssm)"

# Or generate a completion script
_SSM_COMPLETE=bash_source ssm > ~/.ssm-complete.bash
echo "source ~/.ssm-complete.bash" >> ~/.bashrc
```

### Zsh

```bash
# Add to ~/.zshrc
eval "$(_SSM_COMPLETE=zsh_source ssm)"
```

### Fish

```bash
# Add to ~/.config/fish/completions/ssm.fish
_SSM_COMPLETE=fish_source ssm > ~/.config/fish/completions/ssm.fish
```

---------------------------------------------------------------------------------

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_PROFILE` | AWS profile to use | `default` |
| `SSM_LOG_LEVEL` | Log verbosity (DEBUG, INFO, WARNING, ERROR) | `WARNING` |

---------------------------------------------------------------------------------

## Configuration File

You can create a `.ssm.yaml` (or `.ssm.yml` or `.ssm.json`) file in your project directory for default settings:

```yaml
# .ssm.yaml
default_profile: production
default_path_prefix: /myapp/prod/
validation:
  required:
    - database_url
    - api_key
```

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
