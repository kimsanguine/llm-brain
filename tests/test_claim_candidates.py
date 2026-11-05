"""Structural filtering must preserve uncertain text and stable claim indexes."""
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))


def classify(body):
    from lib import claim_candidates
    return claim_candidates.classify_candidates(body)


@pytest.mark.parametrize('statement', [
    '- Alpha is supported by the source.',
    '* The model accepts text',
    '1) A numbered factual bullet',
    'Plain factual text without sentence punctuation',
    '문제 정의 (시작) + 평가 기준 (끝) = 모델이 중간을 채운다',
    'Accuracy: 90%',
    'The source is [Alpha](https://example.invalid/alpha).',
    '#not-a-markdown-heading',
])
def test_normal_text_is_retained_unchanged_without_semantic_certification(statement):
    result = classify(statement)
    assert result == [{'index': 1, 'statement': statement, 'kind': 'text',
                       'exclusion_reason': None}]


@pytest.mark.parametrize(('statement', 'kind'), [
    ('## Heading', 'heading'),
    ('| Name | Value |', 'table'),
    ('| --- | :---: |', 'table'),
    ('---', 'separator'),
    ('* * *', 'separator'),
    ('___', 'separator'),
    ('[Source](https://example.invalid/alpha)', 'link'),
    ('- [[alpha]]', 'link'),
    ('<https://example.invalid/alpha>', 'link'),
    ('https://example.invalid/alpha', 'link'),
    ('![Chart](assets/chart.png)', 'image'),
    ('tags: [alpha, beta]', 'metadata'),
    ('- source: https://example.invalid/alpha', 'metadata'),
    ('[alpha]: https://example.invalid/alpha', 'metadata'),
    ('<!-- source metadata -->', 'metadata'),
])
def test_obvious_structure_is_explicitly_excluded(statement, kind):
    assert classify(statement) == [
        {'index': 1, 'statement': statement, 'kind': kind,
         'exclusion_reason': 'non_statement'}]


def test_context_keeps_split_heading_parts_and_code_lines_out_of_evidence():
    body = ('# Overview. Heading continuation\n'
            '```python\n'
            'print("Alpha.")\n'
            'Bare text. More bare text\n'
            '```\n'
            '- A factual bullet survives\n')
    assert classify(body) == [
        {'index': 1, 'statement': '# Overview.', 'kind': 'heading', 'exclusion_reason': 'non_statement'},
        {'index': 2, 'statement': 'Heading continuation', 'kind': 'heading', 'exclusion_reason': 'non_statement'},
        {'index': 3, 'statement': '```python', 'kind': 'code', 'exclusion_reason': 'non_statement'},
        {'index': 4, 'statement': 'print("Alpha.")', 'kind': 'code', 'exclusion_reason': 'non_statement'},
        {'index': 5, 'statement': 'Bare text.', 'kind': 'code', 'exclusion_reason': 'non_statement'},
        {'index': 6, 'statement': 'More bare text', 'kind': 'code', 'exclusion_reason': 'non_statement'},
        {'index': 7, 'statement': '```', 'kind': 'code', 'exclusion_reason': 'non_statement'},
        {'index': 8, 'statement': '- A factual bullet survives', 'kind': 'text', 'exclusion_reason': None},
    ]


def test_fence_character_and_length_control_the_entire_code_range():
    body = '~~~~text\nAlpha\n```\n~~~\nStill code\n~~~~\nAlpha\n'
    result = classify(body)
    assert [row['kind'] for row in result] == ['code'] * 6 + ['text']
    assert result[-1] == {'index': 7, 'statement': 'Alpha', 'kind': 'text', 'exclusion_reason': None}
    assert [row['kind'] for row in classify('```\nUnclosed code')] == ['code', 'code']


def test_setext_headings_and_table_context_are_structural_but_pipes_in_prose_survive():
    body = 'Overview\n===\nName | Value\n--- | ---\nAlpha | 12\n\nA | B is an ordinary alternative\n'
    assert [row['kind'] for row in classify(body)] == [
        'heading', 'separator', 'table', 'table', 'table', 'text']


def test_empty_and_repeated_statements_preserve_original_split_order():
    assert classify(' \n\n ') == []
    result = classify('\n## Alpha\nAlpha\n```\nAlpha\n```\nAlpha\n')
    assert [(row['index'], row['statement'], row['kind']) for row in result] == [
        (1, '## Alpha', 'heading'), (2, 'Alpha', 'text'),
        (3, '```', 'code'), (4, 'Alpha', 'code'),
        (5, '```', 'code'), (6, 'Alpha', 'text')]


def test_separator_after_a_factual_bullet_does_not_turn_the_bullet_into_a_heading():
    result = classify('- Alpha is factual\n---\n1. Beta is factual\n---\n')
    assert [(row['index'], row['kind'], row['exclusion_reason']) for row in result] == [
        (1, 'text', None), (2, 'separator', 'non_statement'),
        (3, 'text', None), (4, 'text', None), (5, 'separator', 'non_statement')]


def test_split_link_labels_remain_structural_without_dropping_adjacent_prose():
    result = classify('[Source. More detail](https://example.invalid/alpha)\n'
                      'A fact. [Source](https://example.invalid/alpha)\n')
    assert [(row['statement'], row['kind']) for row in result] == [
        ('[Source.', 'link'), ('More detail](https://example.invalid/alpha)', 'link'),
        ('A fact.', 'text'), ('[Source](https://example.invalid/alpha)', 'link')]
