import pytest

import sqlparse
from sqlparse import lexer, sql
from sqlparse import tokens as T


@pytest.mark.parametrize('operator', ['~*', '!~*', '~~*', '!~~*'])
def test_pattern_operator_token_and_group(operator):
    assert list(lexer.tokenize(operator)) == [(T.Operator.Comparison, operator)]
    parsed = sqlparse.parse(f"name {operator} 'pattern'")[0]
    assert len(parsed.tokens) == 1
    assert isinstance(parsed.tokens[0], sql.Comparison)
    assert parsed.tokens[0].tokens[2].value == operator
    assert parsed.tokens[0].right.value == "'pattern'"


@pytest.mark.parametrize('operator', ['~*', '!~*', '~~*', '!~~*'])
@pytest.mark.parametrize('separator', ['', ' '])
def test_pattern_operator_spacing(operator, separator):
    text = f"SELECT name{separator}{operator}{separator}'pattern' FROM tab"
    expected = f"SELECT name {operator} 'pattern' FROM tab"
    assert sqlparse.format(text, use_space_around_operators=True) == expected
    assert sqlparse.format(expected, use_space_around_operators=True) == expected


def test_issue613_operator_spacing():
    text = "SELECT ARRAY[1] <@ ARRAY[1, 2], 'a' !~* 'xyz'"
    assert sqlparse.format(text, use_space_around_operators=True) == text


@pytest.mark.parametrize('text, expected', [
    ('SELECT a*b, * FROM tab', 'SELECT a * b, * FROM tab'),
    ("SELECT '~*', '!~~*', * FROM tab", "SELECT '~*', '!~~*', * FROM tab"),
    ("SELECT name ~ * 'pattern'", "SELECT name ~ * 'pattern'"),
    ("SELECT name ~/* keep */*'pattern'", "SELECT name ~ /* keep */*'pattern'"),
])
def test_pattern_operator_controls(text, expected):
    assert sqlparse.format(text, use_space_around_operators=True) == expected
