# ignr

ignr is a small command-line tool that fetches .gitignore templates directly from Github's official github/githinore repo, so you never have to manually open the site, find your language, and copy-paste the contents into a new project by hand. It offers multiple features, including the ability to select commonly used language templates or create and add your own custom templates.

## Installation

### Option 1: Python
`ignr` requires Python 3.11+.

Clone the repo and install it as a tool:

```bash
git clone https://github.com/yourusername/ignr.git
cd ignr
uv tool install .
```

### Option 2: Binaries
See the latest releases section for more info.

## Docs



(Or use `pipx install .` / `pip install .` if you prefer those.)

**Usage**:

```console
$ ignr [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `add`: Add a .gitignore template to the project.
* `init`: Initialize the tool by fetching all...
* `update`: Update the cache with the latest templates...
* `list`: List all templates in the cache.
* `delete`: Delete a template from the cache.!
* `import`: Import a .gitignore template from the repo...

## `ignr add`

Add a .gitignore template to the project.

**Usage**:

```console
$ ignr add [OPTIONS] {name}
```

**Arguments**:

* `name`: [required]

**Options**:

* `--help`: Show this message and exit.

## `ignr init`

Initialize the tool by fetching all templates and storing them in a cache.

**Usage**:

```console
$ ignr init [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `ignr update`

Update the cache with the latest templates from GitIgnore repository.

**Usage**:

```console
$ ignr update [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `ignr list`

List all templates in the cache.

**Usage**:

```console
$ ignr list [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `ignr delete`

Delete a template from the cache.!

**Usage**:

```console
$ ignr delete [OPTIONS] {name}
```

**Arguments**:

* `name`: [required]

**Options**:

* `--help`: Show this message and exit.

## `ignr import`

Import a .gitignore template from the repo list or a custom file.

**Usage**:

```console
$ ignr import [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `repo`: Import a template from the GitHub...
* `custom`: Import a custom .gitignore file under a...

### `ignr import repo`

Import a template from the GitHub gitignore repo.

**Usage**:

```console
$ ignr import repo [OPTIONS] {name}
```

**Arguments**:

* `name`: [required]

**Options**:

* `--help`: Show this message and exit.

### `ignr import custom`

Import a custom .gitignore file under a given name.

**Usage**:

```console
$ ignr import custom [OPTIONS] {path} {name}
```

**Arguments**:

* `path`: [required]
* `name`: [required]

**Options**:

* `--help`: Show this message and exit.
