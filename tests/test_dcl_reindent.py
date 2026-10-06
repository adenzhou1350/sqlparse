"""Privilege names and REVOKE's FROM are not query-clause boundaries."""

import pytest

import sqlparse
from sqlparse import tokens as T


@pytest.mark.parametrize('statement', [
    'GRANT SELECT ON a_schema.an_object TO a_role;',
    'GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON t TO a_role;',
    'GRANT SELECT ON ALL TABLES IN SCHEMA public TO umbrella;',
    'GRANT ALL PRIVILEGES ON TABLE t TO a_role WITH GRANT OPTION;',
    'REVOKE SELECT ON TABLE customers FROM umbrella;',
    'REVOKE GRANT OPTION FOR SELECT, UPDATE ON t FROM a_role;',
    'REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM a_role;',
])
def test_privileges_are_not_split_as_statements(statement):
    formatted = sqlparse.format(statement, reindent=True)
    assert formatted == statement
    assert sqlparse.format(formatted, reindent=True) == formatted


@pytest.mark.parametrize('comment', ['-- privileges\n', '/* privileges */ '])
def test_dcl_after_comment_is_recognized(comment):
    statement = comment + 'GRANT SELECT ON t TO a_role;'
    assert sqlparse.format(statement, reindent=True) == statement


def test_dcl_retains_keyword_case_filtering():
    statement = 'revoke select on table customers from umbrella;'
    assert sqlparse.format(statement, reindent=True, keyword_case='upper') == (
        'REVOKE SELECT ON TABLE customers FROM umbrella;')


def test_dcl_does_not_disable_following_query_indentation():
    statement = 'GRANT SELECT ON t TO a_role; SELECT a, b FROM t;'
    assert sqlparse.format(statement, reindent=True) == (
        'GRANT SELECT ON t TO a_role;\n\nSELECT a,\n       b\nFROM t;')


def test_privilege_tokens_keep_their_existing_lexical_types():
    statement = sqlparse.parse('GRANT SELECT ON t TO a_role;')[0]
    keywords = [(token.value, token.ttype) for token in statement.flatten()
                if token.ttype in T.Keyword]
    assert keywords == [('GRANT', T.Keyword.DCL), ('SELECT', T.Keyword.DML),
                        ('ON', T.Keyword), ('TO', T.Keyword)]
