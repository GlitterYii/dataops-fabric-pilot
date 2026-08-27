"""
เรียกจาก fabric-ci.yml สำหรับ item type ที่ check=structure (เช่น DataPipeline)
เช็คว่า activity ที่อ้างอิงถึง item อื่น (notebookId ฯลฯ) มี item จริงใน fabric_items/ รองรับอยู่ไหม
ถ้า pipeline อ้างอิง logicalId ที่ไม่มี item ไหนใน repo ประกาศไว้ ถือว่า structure ผิด (dangling reference)
"""
import glob
import json
import os
import sys

# key ใน typeProperties ที่ถือว่าเป็นการอ้างอิงไปยัง item อื่น (เพิ่มได้เรื่อยๆ เมื่อเจอ activity type ใหม่)
REFERENCE_KEYS = ("notebookId", "dataflowId", "pipelineId")


def _load_known_logical_ids(repo_root: str) -> set:
    ids = set()
    for platform_file in glob.glob(os.path.join(repo_root, "fabric_items", "*", ".platform")):
        with open(platform_file, encoding="utf-8") as f:
            data = json.load(f)
        logical_id = data.get("config", {}).get("logicalId")
        if logical_id:
            ids.add(logical_id)
    return ids


def validate(item_path: str) -> bool:
    content_files = glob.glob(os.path.join(item_path, "*.json"))
    if not content_files:
        print(f"[validate_pipeline_structure] {item_path}: no content JSON found")
        return False

    repo_root = os.path.abspath(os.path.join(item_path, "..", ".."))
    known_ids = _load_known_logical_ids(repo_root)

    ok = True
    for content_file in content_files:
        with open(content_file, encoding="utf-8") as f:
            content = json.load(f)

        activities = content.get("properties", {}).get("activities", [])
        if not activities:
            print(f"[validate_pipeline_structure] {content_file}: pipeline has no activities")
            ok = False
            continue

        for activity in activities:
            type_props = activity.get("typeProperties", {})
            for key in REFERENCE_KEYS:
                ref_id = type_props.get(key)
                if ref_id is None:
                    continue
                if ref_id not in known_ids:
                    print(
                        f"[validate_pipeline_structure] {content_file}: "
                        f"activity '{activity.get('name')}' references {key}={ref_id} "
                        f"but no item in fabric_items/ has that logicalId"
                    )
                    ok = False
                else:
                    print(
                        f"[validate_pipeline_structure] {content_file}: "
                        f"activity '{activity.get('name')}' -> {key}={ref_id} OK"
                    )

    return ok


if __name__ == "__main__":
    item_path = sys.argv[1]
    if not validate(item_path):
        sys.exit(1)
