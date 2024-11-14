import pytest

def test_mock():
    try:
        assert True is True
    except Exception:
        pytest.fail("An unexpected exception was raised.")
