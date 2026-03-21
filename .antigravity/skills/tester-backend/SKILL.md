# Backend Test Engineer

## Role

Write pytest tests for Python modules.

## Rules

- One test file per module
- Mock all external calls — Groq, GitHub API, load_dotenv
- Use patch.dict for env vars
- Test happy path AND failure cases
- Group with section comments
- Descriptive names: test_function_condition_expected

## Patterns

### Mocking env vars

```python
from unittest.mock import patch
with patch("utils.load_dotenv"):
    with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}):
        load_env()
```

### Mocking httpx

```python
import respx
import httpx

@respx.mock
def test_github_api():
    respx.get("https://api.github.com/...").mock(
        return_value=httpx.Response(200, json=[...])
    )
```

### FastAPI test client

```python
from fastapi.testclient import TestClient
from api.api import app

client = TestClient(app)
response = client.post("/summarise", json={...})
assert response.status_code == 200
```

## Stack

- pytest
- unittest.mock
- respx for httpx mocking
- fastapi.testclient
