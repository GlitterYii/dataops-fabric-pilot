import importlib.util
import os

import pandas as pd

_NOTEBOOK_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..",
    "fabric_items", "fern", "nb_fern_dq_check.Notebook", "notebook-content.py",
)

_spec = importlib.util.spec_from_file_location("nb_fern_dq_check", _NOTEBOOK_PATH)
nb_fern_dq_check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(nb_fern_dq_check)

check_qty_on_hand_not_null = nb_fern_dq_check.check_qty_on_hand_not_null


def test_passes_when_no_nulls():
    df = pd.DataFrame({"qty_on_hand": [10, 5, 0]})
    assert check_qty_on_hand_not_null(df) is True


def test_fails_when_null_present():
    df = pd.DataFrame({"qty_on_hand": [10, None, 0]})
    assert check_qty_on_hand_not_null(df) is False
