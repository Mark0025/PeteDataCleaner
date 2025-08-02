# Plan: Rules Fetcher Utility

**Version:** v0.7

---

## Changelog

- **v0.1:** Initial plan for rules fetcher utility (fetch by static mapping, direct download).
- **v0.2:** Updated to use GitHub CLI and pandas for dynamic rule discovery and fetching. Added changelog, versioning, and rationale for changes.
- **v0.3:** Improve repo parsing logic to handle cases where rule names do not directly match file or folder names. Add fuzzy matching and/or parse README/index files for better rule discovery.
- **v0.4:** New approach: parse the README for rule names and links, then fetch the corresponding .md or .mdc files. This leverages the curated list in the README for more accurate rule discovery.
- **v0.5:** Integrate rule file downloading and local saving after extracting links from the README. Mark README parsing and link extraction as complete.
- **v0.6:** Log what worked (README download, Markdown to HTML conversion) and what did not (rule extraction, due to README structure). Next: debug and improve rule extraction logic.
- **v0.7:** Add next steps for rule comparison utility, rule application/integration, further automation (CLI/UI), and documentation. Incremented version and updated status.

---

## Why This Version (v0.7)?

- The rule fetcher utility is now able to fetch and save rules by name. The next step is to add value by comparing, integrating, and automating rule management, and documenting the workflow for future use.

---

## What Worked

- Downloading the README from the repo.
- Converting the README from Markdown to HTML using the `markdown` package.

## What Did Not Work

- Extracting rule names and links: The XPath `//li[a]` did not match any elements, resulting in 0 rules found. The README structure may use a different format (e.g., tables, nested lists, or direct links).

---

## Steps

- [x] Scaffold `rules_fetcher/` module in DEV_MAN
- [x] Add dependencies: `requests`, `loguru`, `pandas`, `lxml`, `markdown`
- [x] Download and parse the README from the repo
- [x] Convert README from Markdown to HTML
- [x] Debug HTML structure and update rule extraction logic
- [x] Match requested rule names to README entries
- [x] Download and save the rule files
- [x] Validate/convert to .mdc if needed
- [x] Log all actions
- [x] Test fetching:
  - [x] Python Best Practices
  - [x] Python Developer
  - [x] Python Projects Guide
- [ ] **Rule Comparison Utility:**
  - [ ] Build a script to compare all fetched rules for overlap, contradictions, or gaps.
  - [ ] Output a markdown report in DEV_MAN for review.
- [ ] **Rule Application/Integration:**
  - [ ] Optionally, automate copying or merging these rules into your project’s `.cursorrules` or `.cursor/rules/` as needed.
- [ ] **Further Automation:**
  - [ ] Add a CLI or UI to let you search, preview, and fetch rules by keyword or description.
- [ ] **Documentation:**
  - [ ] Document this workflow in your DEV_MAN logs and README for future reference.

---

## Status

- **In Progress: Building rule comparison utility and planning further automation and documentation.**
