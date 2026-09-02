"""
Bulk-generate/update ci-config.yml จาก fabric_items/ จริงในเครื่อง — ใช้ตอน onboard
item จำนวนมาก (หลักร้อย) เข้า pattern-based CI ครั้งแรก โดยไม่ให้ CI พังทันทีทั้งหมด

หลักการ (evidence-based, ไม่เดา):
  1. หา fabric_type จาก suffix ของ folder (.Notebook / .DataPipeline / .Lakehouse / ...)
  2. เช็คว่ามีไฟล์ evidence รองรับ pattern ไหนอยู่แล้วจริง:
       - tests/unit/test_<name>.py               -> unit_test
       - great_expectations/checkpoints/dq_<name>.yml -> data_quality
       - shared script (structure/schema) + _defaults ระบุ pattern นั้นให้ type นี้ -> ใช้ pattern นั้นได้เลย
         (structure/schema ไม่ต้องมีไฟล์ต่อ item เพราะใช้ script กลาง)
  3. ถ้าไม่มี evidence รองรับเลย (pattern ที่ต้องมีไฟล์เฉพาะ แต่ยังไม่มีใครเขียน)
       -> ใส่ skip_check: true + skip_reason อัตโนมัติ ("bulk onboarding ...")
       เพื่อให้ CI ไม่พังทันทีตอน onboard วันแรก แต่ยังเห็นชัดว่าเป็นหนี้ทางเทคนิคที่ต้องเคลียร์
  4. ไม่แตะ entry ที่มีอยู่แล้วใน ci-config.yml เดิม (merge, ไม่ overwrite)
  5. ไม่แตะ _defaults block เดิม

ใช้:
    python scripts/generate_ci_config.py            # เขียนทับ ci-config.yml จริง
    python scripts/generate_ci_config.py --dry-run  # print ผลลัพธ์ดูก่อน ไม่เขียนไฟล์
"""

import argparse
import io
import os
import sys
from datetime import date

import yaml

# กัน console บน Windows แสดงภาษาไทยเพี้ยน (cp874 default) — ไม่กระทบตอนรันบน Linux/GitHub Actions
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(BASE_DIR, "..")
FABRIC_ITEMS_DIR = os.path.join(REPO_ROOT, "fabric_items")
CI_CONFIG_PATH = os.path.join(REPO_ROOT, "ci-config.yml")
TESTS_UNIT_DIR = os.path.join(REPO_ROOT, "tests", "unit")
GE_CHECKPOINTS_DIR = os.path.join(REPO_ROOT, "great_expectations", "checkpoints")

# pattern ที่ "ต้องมีไฟล์เฉพาะต่อ item" ถึงจะใช้ default ของ type นั้นได้เลย
# structure/schema ไม่อยู่ในนี้เพราะใช้ script กลาง ไม่ต้องมีไฟล์ต่อ item
PATTERNS_NEEDING_EVIDENCE = {"unit_test", "data_quality"}


def load_yaml(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def list_fabric_items():
    items = []
    for entry in sorted(os.listdir(FABRIC_ITEMS_DIR)):
        full_path = os.path.join(FABRIC_ITEMS_DIR, entry)
        if not os.path.isdir(full_path):
            continue  # ข้าม parameter.yml และไฟล์อื่นที่ไม่ใช่ item folder
        if "." not in entry:
            continue
        name, fabric_type = entry.rsplit(".", 1)
        items.append((name, fabric_type))
    return items


def has_unit_test(name):
    return os.path.exists(os.path.join(TESTS_UNIT_DIR, f"test_{name}.py"))


def has_dq_checkpoint(name):
    return os.path.exists(os.path.join(GE_CHECKPOINTS_DIR, f"dq_{name}.yml"))


def decide_entry(name, fabric_type, defaults, existing_entry, today_str):
    """คืนค่า (entry_dict_or_None, note) — None แปลว่าไม่ต้องเขียน entry (ใช้ default ได้เลย)"""

    if existing_entry is not None:
        return None, "already in ci-config.yml — skipped (not overwritten)"

    default_check = defaults.get(fabric_type)

    if default_check is None:
        # ไม่มี default ให้ type นี้เลย -> fallback ปกติคือ unit_test (fail-safe เข้มสุด)
        default_check = "unit_test"

    if default_check not in PATTERNS_NEEDING_EVIDENCE:
        # structure / schema / none -> ใช้ script กลาง ไม่ต้องมีไฟล์ต่อ item เลย
        return None, f"uses shared script for '{default_check}' — no entry needed"

    if default_check == "unit_test" and has_unit_test(name):
        return None, "unit test file already exists — default applies cleanly"

    if default_check == "data_quality" and has_dq_checkpoint(name):
        return None, "data quality checkpoint already exists — default applies cleanly"

    # ไม่มี evidence รองรับ default ที่ต้องมีไฟล์เฉพาะ -> skip ไว้ก่อน ไม่ให้ CI พังทันที
    entry = {
        "skip_check": True,
        "skip_reason": (
            f"Bulk onboarding {today_str} — ยังไม่มี "
            f"{'unit test' if default_check == 'unit_test' else 'data quality checkpoint'} "
            f"ให้ item นี้ ต้องเขียนเพิ่มแล้วเอา skip_check ออก"
        ),
    }
    return entry, f"no evidence for '{default_check}' — marked skip_check (needs follow-up)"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="แสดงผลลัพธ์ ไม่เขียนไฟล์จริง")
    args = parser.parse_args()

    config = load_yaml(CI_CONFIG_PATH)
    defaults = config.get("_defaults", {})
    today_str = date.today().isoformat()

    items = list_fabric_items()
    added, skipped_existing, using_default = [], [], []

    for name, fabric_type in items:
        existing_entry = config.get(name)
        entry, note = decide_entry(name, fabric_type, defaults, existing_entry, today_str)

        if entry is not None:
            config[name] = entry
            added.append((name, fabric_type, note))
        elif existing_entry is not None:
            skipped_existing.append((name, fabric_type, note))
        else:
            using_default.append((name, fabric_type, note))

    print(f"พบ item ทั้งหมด: {len(items)}")
    print(f"  - ใช้ _defaults ได้เลย (ไม่ต้องเขียน entry): {len(using_default)}")
    print(f"  - มี entry อยู่แล้ว ไม่แตะ: {len(skipped_existing)}")
    print(f"  - เพิ่ม entry ใหม่ (ส่วนใหญ่เป็น skip_check รอเติม test): {len(added)}")
    print()

    if added:
        print("=== Entry ใหม่ที่เพิ่ม (ต้องตามไปเขียน test จริงทีหลัง) ===")
        for name, fabric_type, note in added:
            print(f"  [{fabric_type}] {name}: {note}")
        print()

    if not added:
        print("ไม่มี entry ใหม่ต้องเพิ่ม — ไม่แตะไฟล์เลย (กัน comment ในไฟล์เดิมหาย)")
        return

    new_entries = {name: entry for name, _fabric_type, _note in added for entry in [config[name]]}
    appended_yaml = yaml.dump(new_entries, allow_unicode=True, sort_keys=False, default_flow_style=False)

    if args.dry_run:
        print("--dry-run: ไม่เขียนไฟล์จริง — นี่คือส่วนที่จะต่อท้ายไฟล์เดิม:")
        print()
        print(appended_yaml)
        return

    # ต่อท้ายไฟล์เดิมเป็น text แทนการ yaml.dump ทั้งไฟล์ใหม่ — กัน comment ในไฟล์เดิมหายไปหมด
    # (yaml.dump ไม่ preserve comment เลย ถ้า load ทั้งไฟล์มาแล้ว dump ทับ)
    with open(CI_CONFIG_PATH, "a", encoding="utf-8") as f:
        f.write(f"\n# --- เพิ่มโดย generate_ci_config.py ({today_str}) ---\n")
        f.write(appended_yaml)

    print(f"ต่อท้าย {CI_CONFIG_PATH} เรียบร้อย ({len(added)} entries ใหม่)")


if __name__ == "__main__":
    sys.exit(main())
