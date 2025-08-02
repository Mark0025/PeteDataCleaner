import os
import requests
from loguru import logger
from readme_parser import get_rule_links

# List of rules to fetch
REQUESTED_RULES = [
    "Python Best Practices",
    "Python Developer",
    "Python Projects Guide"
]

LOCAL_RULES_DIR = os.path.join(os.path.dirname(__file__), "rules")


def fetch_and_save_rule(rule_name, url):
    logger.info(f"Downloading rule '{rule_name}' from {url}")
    response = requests.get(url)
    if response.status_code == 200:
        os.makedirs(LOCAL_RULES_DIR, exist_ok=True)
        # Use a safe filename
        safe_name = rule_name.replace(' ', '_').replace('/', '_').lower()
        local_path = os.path.join(LOCAL_RULES_DIR, f"{safe_name}.cursorrules")
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(response.text)
        logger.success(f"Rule '{rule_name}' saved to {local_path}")
    else:
        logger.error(f"Failed to download rule '{rule_name}'. Status code: {response.status_code}")


def main():
    rules = get_rule_links()
    for rule_name in REQUESTED_RULES:
        url = rules.get(rule_name)
        if url:
            fetch_and_save_rule(rule_name, url)
        else:
            logger.error(f"Rule '{rule_name}' not found in README.")

if __name__ == "__main__":
    main() 