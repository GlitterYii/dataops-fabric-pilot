import importlib.util
import os

import pytest

_NOTEBOOK_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..",
    "fabric_items", "nb_test_source_and_destination.Notebook", "notebook-content.py",
)

_spec = importlib.util.spec_from_file_location("nb_test_source_and_destination", _NOTEBOOK_PATH)
nb_test_source_and_destination = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(nb_test_source_and_destination)

get_seed_rows = nb_test_source_and_destination.get_seed_rows
validate_row_counts = nb_test_source_and_destination.validate_row_counts


def test_seed_rows_not_empty():
    rows = get_seed_rows()
    assert len(rows) > 0


def test_seed_rows_have_unique_ids():
    rows = get_seed_rows()
    ids = [row[0] for row in rows]
    assert len(ids) == len(set(ids))


def test_validate_row_counts_matching():
    assert validate_row_counts(3, 3) is True


def test_validate_row_counts_mismatch_raises():
    with pytest.raises(AssertionError):
        validate_row_counts(3, 2)
