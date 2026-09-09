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

# CELL ********************

import great_expectations as ge

df = spark.table("inventory").toPandas()
ge_df = ge.from_pandas(df)
result = ge_df.expect_column_values_to_not_be_null("qty_on_hand")
assert result.success, "Data quality check failed: qty_on_hand มีค่า null"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
