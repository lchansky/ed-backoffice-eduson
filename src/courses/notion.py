import os

import notion_client

notion = notion_client.Client(auth=os.getenv("NOTION_TOKEN"))


PRICES_FIELDS_DETECTS_CHANGES = [
    'Полная цена',
    '% скидки',
]


def get_rich_text(rich_text_field: dict):
    plain_texts = [
        elem.get("plain_text")
        for elem in rich_text_field.get("rich_text", [])
    ]
    return "\n".join(plain_texts)


def get_title(title_field: dict):
    plain_texts = [
        elem.get("plain_text")
        for elem in title_field.get("title", [])
    ]
    return "\n".join(plain_texts)


PROPERTIES_PARSERS = {
    "id": lambda x: x.get("id", None),
    "rich_text": get_rich_text,
    "title": get_title,
    "url": lambda x: x.get("url", None) if x.get("url") != "None" else None,
    "number": lambda x: x.get("number", None) if x.get("number") != "None" else None,
    "formula": lambda x: x.get("formula", {}).get("number", None),
    "checkbox": lambda x: x.get("checkbox", None),
    "select": lambda x: x.get("select", {}).get("name", None) if x.get("select") else None,
    "multi_select": lambda x: [
        elem.get("name")
        for elem in x.get("multi_select", [])
    ],
    "relation": lambda x: [
        elem.get("id")
        for elem in x.get("relation", [])
    ]
}


def parse_properties(properties: dict, properties_parsers: dict = None):
    processed_properties = {}
    properties_parsers = properties_parsers or PROPERTIES_PARSERS
    for field_name, field_data in properties.items():
        field_type = field_data.get("type")
        if field_type in properties_parsers.keys():
            processed_properties[field_name] = properties_parsers[field_type](field_data)
        else:
            processed_properties[field_name] = f"Unknown Notion field type: {field_type}"
    return processed_properties


def get_category_popular_courses(page_id: str = None) -> dict:
    if not page_id:
        page_id = os.getenv("NOTION_CATEGORY_POPULAR_COURSES_PAGE_ID")
    data = notion.pages.retrieve(page_id)
    properties = data.get("properties", {})
    properties = parse_properties(properties)
    return properties


class NotionCourseTable:
    def __init__(
            self,
            main_table: list[dict],
    ):
        self.main_table = main_table

    @classmethod
    def init_and_prepare_data(
            cls, main_table: list[dict], categories_table: list[dict], landings_table: list[dict]
    ) -> list[dict]:
        relations = {category["id"]: category for category in categories_table}
        relations.update(
            **{landing["id"]: landing for landing in landings_table}
        )
        main_table = cls.parse_properties_from_db_rows(main_table, relations_from_other_tables=relations)
        instance = cls(main_table)
        finish_data = instance.process_relation_properties()
        return finish_data

    @classmethod
    def parse_properties_from_db_rows(cls, db_rows: list[dict], relations_from_other_tables: dict = None) -> list[dict]:
        if relations_from_other_tables:
            properties_parsers = PROPERTIES_PARSERS.copy()

            def get_relation(relation_field):
                relations_ids = [elem.get("id") for elem in relation_field.get("relation", [])]
                relations = []
                for relation_id in relations_ids:
                    relation_data = relations_from_other_tables.get(relation_id, {})
                    if relation_data:
                        relation_properties = relation_data.get("properties", {})
                        relation_properties = parse_properties(relation_properties, properties_parsers)
                        relations.append(relation_properties)
                return relations

            properties_parsers["relation"] = get_relation
        else:
            properties_parsers = PROPERTIES_PARSERS

        # Добавляю в properties также поле id ноушна (будто бы это проперти)
        # чтобы потом их идентифицировать при сравнении
        for row in db_rows:
            properties_dict = row.get("properties", {})
            properties_dict["id"] = {"type": "id", "id": row["id"]}

        rows_properties = [row["properties"] for row in db_rows]
        processed_rows = []
        for row in rows_properties:
            processed_properties = parse_properties(row, properties_parsers)
            processed_rows.append(processed_properties)
        return processed_rows

    def process_relation_properties(self) -> list[dict]:
        popular_courses_category = get_category_popular_courses()
        popular_courses_category_id = popular_courses_category["category_id"]
        popular_courses_category_name = popular_courses_category["Name"]

        for row in self.main_table:
            landings = row.get("Все лендинги", [])
            main_landing = None
            for landing in landings:
                if landing.get("Основной лендинг продукта?"):
                    main_landing = landing.get("Лендинг", None)
                    break
            row["Лендинг"] = main_landing

            categories = row.get("Категория", [])
            category_id = None
            main_category_name = "undefined"
            # если кластер "Подарочный", "Общее" или "Бесплатный курс", то основная категория = "Популярные курсы"
            for category in categories:
                if category["Основная категория"] is True:
                    category_id = category.get("category_id", None)
                    main_category_name = category.get("Name", "undefined")
                    break
            if row["Кластер"] in ("Подарочный", "Общее", "Бесплатный курс"):
                category_id = popular_courses_category_id
                main_category_name = popular_courses_category_name

            row["category_id"] = category_id
            row["Основная категория"] = main_category_name

        return self.main_table


class NotionAPI:
    def get_database_info(self, database_id: str) -> dict:
        data = notion.databases.retrieve(database_id)
        return data

    def get_database_rows(self, database_id: str) -> list[dict]:
        rows = []
        data = notion.databases.query(database_id)
        rows += data["results"]
        while data.get("has_more"):
            data = notion.databases.query(
                database_id,
                start_cursor=data["next_cursor"]
            )
            rows += data["results"]
        return rows

    def get_courses_table_data(self) -> list[dict]:
        main_table = self.get_database_rows(os.getenv("NOTION_COURSES_DATABASE_ID"))
        categories_table = self.get_database_rows(os.getenv("NOTION_CATEGORIES_DATABASE_ID"))
        landings_table = self.get_database_rows(os.getenv("NOTION_LANDINGS_DATABASE_ID"))
        finish_table = NotionCourseTable.init_and_prepare_data(main_table, categories_table, landings_table)
        return finish_table

    def get_page(self, page_id: str) -> dict:
        data = notion.pages.retrieve(page_id)
        return data
