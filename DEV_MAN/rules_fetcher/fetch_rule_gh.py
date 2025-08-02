import os
import subprocess
import pandas as pd
import requests
from loguru import logger

RULES = [
    "Python Best Practices",
    "Python Developer",
    "Python Projects Guide"
]

RULE_KEYWORDS = {
    "Python Best Practices": "python-best-practices",
    "Python Developer": "python-developer",
    "Python Projects Guide": "python-projects-guide"
}

REPO = "PatrickJS/awesome-cursorrules"
RAW_BASE = "https://raw.githubusercontent.com/PatrickJS/awesome-cursorrules/main/rules/"
LOCAL_RULES_DIR = os.path.join(os.path.dirname(__file__), "rules")


def get_repo_file_list():
    logger.info("Listing files in repo using GitHub CLI...")
    result = subprocess.run([
        "gh", "repo", "clone", REPO, "--", "--depth=1", "--filter=blob:none", "--no-checkout"
    ], capture_output=True, text=True)
    # Use gh api to list files instead of clone for efficiency
    api_result = subprocess.run([
        "gh", "api", f"repos/{REPO}/git/trees/main?recursive=1", "--jq", ".tree[].path"
    ], capture_output=True, text=True)
    if api_result.returncode != 0:
        logger.error(f"Failed to list files: {api_result.stderr}")
        return []
    files = api_result.stdout.strip().split("\n")
    logger.success(f"Found {len(files)} files in repo.")
    return files


def find_rule_paths(files):
    logger.info("Searching for rule files matching requested rules...")
    df = pd.DataFrame(files, columns=["path"])
    rule_paths = {}
    for rule, keyword in RULE_KEYWORDS.items():
        match = df[df["path"].str.contains(keyword) & df["path"].str.endswith("cursorrules.mdc")]
        if not match.empty:
            rule_paths[rule] = match.iloc[0]["path"]
            logger.success(f"Found rule '{rule}' at {rule_paths[rule]}")
        else:
            logger.error(f"Rule '{rule}' not found in repo.")
    return rule_paths


def fetch_and_save_rule(rule, path):
    url = RAW_BASE + path
    logger.info(f"Downloading rule '{rule}' from {url}")
    response = requests.get(url)
    if response.status_code == 200:
        os.makedirs(LOCAL_RULES_DIR, exist_ok=True)
        local_path = os.path.join(LOCAL_RULES_DIR, f"{rule.replace(' ', '_').lower()}.mdc")
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(response.text)
        logger.success(f"Rule '{rule}' saved to {local_path}")
    else:
        logger.error(f"Failed to download rule '{rule}'. Status code: {response.status_code}")


def main():
    files = get_repo_file_list()
    if not files:
        logger.error("No files found in repo. Exiting.")
        return
    rule_paths = find_rule_paths(files)
    for rule, path in rule_paths.items():
        fetch_and_save_rule(rule, path)

if __name__ == "__main__":
    main() 