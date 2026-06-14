# Simple HTBuilder + HTMX + FastAPI Example

A simple example of an all-in-one python webapp with:
    1. [HTBuilder](https://github.com/tvst/htbuilder) for functional HTML generation.
    2. [HTMX](https://htmx.org/) for enriching HTML elements with the ability to trigger HTTP endpoints, and swap out other elements with the response.
    3. [FastAPI](https://fastapi.tiangolo.com/) for the backend server.

For more details, see the [companion post](https://ori-livson.com/posts/simple-htbuilder-htmx-fastapi-combo/) on my blog.

## Instructions:

To setup:
```bash
pip install -r requirements.txt
```

To run:
```bash
export PYTHONPATH=$(pwd)     
uvicorn src.main:app --reload --port 8001
```
or via the following vscode launch config:
```json
{
  "configurations": [
    {
      "name": "Start API",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      },
      "args": ["src.main:app", "--reload", "--port", "8001"]
    }
  ]
}
```