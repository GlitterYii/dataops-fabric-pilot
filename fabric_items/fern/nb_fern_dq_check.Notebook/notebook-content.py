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

import great_expectations as gx

_ge_context = gx.get_context(mode="ephemeral")
_ge_batch_definition = (
    _ge_context.data_sources.add_pandas("pandas")
    .add_dataframe_asset(name="inventory")
    .add_batch_definition_whole_dataframe("batch")
)


def check_qty_on_hand_not_null(pdf):
    batch = _ge_batch_definition.get_batch(batch_parameters={"dataframe": pdf})
    expectation = gx.expectations.ExpectColumnValuesToNotBeNull(column="qty_on_hand")
    return batch.validate(expectation).success


if __name__ == "__main__":
    df = spark.table("inventory").toPandas()
    assert check_qty_on_hand_not_null(df), "Data quality check failed: qty_on_hand มีค่า null"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
