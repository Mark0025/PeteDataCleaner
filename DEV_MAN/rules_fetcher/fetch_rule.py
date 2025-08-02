import os
import requests
from loguru import logger

RULES_BASE_URL = "https://raw.githubusercontent.com/PatrickJS/awesome-cursorrules/main/rules/"
LOCAL_RULES_DIR = os.path.join(os.path.dirname(__file__), "rules")

RULES_MAP = {
    "Python Best Practices": "python-best-practices-cursorrules-prompt-file/cursorrules.mdc",
    "Python Developer": "python-developer-cursorrules-prompt-file/cursorrules.mdc",
    "Python Projects Guide": "python-projects-guide-cursorrules-prompt-file/cursorrules.mdc",
}

def fetch_rule(rule_name):
    if rule_name not in RULES_MAP:
        logger.error(f"Rule '{rule_name}' not found in RULES_MAP.")
        return False
    rule_path = RULES_MAP[rule_name]
    url = RULES_BASE_URL + rule_path
    logger.info(f"Fetching rule '{rule_name}' from {url}")
    response = requests.get(url)
    if response.status_code == 200:
        os.makedirs(LOCAL_RULES_DIR, exist_ok=True)
        local_path = os.path.join(LOCAL_RULES_DIR, f"{rule_name.replace(' ', '_').lower()}.mdc")
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(response.text)
        logger.success(f"Rule '{rule_name}' saved to {local_path}")
        return True
    else:
        logger.error(f"Failed to fetch rule '{rule_name}'. Status code: {response.status_code}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python fetch_rule.py 'Rule Name'")
        exit(1)
    rule_name = sys.argv[1]
    fetch_rule(rule_name) 