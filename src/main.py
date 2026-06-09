import os
from typing import Annotated
from uuid import uuid4

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.ui import (
    HtmlTag,
    Row,
    SessionState,
    bulk_select_button,
    get_row,
    homepage,
    initialise_session,
    main_table,
)
from src.utils import cache, uncache

app = FastAPI()

# Local store of sessions
SESSIONS: dict[str, SessionState] = {}
SESSIONS_DIR = "sessions"

os.makedirs(SESSIONS_DIR, exist_ok=True)
for session_id in os.listdir(SESSIONS_DIR):
    SESSIONS[session_id] = uncache(f"{SESSIONS_DIR}/{session_id}")


@app.get("/")
def render_homepage(session_id: str | None = None) -> HTMLResponse:
    if not session_id:
        session_id = generate_session_id()
        return RedirectResponse(
            url=f"/?session_id={session_id}",
        )

    if session_id not in SESSIONS:
        raise HTTPException(
            status_code=404,
            detail=f"Session ID {session_id} not found.",
        )

    return response(
        dom=homepage(session=SESSIONS[session_id]),
    )


@app.post("/")
def submit_selected(
    selected: Annotated[list[str], Form(default_factory=list)],
    session_id: str,
) -> str:
    if not selected:
        return f"No Rows Selected"

    session = SESSIONS[session_id]
    names = []
    for row_id in selected:
        if row := get_row(session=session, row_id=row_id):
            names.append(row.name)
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Row ID {row_id} not found in session",
            )

    # Print comma separated names with an "and" before the last name
    if len(names) == 1:
        names_str = names[0]
    else:
        names_str = ", ".join(names[:-1]) + " and " + names[-1]

    return f"Submitted {names_str}"


@app.get("/table/filter")
def filter_names(name_contains: str, session_id: str) -> HTMLResponse:
    # Render a table with the updated name filter
    session = SESSIONS[session_id]
    session.name_contains = name_contains
    save_session(session)
    return response(
        dom=main_table(session=session),
    )


# Various implementations of:
# 1. Updating the session state to note selection of row @ row_id
# 2. Rerendering the bulk_select_button depending on whether
#    All vs not all rows are selected


@app.post("/table/row/{row_id}/select")
def select(row_id: str, session_id: str) -> HTMLResponse:
    session = SESSIONS[session_id]
    if row := get_row(session=session, row_id=row_id):
        row.selected = not row.selected
        save_session(session)
        return oob_response(
            dom=None,
            oob=bulk_select_button(session),
        )

    raise HTTPException(
        status_code=404,
        detail=f"Row ID {row_id} not found in session",
    )


@app.post("/table/select/all")
def select(session_id: str) -> HTMLResponse:
    session = SESSIONS[session_id]
    for row in session.rows:
        row.selected = True
    save_session(session)
    return oob_response(
        dom=main_table(session),
        oob=bulk_select_button(session),
    )


@app.post("/table/deselect/all")
def select(session_id: str) -> HTMLResponse:
    session = SESSIONS[session_id]
    for row in session.rows:
        row.selected = False
    save_session(session)
    return oob_response(
        dom=main_table(session),
        oob=bulk_select_button(session),
    )


# Static resources

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return RedirectResponse(url="/static/favicon.ico")


# HTML Utils


def response(dom: HtmlTag) -> HTMLResponse:
    return HTMLResponse(content=str(dom))


def oob_response(dom: HtmlTag | None, oob: HtmlTag) -> HTMLResponse:
    return HTMLResponse(content=str(dom or "") + str(oob))


# Local Session Storage


def generate_session_id() -> str:
    result = str(uuid4())
    SESSIONS[result] = initialise_session(
        session_id=result,
        init_rows=[
            Row(id="1", name="Alice", selected=False),
            Row(id="2", name="Bob", selected=False),
            Row(id="3", name="Charlie", selected=False),
        ],
    )
    save_session(SESSIONS[result])
    return result


def save_session(session: SessionState):
    cache(obj=session, path=f"{SESSIONS_DIR}/{session.id}")
