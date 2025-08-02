import requests
from lxml import html
from loguru import logger

README_URL = "https://raw.githubusercontent.com/PatrickJS/awesome-cursorrules/main/README.md"
RAW_BASE = "https://raw.githubusercontent.com/PatrickJS/awesome-cursorrules/main/"


def download_readme():
    logger.info(f"Downloading README from {README_URL}")
    response = requests.get(README_URL)
    if response.status_code == 200:
        logger.success("README downloaded successfully.")
        return response.text
    else:
        logger.error(f"Failed to download README. Status code: {response.status_code}")
        return None


def parse_rules_from_readme(readme_text, debug_html=False):
    # Convert Markdown to HTML for lxml parsing
    try:
        import markdown
        html_text = markdown.markdown(readme_text)
    except ImportError:
        logger.error("Please install the 'markdown' package: uv pip install markdown")
        return {}
    if debug_html:
        print("\n--- GENERATED HTML ---\n")
        print(html_text)
        print("\n--- END GENERATED HTML ---\n")
    tree = html.fromstring(html_text)
    rules = {}
    # Find all <a> tags with .cursorrules, .md, or .mdc links
    for a in tree.xpath('//a'):
        rule_link = a.get('href')
        rule_name = a.text_content().strip()
        if rule_link and (rule_link.endswith('.cursorrules') or rule_link.endswith('.md') or rule_link.endswith('.mdc')):
            # Normalize relative links to full raw GitHub URLs
            if rule_link.startswith('./'):
                rule_link_full = RAW_BASE + rule_link[2:]
            elif rule_link.startswith('/'):
                rule_link_full = RAW_BASE + rule_link[1:]
            elif rule_link.startswith('http'):
                rule_link_full = rule_link
            else:
                rule_link_full = RAW_BASE + rule_link
            rules[rule_name] = rule_link_full
    logger.success(f"Extracted {len(rules)} rules from README.")
    return rules


def get_rule_links(debug_html=False):
    readme = download_readme()
    if not readme:
        return {}
    return parse_rules_from_readme(readme, debug_html=debug_html)

if __name__ == "__main__":
    rules = get_rule_links(debug_html=False)
    for name, link in rules.items():
        print(f"{name}: {link}") 