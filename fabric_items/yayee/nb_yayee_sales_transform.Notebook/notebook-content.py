# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

# test
from pyspark.sql.functions import when, col

df = spark.table("sales")
df = df.withColumn(
    "region",
    when(col("product_id").isin("P001"), "BKK").otherwise("CNX")
)
df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable("sales")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
