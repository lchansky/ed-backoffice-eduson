from dataclasses import dataclass

from courses.notion import PRICES_FIELDS_DETECTS_CHANGES


@dataclass
class FieldChange:
    old_value: str
    new_value: str


@dataclass
class RowChange:
    id: str
    changed_fields: dict[str, FieldChange]


@dataclass
class Difference:
    removed_cols: list[str]
    added_cols: list[str]
    removed_rows: list[dict]
    added_rows: list[dict]
    changed_rows: list[RowChange]

    def __bool__(self):
        return any([
            self.removed_cols,
            self.added_cols,
            self.removed_rows,
            self.added_rows,
            self.changed_rows,
        ])

    def has_prices_changes(self):
        if self.added_rows:
            return True
        for row in self.changed_rows:
            for field_name, field_change in row.changed_fields.items():
                if field_name in PRICES_FIELDS_DETECTS_CHANGES:
                    return True
        return False


def compare_two_tables(previous_table: list[dict], new_table: list[dict]) -> Difference:
    if not previous_table or not new_table:
        raise ValueError("One of the tables is empty")

    # compare keys (cols)
    previous_keys = set(previous_table[0].keys())
    new_keys = set(new_table[0].keys())
    removed_cols = list(previous_keys - new_keys)
    added_cols = list(new_keys - previous_keys)

    # new/removed rows
    previous_ids = set([row["id"] for row in previous_table])
    new_ids = set([row["id"] for row in new_table])
    removed_ids = list(previous_ids - new_ids)
    added_ids = list(new_ids - previous_ids)
    removed_rows = [row for row in previous_table if row["id"] in removed_ids]
    added_rows = [row for row in new_table if row["id"] in added_ids]

    # changed rows
    changed_rows = []
    common_cols = list(previous_keys & new_keys)
    common_old_rows = {row["id"]: row for row in previous_table if row["id"] in new_ids}
    common_new_rows = {row["id"]: row for row in new_table if row["id"] in previous_ids}
    for idx, row in common_old_rows.items():
        changed_fields = {}
        for col in common_cols:
            if row[col] != common_new_rows[idx][col]:
                changed_fields[col] = FieldChange(row[col], common_new_rows[idx][col])
        if changed_fields:
            changed_rows.append(RowChange(idx, changed_fields))

    difference = Difference(
        removed_cols=removed_cols,
        added_cols=added_cols,
        removed_rows=removed_rows,
        added_rows=added_rows,
        changed_rows=changed_rows,
    )
    return difference

