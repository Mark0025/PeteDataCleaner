import os
from loguru import logger
from collections import defaultdict

RULES_DIR = os.path.join(os.path.dirname(__file__), "rules")
REPORT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rules_comparison_report.md")


def read_rule_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def extract_key_points(text):
    # Naive extraction: split by lines, filter for lines that look like rules, requirements, or principles
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    key_points = [line for line in lines if (
        line.startswith("-") or
        line.startswith("*") or
        line[0:2].isdigit() or
        ":" in line or
        "should" in line.lower() or
        "must" in line.lower() or
        "always" in line.lower() or
        "never" in line.lower()
    )]
    return set(key_points)


def compare_rules():
    logger.info(f"Comparing all .cursorrules files in {RULES_DIR}")
    rule_files = [f for f in os.listdir(RULES_DIR) if f.endswith(".cursorrules")]
    rules_content = {f: read_rule_file(os.path.join(RULES_DIR, f)) for f in rule_files}
    rules_points = {f: extract_key_points(content) for f, content in rules_content.items()}

    # Build a reverse index: point -> [rule_files]
    point_index = defaultdict(list)
    for rule_file, points in rules_points.items():
        for point in points:
            point_index[point].append(rule_file)

    # Find overlaps (points in more than one rule)
    overlaps = {p: files for p, files in point_index.items() if len(files) > 1}
    # Find unique points (points in only one rule)
    unique_points = {p: files[0] for p, files in point_index.items() if len(files) == 1}

    # Naive contradiction detection: look for "should" vs "should not" or "must" vs "must not" in the same/similar point
    contradictions = []
    for p1 in point_index:
        for p2 in point_index:
            if p1 != p2 and p1.lower().replace("should not", "should").replace("must not", "must") == p2.lower().replace("should not", "should").replace("must not", "must"):
                if ("should not" in p1.lower() and "should" in p2.lower()) or ("must not" in p1.lower() and "must" in p2.lower()):
                    contradictions.append((p1, p2, point_index[p1], point_index[p2]))

    # Write report
    with open(REPORT_PATH, "w", encoding="utf-8") as report:
        report.write("# Rules Comparison Report\n\n")
        report.write("## Overlapping Points (appear in multiple rules)\n\n")
        for point, files in overlaps.items():
            report.write(f"- {point}\n  - Appears in: {', '.join(files)}\n")
        report.write("\n## Unique Points (appear in only one rule)\n\n")
        for point, file in unique_points.items():
            report.write(f"- {point}\n  - Only in: {file}\n")
        report.write("\n## Potential Contradictions\n\n")
        for p1, p2, files1, files2 in contradictions:
            report.write(f"- CONTRADICTION: '{p1}' <-> '{p2}'\n  - In: {', '.join(set(files1 + files2))}\n")
    logger.success(f"Rules comparison report written to {REPORT_PATH}")

if __name__ == "__main__":
    compare_rules() 