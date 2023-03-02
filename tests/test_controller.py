import pytest
import os
from unittest.mock import patch

from controller import Controller, NotFoundError, ConflictError, pd
from guest import Guest


@pytest.mark.parametrize(
    "file, expected_result",
    [
        (
            f"{os.getcwd()}/tests/fixtures/db.csv",
            [Guest(name="Ignacio", last_name="Vaquero")],
        ),
        ("non_existing.csv", []),
    ],
)
def test_get_all(file, expected_result):
    c = Controller(filename=file)
    guests = c.get_all()
    assert guests == expected_result


@pytest.mark.parametrize(
    "file, guest_id, expected_result, exception",
    [
        (
            f"{os.getcwd()}/tests/fixtures/db.csv",
            "Ignacio:Vaquero",
            Guest(name="Ignacio", last_name="Vaquero"),
            None,
        ),
        ("non_existing", "", None, NotFoundError),
        (
            f"{os.getcwd()}/tests/fixtures/db.csv",
            "non_existing_id",
            None,
            NotFoundError,
        ),
    ],
)
def test_get(file, guest_id, expected_result, exception):
    c = Controller(filename=file)
    if exception is not None:
        with pytest.raises(exception):
            c.get(id=guest_id)
        return
    assert c.get(id=guest_id) == expected_result


@pytest.mark.parametrize(
    "file, guest_id, exception",
    [
        (f"{os.getcwd()}/tests/fixtures/db.csv", "Ignacio:Vaquero", None),
        ("non_existing_file", "Ignacio:Vaquero", NotFoundError),
    ],
)
@patch.object(pd.DataFrame, "to_csv", return_value=None)
def test_delete(mock_pd, file, guest_id, exception):
    c = Controller(filename=file)
    if exception is not None:
        with pytest.raises(exception):
            c.delete(guest_id)
        return
    c.delete(guest_id)


@pytest.mark.parametrize(
    "file, guest, expected_create, exception",
    [
        (
            f"{os.getcwd()}/tests/fixtures/db.csv",
            Guest("Ignacio", "Vaquero"),
            False,
            ConflictError,
        ),
        (
            f"{os.getcwd()}/tests/fixtures/db.csv",
            Guest("Jaime", "Vaquero"),
            False,
            None,
        ),
        ("non_existing_file", Guest("Jaime", "Vaquero"), True, None),
    ],
)
def test_save(file, guest, expected_create, exception):
    c = Controller(file)
    if exception is not None:
        with pytest.raises(exception):
            c.save(guest)
    else:
        if not expected_create:
            with patch.object(pd.DataFrame, "to_csv", return_value=None):
                c.save(guest)
        else:
            c.save(guest)
            assert os.path.exists(file)
            os.remove(file)
