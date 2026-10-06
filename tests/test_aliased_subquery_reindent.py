import pytest

import sqlparse


@pytest.mark.parametrize('width', [2, 4])
def test_aliased_subquery_has_one_leading_break(width):
    # Issue 334: both the IdentifierList and the query Parenthesis added a
    # newline when an alias wrapped the parenthesis in an Identifier.
    source = ('select c.id, c.value, '
              '(select count(*) as cnt from d where d.item_id = id) '
              'as "Count", c.whatever from something as c')
    expected = '\n'.join([
        'SELECT c.id,',
        '       c.value,',
        ' ' * width + '(SELECT count(*) AS cnt',
        ' ' * (width + 1) + 'FROM d',
        ' ' * (width + 1) + 'WHERE d.item_id = id) AS "Count",',
        '       c.whatever',
        'FROM something AS c',
    ])
    options = {'reindent': True, 'keyword_case': 'upper', 'indent_width': width}
    assert sqlparse.format(source, **options) == expected
    assert sqlparse.format(expected, **options) == expected


@pytest.mark.parametrize('alias', ['as counted', 'counted', 'as "Count"'])
def test_multiple_aliased_query_columns(alias):
    source = f'select a, (select 1) {alias}, (select 2) othercol, b from tbl'
    expected = '\n'.join([
        'select a,',
        f'  (select 1) {alias},',
        '  (select 2) othercol,',
        '       b',
        'from tbl',
    ])
    assert sqlparse.format(source, reindent=True) == expected


@pytest.mark.parametrize('source,expected', [
    ('select (select 1) as counted, c.id from something as c',
     'select\n  (select 1) as counted,\n       c.id\nfrom something as c'),
    ('select (select 1) as counted from something as c',
     'select\n  (select 1) as counted\nfrom something as c'),
    ('select c.id, (c.value + 1) as counted, c.whatever from something as c',
     'select c.id,\n       (c.value + 1) as counted,\n'
     '       c.whatever\nfrom something as c'),
    ('select * from (select 1) as counted',
     'select *\nfrom\n  (select 1) as counted'),
])
def test_other_parenthesis_layouts_are_unchanged(source, expected):
    assert sqlparse.format(source, reindent=True) == expected


@pytest.mark.parametrize('options,expected', [
    ({'indent_tabs': True},
     'select a,\n\t\t(select 1) as counted,\n\tb\nfrom tbl'),
    ({'indent_columns': True},
     'select\n  a,\n  (select 1) as counted,\n  b\nfrom tbl'),
    ({'wrap_after': 100},
     'select a,\n  (select 1) as counted, b\nfrom tbl'),
    ({'comma_first': True},
     'select a\n     ,\n  (select 1) as counted\n     , b\nfrom tbl'),
])
def test_aliased_subquery_format_options(options, expected):
    source = 'select a, (select 1) as counted, b from tbl'
    assert sqlparse.format(source, reindent=True, **options) == expected


def test_statement_separator_blank_line_is_retained():
    source = 'select a, (select 1) as counted, b from tbl; select 2;'
    expected = ('select a,\n  (select 1) as counted,\n       b\n'
                'from tbl;\n\nselect 2;')
    assert sqlparse.format(source, reindent=True) == expected
