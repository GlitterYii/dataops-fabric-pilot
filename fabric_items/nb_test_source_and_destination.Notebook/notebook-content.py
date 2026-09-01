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

def get_seed_rows():
    return [(1, "row-a"), (2, "row-b"), (3, "row-c")]


def validate_row_counts(source_count, dest_count):
    if source_count != dest_count:
        raise AssertionError(
            f"Row count mismatch: source={source_count}, destination={dest_count}"
        )
    return True


if __name__ == "__main__":
    df_source = spark.createDataFrame(get_seed_rows(), ["id", "label"])
    df_source.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable("ci_test_source")

    df_source_read = spark.read.table("ci_test_source")
    df_source_read.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable("ci_test_destination")

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
