from occlib import __version__


def test_example(example_fixture: int) -> None:
    assert __version__ is not False
