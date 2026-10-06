"""Text and binary streams should share the existing decoding path."""
import gzip
from io import BytesIO, StringIO

import pytest

import sqlparse


@pytest.mark.parametrize('encoding', ['utf-8', 'latin-1'])
@pytest.mark.parametrize('compressed', [False, True])
def test_parsestream_binary(encoding, compressed):
    # issue352: GzipFile is a binary stream, not a TextIOBase.
    text = "SELECT 'caf\N{LATIN SMALL LETTER E WITH ACUTE}'; SELECT 2;"
    data = text.encode(encoding)
    if compressed:
        stream = gzip.GzipFile(fileobj=BytesIO(gzip.compress(data)))
    else:
        stream = BytesIO(data)
    with stream:
        result = [str(stmt) for stmt in sqlparse.parsestream(stream, encoding)]
        assert not stream.closed
    assert result == [str(stmt) for stmt in sqlparse.parse(text)]


def test_parsestream_binary_default_encoding():
    text = "SELECT '\N{CJK UNIFIED IDEOGRAPH-65E5}';"
    with BytesIO(text.encode('utf-8')) as stream:
        assert [str(stmt) for stmt in sqlparse.parsestream(stream)] == [text]


def test_parsestream_text():
    text = "SELECT 'caf\N{LATIN SMALL LETTER E WITH ACUTE}';"
    with StringIO(text) as stream:
        assert [str(stmt) for stmt in sqlparse.parsestream(stream)] == [text]
        assert not stream.closed


def test_parsestream_binary_bad_encoding():
    with BytesIO(b"SELECT '\xff';") as stream:
        with pytest.raises(UnicodeDecodeError):
            list(sqlparse.parsestream(stream, encoding='utf-8'))


def test_parsestream_invalid_object():
    with pytest.raises(TypeError, match='Expected text or file-like object'):
        list(sqlparse.parsestream(object()))
