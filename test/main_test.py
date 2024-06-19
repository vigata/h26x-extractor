from pathlib import Path
import pytest


@pytest.fixture
def assets():
    a = Path(__file__).parent / 'assets' / 'sample.264'
    b = Path(__file__).parent / 'assets' / 'test.h264'
    return {'a': a, 'b': b}


def test_extract(assets):
    files =assets
    from h26x_extractor.h26x_parser_ex import extract_nal_units_from_file
    extract_nal_units_from_file(files['a'])
