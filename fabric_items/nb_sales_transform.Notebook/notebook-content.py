# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

def calculate_regional_sales(records):
    # รวมยอดขายต่อภูมิภาค กรอง record ที่ amount เป็น None/ติดลบ หรือไม่มี region ทิ้ง (data quality ผิดพลาด ไม่นับรวม)
    totals = {}
    for record in records:
        region = record.get("region")
        amount = record.get("amount")
        if region is None or amount is None or amount < 0:
            continue
        totals[region] = totals.get(region, 0) + amount
    return totals

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

if __name__ == "__main__":
    df = spark.read.table("lh_test_lakehouse.sales_raw")
    records = [row.asDict() for row in df.collect()]
    result = calculate_regional_sales(records)
    spark.createDataFrame(
        [(region, total) for region, total in result.items()],
        ["region", "total_sales"],
    ).write.mode("overwrite").saveAsTable("sales_by_region")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
