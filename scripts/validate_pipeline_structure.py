"""
เรียกจาก fabric-ci.yml สำหรับ item type DataPipeline
เช็คว่า activity ที่อ้างอิงถึง item อื่น (Notebook, Dataflow) มีอยู่จริงใน fabric_items/
ยังไม่มี DataPipeline item ใน repo นี้ — เป็น placeholder รอเพิ่ม item ประเภทนี้จริง
"""
import sys


def validate(item_path: str) -> bool:
    print(f"[validate_pipeline_structure] checking {item_path} ... skipped (placeholder)")
    return True


if __name__ == "__main__":
    item_path = sys.argv[1]
    if not validate(item_path):
        sys.exit(1)
