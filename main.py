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
        other_controls = ["View All"]
        choice = inquirer.fuzzy(message="Choose the language for the template: ", choices=config["selected_templates"]+config["custom_templates"]+other_controls).execute()
        if choice == "View All":
            choice = inquirer.fuzzy(message="Choose the language for the template: ", choices=config["custom_templates"]+config["all_templates_list"]).execute()
        if retrieve_template(choice):
            print(f"Initialized .gitignore with {choice} template.")
        else:
            print(f"Couldn't find a template for {choice}")
            raise typer.Exit(code=1)



@app.command(name="fetch")
def fetch(name: str):
    """Fetch a .gitignore template by name."""
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

if __name__ == "__main__":
    app()