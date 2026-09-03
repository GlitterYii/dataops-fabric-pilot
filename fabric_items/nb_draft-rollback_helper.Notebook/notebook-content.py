# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "a7654c8c-f870-4bb7-8a88-fe3866b9c2a9",
# META       "default_lakehouse_name": "lh_test_lakehouse",
# META       "default_lakehouse_workspace_id": "7a829f6b-4fd1-45c7-8c8e-b7c317816e4b",
# META       "known_lakehouses": [
# META         {
# META           "id": "a7654c8c-f870-4bb7-8a88-fe3866b9c2a9"
# META         }
# META       ]
# META     }
# META   }
# META }

# PARAMETERS CELL ********************

# ===== Cell 1 — Parameters (toggle เป็น Parameter Cell ใน Fabric UI) =====
table_name = "lh_test_lakehouse.dbo.sales_raw"
control_lakehouse = "lh_test_lakehouse"          # lakehouse ที่จะเก็บ log การ rollback
target_version = None                            # ปล่อย None = auto ถอยกลับ 1 version หรือใส่เลขเจาะจง เช่น 12 ถ้ารู้ค่าที่ต้องการแล้ว
confirm_table_name = "lh_test_lakehouse.dbo.sales_raw"                          # <-- ต้องพิมพ์ชื่อตารางด้านบนซ้ำตรงนี้ให้ตรงเป๊ะก่อนกด Run all ไม่งั้น cell 4 จะ raise error กันไว้

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, lit
from delta.tables import DeltaTable

spark = SparkSession.builder.getOrCreate()

if confirm_table_name.strip() != table_name:
    raise RuntimeError(
        "confirm_table_name ที่ Cell 1 ไม่ตรงกับ table_name (หรือยังไม่ได้กรอก) "
        "— ยกเลิกการรันทั้งหมดเพื่อความปลอดภัย แก้ Cell 1 แล้วรันใหม่"
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# ===== Cell 3 — ดึงประวัติ version ทั้งหมดของตาราง (รันเสมอ ไว้ดูใน log/output) =====
# DESCRIBE HISTORY คืน version ใหม่สุดมาก่อน (DESC) อยู่แล้ว — ไม่ต้อง sort เอง
history_df = spark.sql(f"DESCRIBE HISTORY {table_name}")
history_rows = (
    history_df
    .select("version", "timestamp", "operation")
    .orderBy(col("version").desc())
    .collect()
)

if not history_rows:
    raise RuntimeError(f"ไม่พบประวัติของตาราง {table_name} — เช็คชื่อตารางอีกครั้ง")

current_version = history_rows[0]["version"]

print(f"\nประวัติของตาราง {table_name} (ล่าสุดอยู่บนสุด, เจอทั้งหมด {len(history_rows)} version):\n")
print(f"{'#':<4}{'version':<10}{'timestamp':<28}{'operation':<28}{'หมายเหตุ'}")
for idx, row in enumerate(history_rows):
    note = "← CURRENT (เวอร์ชันปัจจุบัน)" if row["version"] == current_version else ""
    print(f"{idx:<4}{row['version']:<10}{str(row['timestamp']):<28}{row['operation']:<28}{note}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# ===== Cell 4 — ตัดสิน target_version (auto หรือตามที่ระบุใน Cell 1) แล้วรัน restore ต่อรวด =====
# หมายเหตุสำคัญ: version เรียงลำดับตามเวลาที่เขียนจริง ไม่ใช่ "เลขน้อย = เก่ากว่าเสมอ"
# ไปเดาว่า index 0 ใน list คือของถูกต้องโดยไม่เช็ค operation/timestamp อาจกู้ผิดตัว
# (พบจริงตอนทดสอบ 2026-08-28 — ดู section 16 ของ DataOps-CICD-Workflow.md)
if len(history_rows) < 2:
    raise RuntimeError(f"{table_name} มีแค่ version เดียว ไม่มี version ก่อนหน้าให้ rollback กลับไป")

if target_version is None:
    selected = history_rows[1]              # ก่อนหน้า current 1 ก้าว (ตามลำดับเวลา ไม่ใช่ลบเลข current -1 เอง)
    target_version = selected["version"]
    print(f"\ntarget_version ไม่ได้ระบุ → auto เลือก version ก่อนหน้า current 1 ก้าว: version {target_version}")
else:
    matches = [row for row in history_rows if row["version"] == target_version]
    if not matches:
        raise RuntimeError(f"ไม่พบ version {target_version} ใน history ของ {table_name} — เช็ค list ด้านบนอีกครั้ง")
    selected = matches[0]

if target_version == current_version:
    raise RuntimeError("target_version ตรงกับ version ปัจจุบันอยู่แล้ว ไม่มีอะไรต้อง restore")

print(f"\nกำลังจะ RESTORE {table_name}")
print(f"  จาก version {current_version} (ปัจจุบัน)")
print(f"  ไปเป็น  version {target_version} (เขียนเมื่อ {selected['timestamp']}, operation={selected['operation']})")

spark.sql(f"RESTORE TABLE {table_name} TO VERSION AS OF {target_version}")
print(f"\nRestore สำเร็จ: {table_name} กลับไปที่ version {target_version} แล้ว")

try:
    import notebookutils
    executed_by = notebookutils.runtime.context.get("userId", "unknown")
except Exception:
    executed_by = "unknown"

log_row = spark.createDataFrame([{
    "table_name": table_name,
    "executed_by": executed_by,
    "from_version": current_version,
    "to_version": target_version,
    "to_version_timestamp": str(selected["timestamp"]),
    "to_version_operation": selected["operation"],
}]).withColumn("restored_at", current_timestamp())

(log_row.write
    .format("delta")
    .mode("append")
    .option("mergeSchema", "true")
    .saveAsTable(f"{control_lakehouse}.dbo.rollback_incident_log")
)

print(f"บันทึก log ลง {control_lakehouse}.dbo.rollback_incident_log แล้ว")
print(
    "\nขั้นตอนต่อไป (runbook เต็มอยู่ที่ section 16 ของ DataOps-CICD-Workflow.md ข้อ 6-9):\n"
    "  6. เช็ค row count / spot-check ค่าสำคัญเทียบกับที่คาดไว้\n"
    "  7. แจ้ง downstream owner ที่ query ตารางนี้ต่อ ให้ refresh/re-validate\n"
    "  8. เปิด pipeline ที่หยุดไว้ตอนต้น ให้กลับมารันตามปกติ\n"
    "  9. บันทึก incident ลง section 14 หรือ incident log ของทีม (root cause, ตารางที่กระทบ, วิธีกู้คืนที่ใช้จริง)"
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
