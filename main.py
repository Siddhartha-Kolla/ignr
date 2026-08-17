import requests
import typer
from InquirerPy import inquirer

app = typer.Typer()

templates = ["Python", "Node", "Go", "Java", "Rust", "React","View All", "Add own template"]

def retrieve_template(lang: str):
    response = requests.get(f"https://raw.githubusercontent.com/github/gitignore/refs/heads/main/{lang}.gitignore")
    if response.text == "404: Not Found":
        return False
    with open(".gitignore", "w") as f:
        f.write(response.text)
        f.close()
    return True

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        choice = inquirer.fuzzy(message="Choose the language for the template: ", choices=templates).execute()
        retrieve_template(choice)

@app.command(name="fetch")
def fetch(name: str):
    retrieve_template(name)
    """Fetch a .gitignore template by name."""
    # pass


if __name__ == "__main__":
    app()