import os
import re
from loguru import logger

RULES_DIR = os.path.join(os.path.dirname(__file__), 'rules')
REPORT_PATH = os.path.join(os.path.dirname(__file__), '..', 'description_update_report.md')

DESCRIPTION_MAP = {
    "python_best_practices.cursorrules": "Best practices for Python development, including structure, testing, typing, and AI-friendly code.",
    "python_developer.cursorrules": "Guidelines for elite Python developers, focusing on CLI tools, debugging, and performance.",
    "python_projects_guide.cursorrules": "Comprehensive guide for structuring, testing, and maintaining Python projects.",
}

def infer_globs(fname, desc):
    # If filename or description contains 'python', set globs: .py**
    if 'python' in fname.lower() or 'python' in desc.lower():
        return '.py**'
    # Add more language/tech inference here as needed
    return ''

def update_description_and_globs(filepath, new_description):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    desc_updated = False
    globs_updated = False
    desc_found = False
    globs_found = False
    for i, line in enumerate(lines):
        if line.strip().startswith('description:'):
            desc_found = True
            if '<ADD DESCRIPTION>' in line or line.strip() == 'description:':
                lines[i] = f'description: {new_description}\n'
                desc_updated = True
        if line.strip().startswith('globs:'):
            globs_found = True
            # Only update if empty or placeholder
            if line.strip() == 'globs:' or line.strip() == 'globs: ':
                inferred_glob = infer_globs(os.path.basename(filepath), new_description)
                if inferred_glob:
                    lines[i] = f'globs: {inferred_glob}\n'
                    globs_updated = True
    # If not found, insert after the first '---'
    if not desc_found:
        for i, line in enumerate(lines):
            if line.strip() == '---':
                lines.insert(i+1, f'description: {new_description}\n')
                desc_updated = True
                break
    if not globs_found:
        for i, line in enumerate(lines):
            if line.strip() == '---':
                inferred_glob = infer_globs(os.path.basename(filepath), new_description)
                if inferred_glob:
                    lines.insert(i+2, f'globs: {inferred_glob}\n')
                    globs_updated = True
                break
    return lines, desc_updated, globs_updated

def main():
    logger.add(REPORT_PATH, level="INFO")
    logger.info(f"Scanning {RULES_DIR} for .cursorrules files...")
    updated = []
    skipped = []
    globs_changed = []
    for fname in os.listdir(RULES_DIR):
        if fname.endswith('.cursorrules'):
            fpath = os.path.join(RULES_DIR, fname)
            desc = DESCRIPTION_MAP.get(fname)
            if not desc:
                # Fallback: use first non-header, non-empty line as summary
                with open(fpath, 'r', encoding='utf-8') as f:
                    content = f.read()
                match = re.search(r'---\s*(.*?)\s*---', content, re.DOTALL)
                after_header = content[match.end():] if match else content
                for line in after_header.splitlines():
                    if line.strip():
                        desc = line.strip()[:100]
                        break
                else:
                    desc = "No description available."
            new_lines, desc_changed, globs_changed_flag = update_description_and_globs(fpath, desc)
            if desc_changed or globs_changed_flag:
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                logger.success(f"Updated {fname}: description {'changed' if desc_changed else 'unchanged'}, globs {'changed' if globs_changed_flag else 'unchanged'}")
                updated.append(fname)
                if globs_changed_flag:
                    globs_changed.append(fname)
            else:
                logger.info(f"Skipped {fname} (already has description and globs)")
                skipped.append(fname)
    logger.info(f"Update complete. Updated: {updated}, Skipped: {skipped}, Globs changed: {globs_changed}")
    # Write summary report
    with open(REPORT_PATH, 'a', encoding='utf-8') as f:
        f.write("\n# Description & Globs Update Report\n")
        f.write(f"\n## Updated Files\n- " + "\n- ".join(updated) + "\n")
        f.write(f"\n## Skipped Files\n- " + "\n- ".join(skipped) + "\n")
        f.write(f"\n## Globs Changed\n- " + "\n- ".join(globs_changed) + "\n")

if __name__ == "__main__":
    main() 