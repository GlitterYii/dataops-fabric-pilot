import importlib.util
import os

_NOTEBOOK_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..",
    "fabric_items", "nb_sales_transform.Notebook", "notebook-content.py",
)

_spec = importlib.util.spec_from_file_location("nb_sales_transform", _NOTEBOOK_PATH)
nb_sales_transform = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(nb_sales_transform)

calculate_regional_sales = nb_sales_transform.calculate_regional_sales


def test_sums_amount_per_region():
    records = [
        {"region": "north", "amount": 100},
        {"region": "north", "amount": 50},
        {"region": "south", "amount": 200},
    ]
    assert calculate_regional_sales(records) == {"north": 150, "south": 200}


def test_filters_out_null_amount():
    records = [
        {"region": "north", "amount": None},
        {"region": "north", "amount": 100},
    ]
    assert calculate_regional_sales(records) == {"north": 100}


def test_filters_out_negative_amount():
    records = [
        {"region": "north", "amount": -50},
        {"region": "north", "amount": 100},
    ]
    assert calculate_regional_sales(records) == {"north": 100}


def test_filters_out_missing_region():
    records = [
        {"region": None, "amount": 100},
        {"region": "south", "amount": 300},
    ]
    assert calculate_regional_sales(records) == {"south": 300}


def test_empty_input_returns_empty_dict():
    assert calculate_regional_sales([]) == {}
