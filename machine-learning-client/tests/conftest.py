"""
This module contains pytest fixtures for the test suite.
"""

import pytest

@pytest.fixture
def example_fixture():
    """
    This fixture provides the string 'example' for use in tests.
    """
    return "example"
