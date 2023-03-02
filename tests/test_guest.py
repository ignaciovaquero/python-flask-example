import pytest
from guest import Guest


@pytest.mark.parametrize(
    "guest_data, expected_result",
    [
        (
            {"name": "Ignacio", "last_name": "Vaquero"},
            "Ignacio:Vaquero",
        ),
        (
            {"name": "Ignacio", "last_name": "", "plus_one": False},
            "Ignacio:",
        ),
        (
            {"name": "", "last_name": "Vaquero", "plus_one": True},
            ":Vaquero",
        ),
        (
            {"name": "", "last_name": "", "plus_one": True},
            ":",
        ),
    ],
)
def test_guest_id_generation(guest_data, expected_result):
    guest = Guest(**guest_data)
    assert guest.id == expected_result
