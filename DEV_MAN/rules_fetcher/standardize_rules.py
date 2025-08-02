import os
from loguru import logger

RULES_DIR = os.path.join(os.path.dirname(__file__), "rules")
REPORT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "standardization_report.md")
CURSORRULES_TEMPLATE = '''---
description: <ADD DESCRIPTION>
globs: 
alwaysApply: true
---
'''

HEADER_KEYS = ["---", "description:", "globs:", "alwaysApply:"]

def has_modern_header(text):
    # Check for all required header keys
    return all(key in text for key in HEADER_KEYS)

def standardize_rule_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if has_modern_header(content):
        return False, content  # Already standardized
    # Add template header at the top
    new_content = CURSORRULES_TEMPLATE + content
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True, new_content

def main():
    logger.info(f"Checking all .cursorrules files in {RULES_DIR} for modern Cursor rules header...")
    rule_files = [f for f in os.listdir(RULES_DIR) if f.endswith(".cursorrules")]
    standardized = []
    already_standard = []
    for rule_file in rule_files:
        path = os.path.join(RULES_DIR, rule_file)
        changed, _ = standardize_rule_file(path)
        if changed:
            logger.success(f"Standardized header added to {rule_file}")
            standardized.append(rule_file)
        else:
            already_standard.append(rule_file)
    # Write report
    with open(REPORT_PATH, "w", encoding="utf-8") as report:
        report.write("# Rule Standardization Report\n\n")
        report.write("## Standardized (header added):\n")
        for f in standardized:
            report.write(f"- {f}\n")
        report.write("\n## Already Standard:\n")
        for f in already_standard:
            report.write(f"- {f}\n")
    logger.success(f"Standardization report written to {REPORT_PATH}")

if __name__ == "__main__":
    main() 