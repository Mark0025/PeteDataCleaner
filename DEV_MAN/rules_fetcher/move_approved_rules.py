import os
import shutil
import subprocess
from loguru import logger

SRC_DIR = os.path.join(os.path.dirname(__file__), 'rules')
DEST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.cursor', 'rules'))
REPORT_PATH = os.path.join(os.path.dirname(__file__), '..', 'move_rules_report.md')

def prompt_mode():
    while True:
        resp = input("Do you want to move all rules, or preview them first? [move/preview]: ").strip().lower()
        if resp in ("move", "preview"):
            return resp

def prompt_approve(rule):
    while True:
        resp = input(f"Approve move for {rule}? [y/n]: ").strip().lower()
        if resp in ("y", "n"):
            return resp == "y"

def prompt_overwrite(rule):
    while True:
        resp = input(f"{rule} already exists in destination. Overwrite? [y/n]: ").strip().lower()
        if resp in ("y", "n"):
            return resp == "y"

def preview_rule(filepath):
    while True:
        resp = input(f"Open {os.path.basename(filepath)} for preview? [y/n]: ").strip().lower()
        if resp == "y":
            subprocess.run(["open", filepath])
            break
        elif resp == "n":
            break

def move_rule(src, dest):
    shutil.move(src, dest)

def main():
    logger.add(REPORT_PATH, level="INFO")
    logger.info(f"Moving approved .cursorrules from {SRC_DIR} to {DEST_DIR}")
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)
        logger.info(f"Created destination directory: {DEST_DIR}")
    moved = []
    skipped = []
    overwritten = []
    rules = [f for f in os.listdir(SRC_DIR) if f.endswith('.cursorrules')]
    mode = prompt_mode()
    if mode == "move":
        print(f"Rules to move: {', '.join(rules)}")
        if prompt_approve("ALL rules listed above"):
            for fname in rules:
                src_path = os.path.join(SRC_DIR, fname)
                dest_path = os.path.join(DEST_DIR, fname)
                if os.path.exists(dest_path):
                    if prompt_overwrite(fname):
                        move_rule(src_path, dest_path)
                        logger.success(f"Overwrote and moved {fname}")
                        overwritten.append(fname)
                    else:
                        logger.info(f"Skipped {fname} (exists, not overwritten)")
                        skipped.append(fname)
                else:
                    move_rule(src_path, dest_path)
                    logger.success(f"Moved {fname}")
                    moved.append(fname)
        else:
            print("No rules moved.")
            logger.info("No rules moved (user declined ALL).")
    else:  # preview mode
        for fname in rules:
            src_path = os.path.join(SRC_DIR, fname)
            preview_rule(src_path)
            if prompt_approve(fname):
                dest_path = os.path.join(DEST_DIR, fname)
                if os.path.exists(dest_path):
                    if prompt_overwrite(fname):
                        move_rule(src_path, dest_path)
                        logger.success(f"Overwrote and moved {fname}")
                        overwritten.append(fname)
                    else:
                        logger.info(f"Skipped {fname} (exists, not overwritten)")
                        skipped.append(fname)
                else:
                    move_rule(src_path, dest_path)
                    logger.success(f"Moved {fname}")
                    moved.append(fname)
            else:
                logger.info(f"Skipped {fname} (not approved)")
                skipped.append(fname)
    logger.info(f"Move complete. Moved: {moved}, Overwritten: {overwritten}, Skipped: {skipped}")
    # Write summary report
    with open(REPORT_PATH, 'a', encoding='utf-8') as f:
        f.write("\n# Move Rules Report\n")
        f.write(f"\n## Moved Files\n- " + "\n- ".join(moved) + "\n")
        f.write(f"\n## Overwritten Files\n- " + "\n- ".join(overwritten) + "\n")
        f.write(f"\n## Skipped Files\n- " + "\n- ".join(skipped) + "\n")

if __name__ == "__main__":
    main() 