import pytest

from courses.notion import parse_properties


@pytest.mark.parametrize(
    "input_data, expected",
    [
        (
                {"id": {"type": "id", "id": "some_id"}},
                {"id": "some_id"},
        ),
        (
                {"title_field_name": {"type": "title", "title": [{"type": "text", "text": {"content": "content_value"}, "plain_text": "plain_text_value"}]}},
                {"title_field_name": "plain_text_value"},
        ),
        (
                {"select_field_name": {"type": "select", "select": {"id": "123456", "name": "select_value"}}},
                {"select_field_name": "select_value"},
        ),
        (
                {"multi_select_field_name": {
                    "type": "multi_select",
                    "multi_select": [
                        {"id": "123", "name": "multi_select_value_1"},
                        {"id": "456", "name": "multi_select_value_2"},
                    ],
                }},
                {"multi_select_field_name": ["multi_select_value_1", "multi_select_value_2"]},
        ),
        (
                {"formula_field_name": {
                    "type": "formula",
                    "formula": {
                        "type": "number",
                        "number": 123456
                    }
                }},
                {"formula_field_name": 123456},
        ),
        (
                {"number_field_name": {
                    "type": "number",
                    "number": "None"
                }},
                {"number_field_name": None},
        ),
        (
                {"number_field_name": {
                    "type": "number",
                    "number": 123
                }},
                {"number_field_name": 123},
        ),
        (
                {"rich_text_field_name": {
                    'type': 'rich_text',
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {
                                'content': 'content_value',
                            },
                            'plain_text': 'plain_text_value',
                        }
                    ]
                }},
                {"rich_text_field_name": "plain_text_value"},
        ),
        (
                {"url_field_name": {
                    "type": "url",
                    "url": "https://eduson.academy"
                }},
                {"url_field_name": "https://eduson.academy"},
        ),
        (
                {"checkbox_field_name": {'checkbox': True, 'type': 'checkbox'}},
                {"checkbox_field_name": True},
        ),
        (
                {"relation_field_name": {
                    'type': 'relation',
                    'relation': [
                        {'id': 'id1'},
                        {'id': 'id2'}
                    ],
                }},
                {"relation_field_name": ["id1", "id2"]},
        ),
    ]
)
def test_parse_properties(input_data, expected):
    result = parse_properties(input_data)
    assert result == expected




