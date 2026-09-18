# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "07d15704-7372-4746-a6dd-28f671348a83",
# META       "default_lakehouse_name": "lh_endpoint_test_a",
# META       "default_lakehouse_workspace_id": "7a829f6b-4fd1-45c7-8c8e-b7c317816e4b",
# META       "known_lakehouses": [
# META         {
# META           "id": "07d15704-7372-4746-a6dd-28f671348a83"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

# ทดสอบ cross-workspace write: pipeline/notebook นี้อยู่ spl-cicd-dev แต่เขียนข้อมูลออกไปยัง
# Lakehouse lh_endpoint_test_a ที่อยู่คนละ workspace (spl-cicd-endpoint-dev/prd) ดู
# DataOps-CICD-Workflow.md section 14 Phase 6
#
# เขียนผ่าน abfss:// path ตรงๆ (ไม่ใช้ default_lakehouse attach, ไม่ใช้ Copy Activity)
# เพื่อเลี่ยงบั๊ก Connection-permission ที่เจอมาแล้ว (section 15) — Spark เขียนเข้า OneLake
# ผ่านสิทธิ์ workspace โดยตรง ไม่ต้องพึ่ง Connection object เลย
#
# ค่า 2 ตัวนี้เป็นของ spl-cicd-endpoint-dev (ตอนสร้างตาม UI-first rule) — ต้อง remap ผ่าน
# parameter.yml ตอน deploy เข้า prod (ดู draft-parameter-endpoint.yml ใน DataOps repo)
ENDPOINT_WORKSPACE_ID = "30e32f68-1cee-419b-be00-c0671b00f7af"  # spl-cicd-endpoint-dev
ENDPOINT_LAKEHOUSE_ID = "04a575b1-f277-4fa2-84d4-5214992b8ed0"  # lh_endpoint_test_a ใน spl-cicd-endpoint-dev (สร้างโดย deploy-dev-endpoint job)

endpoint_path = (
    f"abfss://{ENDPOINT_WORKSPACE_ID}@onelake.dfs.fabric.microsoft.com/"
    f"{ENDPOINT_LAKEHOUSE_ID}/Tables/ci_endpoint_test"
)

df = spark.createDataFrame(
    [(1, "cross-workspace-write-ok")],
    ["id", "note"],
)
df.write.format("delta").mode("overwrite").save(endpoint_path)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
