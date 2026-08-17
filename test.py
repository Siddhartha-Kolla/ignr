import requests
import json

def fetch_templates_from_github():
    # url = "https://api.github.com/repos/github/gitignore/git/trees/main?recursive=1"
    # response = requests.get(url).json()
    # print(response)
    # with open("response.txt","w") as f:
    #     f.write(json.dumps(response))
    #     f.close()
    with open("response.json","r") as f:
        response = json.load(f)
    templates = []
    for item in response["tree"]:
        if item["path"].endswith(".gitignore") and not item["path"].count("/") >= 1:
            templates.append(item["path"].removesuffix(".gitignore"))

    return templates


s = fetch_templates_from_github()
print(s)