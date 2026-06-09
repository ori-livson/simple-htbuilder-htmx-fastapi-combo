from dataclasses import dataclass

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


def add_session(href: str, session: SessionState) -> str:
    return f"{href}?session_id={session.id}"


def initialise_session(session_id: str, init_rows: list[Row]) -> SessionState:
    return SessionState(
        id=session_id,
        name_contains="",
        rows=init_rows,
    )


def get_row(session: SessionState, row_id: str) -> Row | None:
    for row in session.rows:
        if row.id == row_id:
            return row


# HTML Rendering


def homepage(session: SessionState) -> HtmlTag:
    return html(
        style=styles(
            background_color="black",
            color="white",
            padding_left=px(20),
        )
    )(
        head(
            script(src="/static/htmx.min.js"),
        ),
        body(
            form(
                h3("HTMX Demo"),
                div(
                    name_contains_input(session),
                    bulk_select_button(session),
                ),
                main_table(session),
                submit_button(session),
                style=styles(
                    display="flex",
                    flex_direction="column",
                    gap=px(12),
                ),
            ),
            p(id=RESULT_ID),
        ),
    )


def name_contains_input(session: SessionState) -> HtmlTag:
    placeholder = "Type to filter rows by name..."
    return input_(
        type="text",
        name="name_contains",
        value=session.name_contains,
        placeholder=placeholder,
        data_hx_get=add_session(f"/table/filter", session),
        data_hx_trigger="input changed delay:300ms, keyup[key=='Enter']",
        data_hx_target=f"#{TABLE_ID}",
        style=styles(width=ch(len(placeholder))),
    )


def bulk_select_button(session: SessionState) -> HtmlTag:
    all_selected = all(row.selected for row in session.rows)
    button_text = "Deselect All" if all_selected else "Select All"
    href = f"/table/{'deselect' if all_selected else 'select'}/all"
    return button(
        button_text,
        id=SELECT_ALL_ID,
        data_hx_post=add_session(href, session),
        data_hx_target=f"#{TABLE_ID}",
        data_hx_swap_oob="true",
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
                style=header_cell_style,
            ),
            th(
                "Name",
                style=header_cell_style,
            ),
        )
    )
    data_rows = tbody(
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
        data_rows,
        id=TABLE_ID,
        style=styles(
            width=px(200),
        ),
    )


def checkbox(row: Row, session: SessionState) -> HtmlTag:
    attrs = dict(
        type="checkbox",
        name="selected",
        value=row.id,
        data_hx_post=add_session(f"/table/row/{row.id}/select", session),
    )
    # need an absence of the checked attribute to render an unchecked checkbox
    if row.selected:
        attrs["checked"] = "checked"  # any string works

    return input_(**attrs)


def submit_button(session: SessionState) -> HtmlTag:
    return input_(
        type="submit",
        data_hx_post=add_session("/", session),
        data_hx_target=f"#{RESULT_ID}",
        data_hx_swap="textContent",
        style=styles(width=ch(10)),
    )
