"""Test the names module."""
import pytest

from names import Names


@pytest.fixture
def new_names():
    """Return a new names instance."""
    return Names()


@pytest.fixture
def old_names():
    """Return a names instance with preallocated error count and names list."""
    names = Names()
    names.error_code_count = 3
    names.names = ["nand1", "or4", "xor"]
    #names.lookup(["nand1", "or4", "xor"])
    return names


def test_unique_error_codes(new_names, old_names):
    """Test if unique_error_codes method returns correct range() object."""
    with pytest.raises(TypeError):
        new_names.unique_error_codes(3.1)

    # Test returned range
    assert old_names.unique_error_codes(4) == range(3, 7)


def test_query_exceptions(new_names):
    """Test if query method raises correct errors."""
    with pytest.raises(TypeError):
        new_names.query(34.5)
    with pytest.raises(TypeError):
        new_names.query("2ab")  # not a "name" in EBFL


@pytest.mark.parametrize("name_id, name_string", [
    (0, "nand1"),
    (1, "or4"),
    (2, "xor"),
    (None, "and3")
])
def test_query(new_names, old_names, name_id, name_string):
    """Test if query method returns corresponding name ID."""
    assert old_names.query(name_string) == name_id


def test_lookup_exceptions(new_names):
    """Test if proper TypeError raised in lookup()."""
    with pytest.raises(TypeError):
        new_names.lookup(["and1", "2or"])
    with pytest.raises(TypeError):
        new_names.lookup(["and1", 3.14])


def test_lookup(old_names):
    """Test if lookup method returns correct ID list."""
    assert old_names.lookup(["or4", "nand1", "and2", "xor"]) == [1, 0, 3, 2]


def test_get_name_string(old_names):
    """Test if get_name_string returns correct name"""
    with pytest.raises(TypeError):
        old_names.get_name_string(2.4)

    # Verify correct name is returned
    assert old_names.get_name_string(2) == "xor"
    assert old_names.get_name_string(3) is None
