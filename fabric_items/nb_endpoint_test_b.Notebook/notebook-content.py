# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

# Test B (section 14 Phase 6): เขียนข้าม workspace เหมือน Test A แต่ Lakehouse ปลายทาง
# (lh_endpoint_test_b) authored ผ่าน Git Integration อิสระของตัวเอง ไม่ใช่ authored ใน
# spl-cicd-dev แบบ lh_endpoint_test_a — ดู DataOps-CICD-Workflow.md section 14 Phase 6
#
# เขียนผ่าน abfss:// path ตรงๆ (ไม่ใช้ default_lakehouse attach, ไม่ใช้ Copy Activity)
# เพื่อเลี่ยงบั๊ก Connection-permission เหมือน nb_endpoint_test
#
# ค่า 2 ตัวนี้เป็นของ spl-cicd-endpoint-dev (ตอนสร้างตาม UI-first rule) — ต้อง remap ผ่าน
# parameter.yml ตอน deploy เข้า prod
ENDPOINT_WORKSPACE_ID = "30e32f68-1cee-419b-be00-c0671b00f7af"  # spl-cicd-endpoint-dev
ENDPOINT_LAKEHOUSE_ID = "e68b8bb0-0ddb-44db-af00-bfd5b855a1ce"  # lh_endpoint_test_b ใน spl-cicd-endpoint-dev

endpoint_path = (
    f"abfss://{ENDPOINT_WORKSPACE_ID}@onelake.dfs.fabric.microsoft.com/"
    f"{ENDPOINT_LAKEHOUSE_ID}/Tables/ci_endpoint_test_b"
)

df = spark.createDataFrame(
    [(1, "cross-workspace-write-ok-test-b")],
    ["id", "note"],
)
df.write.format("delta").mode("overwrite").save(endpoint_path)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
