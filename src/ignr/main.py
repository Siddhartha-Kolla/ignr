import json
from pathlib import Path
from shutil import copyfile
from time import time

import requests
import typer
from InquirerPy import inquirer

CACHE_CONFIG_FILE = Path.home() / ".gitignore_templates" / "config.json"
CACHE_FOLDER = Path.home() / ".gitignore_templates"
CACHE_FOLDER.mkdir(parents=True, exist_ok=True)
CACHE_REFRESH_INTERVAL = 60 * 60 * 24 * 7
app = typer.Typer()

def fetch_templates_from_github():
    url = "https://api.github.com/repos/github/gitignore/git/trees/main?recursive=1"
    response = requests.get(url).json()
    templates = []
    for item in response["tree"]:
        if item["path"].endswith(".gitignore") and not item["path"].count("/") >= 1:
            templates.append(item["path"].removesuffix(".gitignore"))

    return templates

def initialize():
    config = {}
    config["last_updated"] = time()
    config['all_templates_list'] = fetch_templates_from_github()
    choices = inquirer.fuzzy(message="Choose the language for the template: ", choices=config['all_templates_list'], multiselect=True,).execute()
    for choice in choices:
        with open(CACHE_FOLDER / f"{choice}.gitignore", "w") as f:
            response = requests.get(f"https://raw.githubusercontent.com/github/gitignore/refs/heads/main/{choice}.gitignore")
            f.write(response.text)
            f.close()
    config["selected_templates"] = sorted(choices)
    config["custom_templates"] = []
    with open(CACHE_CONFIG_FILE, "w") as f:
        json.dump(config, f)
    print(f"Config and template initalized to {CACHE_FOLDER}. You can now use the tool to fetch templates from the cache or from the Gitignore repository.")

def ensure_initialized():
    if not CACHE_CONFIG_FILE.exists():
        should_init = inquirer.confirm(message="The tool hasn't been initialized yet. Initialize now?", default=True).execute()
        if not should_init:
            typer.echo("Cannot continue without initialization.")
            raise typer.Exit(code=1)
        initialize()





def add_template_to_cache(name: str, content: str, list_key: str):
    """Write a template to the cache and register it in the config, confirming before overwrite."""
    target = CACHE_FOLDER / f"{name}.gitignore"
    if target.exists():
        overwrite = inquirer.confirm(message=f"A template named '{name}' already exists. Overwrite it?", default=False).execute()
        if not overwrite:
            print("Import cancelled.")
            raise typer.Exit(code=1)

    with open(target, "w") as f:
        f.write(content)

    with open(CACHE_CONFIG_FILE, "r") as f:
        config = json.load(f)
    if name not in config[list_key]:
        config[list_key].append(name)
        config[list_key] = sorted(config[list_key])
    with open(CACHE_CONFIG_FILE, "w") as f:
        json.dump(config, f)
    print(f"Imported '{name}' template.")


def retrieve_template(lang: str, config = None):
    if config is None:
        with open(CACHE_CONFIG_FILE, "r") as f:
            config = json.load(f)
    if lang in config["selected_templates"] or lang in config["custom_templates"]:
        copyfile(CACHE_FOLDER / f"{lang}.gitignore", ".gitignore")
        # print(f"Initialized .gitignore with {lang} template.")
        return True
    
    response = requests.get(f"https://raw.githubusercontent.com/github/gitignore/refs/heads/main/{lang}.gitignore")
    if response.text == "404: Not Found":
        # print(f"Couldn't find a template for {lang}")
        return False
    with open(".gitignore", "w") as f:
        f.write(response.text)
        f.close()
    # print(f"Initialized .gitignore with {lang} template.")
    return True



@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    ensure_initialized()
    if ctx.invoked_subcommand is None:
        with open(CACHE_CONFIG_FILE, "r") as f:
            config = json.load(f)
        other_controls = ["View All", "Add a new template (Repository or Custom)"]
        choice = inquirer.fuzzy(message="Choose the language for the template: ", choices=config["selected_templates"]+config["custom_templates"]+other_controls).execute()
        if choice == "View All":
            choice = inquirer.fuzzy(message="Choose the language for the template: ", choices=config["custom_templates"]+config["all_templates_list"]).execute()
        if choice == "Add a new template (Repository or Custom)":
            import_main(ctx)
            return
        if retrieve_template(choice):
            print(f"Initialized .gitignore with {choice} template.")
        else:
            print(f"Couldn't find a template for {choice}")
            raise typer.Exit(code=1)



@app.command(name="add")
def fetch(name: str):
    """Add a .gitignore template to the project."""
    if retrieve_template(name):
        print(f"Initialized .gitignore with {name} template.")
    else:
        print(f"Couldn't find a template for {name}")
        raise typer.Exit(code=1)

    
@app.command(name="init")
def init():
    """Initialize the tool by fetching all templates and storing them in a cache."""
    initialize()

@app.command(name="update")
def update():
    """Update the cache with the latest templates from GitIgnore repository."""
    with open(CACHE_CONFIG_FILE, "r") as f:
        config = json.load(f)
    config["last_updated"] = time()
    config['all_templates_list'] = fetch_templates_from_github()
    with open(CACHE_CONFIG_FILE, "w") as f:
        json.dump(config, f)
    print("Cache updated successfully.")

@app.command(name="list")
def list_templates():
    """List all templates in the cache."""
    with open(CACHE_CONFIG_FILE, "r") as f:
        config = json.load(f)
    if len(config["selected_templates"]) + len(config["custom_templates"]) == 0:
        print("No templates in the cache.")
        raise typer.Exit(code=1)
    if len(config["selected_templates"]) > 0:
        print("Selected templates:")
        for template in config["selected_templates"]:
            print(f"  - {template}")
    if len(config["custom_templates"]) > 0:
        print("\nCustom templates:")
        for template in config["custom_templates"]:
            print(f"  - {template}")

@app.command(name="delete")
def delete(name: str):
    """Delete a template from the cache.!"""
    target = CACHE_FOLDER / f"{name}.gitignore"
    if not target.exists():
        print(f"No template named '{name}' was found in the cache.")
        raise typer.Exit(code=1)
    confirm = inquirer.confirm(message=f"Are you sure you want to delete the template '{name}'?", default=False).execute()
    if not confirm:
        print("Deletion cancelled.")
        raise typer.Exit(code=1)
    target.unlink()
    with open(CACHE_CONFIG_FILE, "r") as f:
        config = json.load(f)
    if name in config["selected_templates"]:
        config["selected_templates"].remove(name)
    if name in config["custom_templates"]:
        config["custom_templates"].remove(name)
    with open(CACHE_CONFIG_FILE, "w") as f:
        json.dump(config, f)
    print(f"Template '{name}' deleted successfully.")

import_app = typer.Typer(invoke_without_command=True)
app.add_typer(import_app, name="import")

@import_app.callback(invoke_without_command=True)
def import_main(ctx: typer.Context):
    """Import a .gitignore template from the repo list or a custom file."""
    if ctx.invoked_subcommand is not None:
        return
    choice = inquirer.select(message="Import from:", choices=["Repository template", "Custom file"]).execute()
    if choice == "Repository template":
        with open(CACHE_CONFIG_FILE, "r") as f:
            config = json.load(f)
        name = inquirer.fuzzy(message="Choose a template to import: ", choices=config["all_templates_list"]).execute()
        import_repo(name)
    else:
        path = inquirer.filepath(message="Path to the .gitignore file: ").execute()
        name = inquirer.text(message="Name for the template: ").execute()
        import_custom(path, name)

@import_app.command(name="--repo")
def import_repo(name: str):
    """Import a template from the GitHub gitignore repo."""
    response = requests.get(f"https://raw.githubusercontent.com/github/gitignore/refs/heads/main/{name}.gitignore")
    if response.text == "404: Not Found":
        print(f"Couldn't find a template for {name}")
        raise typer.Exit(code=1)
    add_template_to_cache(name, response.text, "selected_templates")
    
@import_app.command(name="--custom")
def import_custom(path: str, name: str):
    """Import a custom .gitignore file under a given name."""
    content = Path(path).read_text()
    add_template_to_cache(name, content, "custom_templates")