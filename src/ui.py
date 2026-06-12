from dataclasses import asdict, dataclass

from htbuilder import (
    HtmlTag,
    body,
    button,
    div,
    form,
    h3,
    head,
    html,
    input_,
    p,
    script,
    span,
    styles,
    table,
    tbody,
    td,
    th,
    thead,
    tr,
)
from htbuilder.units import ch, px

# Element IDs we need for HTMX Targets

TABLE_ID = "table"
RESULT_ID = "result"
SELECT_ALL_ID = "select_all"

# Session State Logic


@dataclass
class Row:
    id: str
    name: str
    selected: bool


@dataclass
class SessionState:
    id: str
    name_contains: str
    rows: list[Row]
    sort_by: tuple[str, bool]  # (attr of Row, ascending?)

    def sort(self):
        sort_col, sort_ascending = self.sort_by
        self.rows = sorted(
            self.rows,
            key=lambda r: asdict(r)[sort_col],
            reverse=not sort_ascending,
        )


def add_session(href: str, session: SessionState) -> str:
    return f"{href}?session_id={session.id}"


def initialise_session(session_id: str, init_rows: list[Row]) -> SessionState:
    result = SessionState(
        id=session_id,
        name_contains="",
        rows=init_rows,
        sort_by=("name", True),
    )
    result.sort()
    return result


def get_row(session: SessionState, row_id: str) -> Row | None:
    for row in session.rows:
        if row.id == row_id:
            return row


# HTML Rendering


def homepage(session: SessionState) -> HtmlTag:
    # Basic dark theme
    html_style = styles(
        background_color="black",
        color="white",
        padding_left=px(20),
    )
    # Stack body elements vertically with a bit of space between them
    form_style = styles(
        display="flex",
        flex_direction="column",
        gap=px(12),
    )

    return html(
        head(script(src="/static/htmx.min.js")),
        body(
            h3("HTMX Demo"),
            form(
                span(
                    name_contains_input(session),
                    bulk_select_button(session),
                ),
                main_table(session),
                submit_button(session),
                style=form_style,
            ),
            p(id=RESULT_ID),
        ),
        style=html_style,
    )


def name_contains_input(session: SessionState) -> HtmlTag:
    placeholder = "Type to filter rows by name..."
    return input_(
        type="text",
        name="name_contains",
        value=session.name_contains,
        placeholder=placeholder,
        hx_get=add_session(f"/table/filter", session),
        hx_trigger="input changed delay:300ms, keyup[key=='Enter']",
        hx_target=f"#{TABLE_ID}",
        hx_swap="outerHTML",
        style=styles(width=ch(len(placeholder))),
    )


def bulk_select_button(session: SessionState) -> HtmlTag:
    all_selected = all(row.selected for row in session.rows)
    button_text = "Deselect All" if all_selected else "Select All"
    href = f"/table/{'deselect' if all_selected else 'select'}/all"
    return button(
        button_text,
        id=SELECT_ALL_ID,
        hx_post=add_session(href, session),
        hx_target=f"#{TABLE_ID}",
        hx_swap_oob="true",
    )


def main_table(session: SessionState) -> HtmlTag:
    base_cell_style = dict(
        padding=px(8),
        border_bottom="1px solid #eee",
    )
    # header center aligned by default; data left aligned by default
    header_cell_style = styles(text_align="left", **base_cell_style)
    data_cell_style = styles(**base_cell_style)

    heading_row = thead(
        tr(
            th(
                "Selected",
                sort_icon(session, "selected"),
                style=header_cell_style,
            ),
            th(
                "Name",
                sort_icon(session, "name"),
                style=header_cell_style,
            ),
        )
    )
    rows = tbody(
        tr(
            td(
                checkbox(row, session),
                style=data_cell_style,
            ),
            td(
                row.name,
                style=data_cell_style,
            ),
        )
        for row in session.rows
        if session.name_contains.lower() in row.name.lower()
    )
    return table(
        heading_row,
        rows,
        id=TABLE_ID,
        style=styles(
            width=px(200),
        ),
    )


def sort_icon(session: SessionState, header_key: str):
    # header_key must be an attribute name of Row
    sort_col, sort_ascending = session.sort_by
    matches_header = sort_col == header_key
    header_ascending = sort_ascending if matches_header else True

    href = f"/table/sort/{header_key}"

    up_arrow = "&#8593;"
    down_arrow = "&#8595;"
    sort_icon = up_arrow if header_ascending else down_arrow

    icon_style = styles(
        color="red" if matches_header else "white",
        margin_left=ch(2),
        text_decoration="none",
        cursor="pointer",
    )

    return span(
        sort_icon,
        hx_get=add_session(href, session),
        hx_target=f"#{TABLE_ID}",
        style=icon_style,
    )


def checkbox(row: Row, session: SessionState) -> HtmlTag:
    attrs = dict(
        type="checkbox",
        name="selected",
        value=row.id,
        hx_post=add_session(f"/table/row/{row.id}/toggle-select", session),
    )
    # need an absence of the checked attribute to render an unchecked checkbox
    if row.selected:
        attrs["checked"] = "checked"  # any string works

    return input_(**attrs)


def submit_button(session: SessionState) -> HtmlTag:
    return input_(
        type="submit",
        hx_post=add_session("/", session),
        hx_target=f"#{RESULT_ID}",
        hx_swap="textContent",
        style=styles(width=ch(10)),
    )
