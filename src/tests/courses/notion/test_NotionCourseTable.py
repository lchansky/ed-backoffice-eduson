import pytest

from courses import notion
from courses.notion import NotionCourseTable


def test_init_and_prepare_data(monkeypatch):
    main_table = [
        {
            "object": "page",
            "id": "123",
            "parent": {
                "type": "database_id",
                "database_id": "123"
            },
            "properties": {
                "Продукт для шаблонов (название курса)": {
                    "type": "title",
                    "title": [
                        {
                            "type": "text",
                            "plain_text": "Название курса",
                        }
                    ]
                },
                "Статус": {
                    "type": "multi_select",
                    "multi_select": [
                        {"id": "123", "name": "multi_select_value_1"},
                        {"id": "456", "name": "multi_select_value_2"},
                    ]
                },
                "Все лендинги": {
                    "type": "relation",
                    "relation": [
                        {'id': 'id1'},
                        {'id': 'id2'}
                    ],
                },
                "Категория": {
                    "type": "relation",
                    "relation": [
                        {'id': 'id3'},
                        {'id': 'id4'}
                    ],
                },
                "Кластер": {
                    "type": "select",
                    "select": {"name": "IT"}
                }
            },
            "url": "https://www.notion.so/all-sales-300fe3de8b6d4dd5b6a168db75b29091",
        },
    ]
    landings_table = [
        {
            "id": "id1",
            "properties": {
                "Основной лендинг продукта?": {'checkbox': True, 'type': 'checkbox'},
                "Лендинг": {"type": "url", "url": "https://landing1"}
            }
        },
        {
            "id": "id2",
            "properties": {
                "Основной лендинг продукта?": {'checkbox': False, 'type': 'checkbox'},
                "Лендинг": {"type": "url", "url": "https://landing2"}
            }
        },
    ]
    categories_table = [
        {
            "id": "id3",
            "properties": {
                "Name": {
                    'type': 'rich_text',
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {
                                'content': "Категория 3",
                            },
                            'plain_text': "Категория 3",
                        }
                    ]
                },
                "Основная категория": {'checkbox': True, 'type': 'checkbox'},
                "category_id": {'type': 'number', 'number': 3}
            }
        },
        {
            "id": "id4",
            "properties": {
                "Name": {
                    'type': 'rich_text',
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {
                                'content': "Категория 4",
                            },
                            'plain_text': "Категория 4",
                        }
                    ]
                },
                "Основная категория": {'checkbox': False, 'type': 'checkbox'},
                "category_id": {'type': 'number', 'number': 4}
            }
        },
    ]

    def mock_func(*args, **kwargs):
        data = {
            'category_id': 10,
            'Name': "Популярные курсы",
        }
        return data

    monkeypatch.setattr(notion, "get_category_popular_courses", mock_func)
    result = NotionCourseTable.init_and_prepare_data(main_table, categories_table, landings_table)

    assert result[0] == {
        "id": "123",
        "Продукт для шаблонов (название курса)": "Название курса",
        "Статус": ["multi_select_value_1", "multi_select_value_2"],
        "Все лендинги": [
            {
                "Основной лендинг продукта?": True,
                "Лендинг": "https://landing1"
            },
            {
                "Основной лендинг продукта?": False,
                "Лендинг": "https://landing2"
            }
        ],
        "Лендинг": "https://landing1",
        "Категория": [
            {
                "Name": "Категория 3",
                "Основная категория": True,
                "category_id": 3
            },
            {
                "Name": "Категория 4",
                "Основная категория": False,
                "category_id": 4
            }
        ],
        "category_id": 3,
        "Основная категория": "Категория 3",
        "Кластер": "IT",
    }



