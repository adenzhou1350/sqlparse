import pytest

import sqlparse
from sqlparse import sql
from sqlparse import tokens as T
from sqlparse.lexer import tokenize


@pytest.mark.parametrize('join', [
    'JOIN', 'join', 'LEFT JOIN', 'LEFT OUTER JOIN', 'CROSS JOIN', 'NATURAL JOIN',
])
def test_join_before_parenthesized_subquery(join):
    condition = '' if join in ('CROSS JOIN', 'NATURAL JOIN') else ' on child.parent_id=p.id'
    query = f'select * from child {join}(select * from parent) as p{condition};'
    statement = sqlparse.parse(query)[0]
    significant = [token for token in statement if not token.is_whitespace]

    assert significant[4].match(T.Keyword, join.upper())
    assert isinstance(significant[3], sql.Identifier)
    assert significant[3].get_real_name() == 'child'
    assert isinstance(significant[5], sql.Identifier)
    assert significant[5].get_alias() == 'p'
    assert str(statement) == query


@pytest.mark.parametrize('name', ['joined', 'join_table', 'schema.join', 'schema.JOIN'])
def test_join_function_name_controls(name):
    query = f'{name}(1)'
    names = [value for ttype, value in tokenize(query) if ttype is T.Name]
    assert names == name.split('.')
    expected_group = sql.Identifier if '.' in name else sql.Function
    assert isinstance(sqlparse.parse(query)[0].tokens[0], expected_group)
