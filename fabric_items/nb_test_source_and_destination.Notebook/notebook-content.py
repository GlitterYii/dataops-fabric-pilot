# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

def get_seed_rows():
    # ข้อมูล dummy คงที่ ใช้ยืนยันว่า write เข้า lakehouse ได้ในทุก environment (dev/staging/prod)
    # ไม่พึ่งพา external Connection ใดๆ — อ่าน/เขียนผ่าน Spark ภายใน workspace เดียวกันเท่านั้น
    # แยกเป็น pure function (ไม่แตะ spark) เพื่อ unit-test ได้โดยไม่ต้องมี Spark session จริง
    return [(1, "row-a"), (2, "row-b"), (3, "row-c")]


def validate_row_counts(source_count, dest_count):
    # แยกเป็น pure function เพื่อ unit-test ได้เช่นกัน
    if source_count != dest_count:
        raise AssertionError(
            f"Row count mismatch: source={source_count}, destination={dest_count}"
        )
    return True

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

if __name__ == "__main__":
    # 1) Seed source แบบ idempotent — รันซ้ำได้ผลลัพธ์เดิมทุกครั้ง
    df_source = spark.createDataFrame(get_seed_rows(), ["id", "label"])
    df_source.write.mode("overwrite").saveAsTable("ci_test_source")

    # 2) Copy source -> destination (พิสูจน์ว่า read/write ภายใน environment นี้ใช้งานได้จริง)
    df_source_read = spark.read.table("ci_test_source")
    df_source_read.write.mode("overwrite").saveAsTable("ci_test_destination")

    # 3) Validate — row count ต้องตรงกันเป๊ะ ไม่งั้นถือว่า smoke test ล้มเหลว
    source_count = spark.read.table("ci_test_source").count()
    dest_count = spark.read.table("ci_test_destination").count()
    print(f"ci_test_source rows: {source_count}, ci_test_destination rows: {dest_count}")
    validate_row_counts(source_count, dest_count)
    print("Source/destination smoke test passed.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
