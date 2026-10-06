# enterprise-tool-calling-agent-platform — interview questions and answers

[README](README.md) · [Project architecture](PROJECT_ARCHITECTURE.md)

Answers below use this repository’s files and implementation. They distinguish existing behavior from suggested extensions; source links let you verify each walkthrough.

## 1. What problem does enterprise-tool-calling-agent-platform address, and what can you demonstrate?

Enterprise allowlist of read tools. Apply refused.

I would demonstrate the linked implementation or examples and distinguish that evidence from any planned production features. Start with [`README.md`](README.md).

## 2. How is this repository organized?

- [`src/enttools/main.py`](src/enttools/main.py): Implementation or supporting configuration.
- [`src/enttools/ops.py`](src/enttools/ops.py): Implementation or supporting configuration.
- [`src/enttools/mcp.py`](src/enttools/mcp.py): Implementation or supporting configuration.
- [`requirements.txt`](requirements.txt): Implementation or supporting configuration.
- [`src/enttools/__init__.py`](src/enttools/__init__.py): Implementation or supporting configuration.
- [`Dockerfile`](Dockerfile): Container build/service configuration.
- [`Makefile`](Makefile): Implementation or supporting configuration.
- [`docker-compose.yml`](docker-compose.yml): Container build/service configuration.

[PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) contains the component diagram and the implementation walkthrough.

## 3. Can you walk through `call` and explain the decision it makes?

The main walkthrough here is `call(name, arguments)` in [`src/enttools/mcp.py`](src/enttools/mcp.py#L13).

```python
def call(name, arguments):
    if name not in TOOLS:
        raise InputError(f"unknown tool: {name}")
    blob = " ".join(str(v) for v in (arguments or {}).values()).lower() + " " + name
    if any(word in blob for word in FORBIDDEN):
        return {"ok": False, "reason": "apply and delete are refused", "applied": False}
    return {"ok": True, "tool": name, "echo": arguments or {}, "applied": False}
```

The implementation calls `' '.join`, `' '.join((str(v) for v in (arguments or {}).values())).lower`, `(arguments or {}).values`, `InputError`, `any`, `str`. In an interview, trace those calls in execution order using a fixture input.

## 4. What responsibility does `list_tools` have?

`list_tools()` is defined in [`src/enttools/mcp.py`](src/enttools/mcp.py#L9).

Its return expressions include:

- `{'tools': TOOLS}`

## 5. What input validation and failure behavior are implemented?

Explicit failure paths include:

- `HTTPException(status_code=422, detail=str(exc))` in [`src/enttools/main.py`](src/enttools/main.py#L24).
- `InputError(f'unknown tool: {name}')` in [`src/enttools/mcp.py`](src/enttools/mcp.py#L15).
- `HTTPException(status_code=404, detail='workspace not found')` in [`src/enttools/ops.py`](src/enttools/ops.py#L77).
- `HTTPException(status_code=404, detail='job not found')` in [`src/enttools/ops.py`](src/enttools/ops.py#L100).
- `HTTPException(status_code=404, detail='job not found')` in [`src/enttools/ops.py`](src/enttools/ops.py#L109).
- `HTTPException(status_code=403, detail='production apply is disabled in this lab')` in [`src/enttools/ops.py`](src/enttools/ops.py#L113).

I would test both the condition that reaches each exception and the caller that translates it. An explicit raise does not mean every malformed input or dependency failure is handled.

## 6. Which test would you use to demonstrate correctness?

[`tests/test_mcp.py`](tests/test_mcp.py#L7) contains `test_lists_and_refuses_apply`:

```python
def test_lists_and_refuses_apply():
    assert "policy.check" in client.get("/tools").json()["tools"]
    ok = client.post("/call", json={"name": "policy.check", "arguments": {"q": "status"}}).json()
    assert ok["ok"] is True
    assert ok["applied"] is False
    refused = client.post("/call", json={"name": "catalog.search", "arguments": {"cmd": "kubectl apply"}}).json()
    assert refused["ok"] is False
```

This is a concrete regression example from the repository. Its assertions establish that case; they do not establish behavior for every input or under production load.

## 7. What HTTP interface does the code expose?

- `GET /healthz` → `healthz` in [`src/enttools/main.py`](src/enttools/main.py#L10).
- `GET /tools` → `tools` in [`src/enttools/main.py`](src/enttools/main.py#L15).
- `POST /call` → `post_call` in [`src/enttools/main.py`](src/enttools/main.py#L20).
- `GET /readyz` → `readyz` in [`src/enttools/ops.py`](src/enttools/ops.py#L74).
- `POST /workspaces` → `create_workspace` in [`src/enttools/ops.py`](src/enttools/ops.py#L80).
- `GET /workspaces` → `list_workspaces` in [`src/enttools/ops.py`](src/enttools/ops.py#L98).
- `POST /workspaces/{workspace_id}/jobs` → `create_job` in [`src/enttools/ops.py`](src/enttools/ops.py#L106).
- `GET /jobs/{job_id}` → `get_job` in [`src/enttools/ops.py`](src/enttools/ops.py#L130).

These are literal decorators. Application/router prefixes, authentication, and middleware must be checked in the corresponding setup code.

## 8. Where does state live, and what happens with multiple workers?

Module-level containers include `TOOLS` in [`src/enttools/mcp.py`](src/enttools/mcp.py); `_WORKSPACES`, `_JOBS`, `_AUDIT`, `_METRICS` in [`src/enttools/ops.py`](src/enttools/ops.py).

These containers belong to a Python process. Inspect which are constant fixtures and which are mutated. Mutable process state needs an explicit shared-storage or synchronization strategy before multiple workers can provide consistent behavior.

## 9. How would another engineer reproduce your walkthrough?

Start from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

These commands follow repository manifests; environment setup and command results still need to be checked on the target machine.

## 10. What does automation verify, and what does it not prove?

Inspect [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for triggers, permissions, and job commands. I would name the checks that those definitions run and show the latest run separately. A workflow definition alone does not establish a successful deployment, security review, or production SLO.

## 11. How would you present this project in a Forward Deployed Engineer interview?

Start with the user and operational problem described in [`README.md`](README.md). Explain one constraint that changes the implementation, show the linked code or example, and walk through a success case and a failure case. Agree on a measurable acceptance criterion before expanding the solution, and leave a handoff with data boundaries and rollback ownership. Any proposed production or business metric should be identified as a target until measured.

## 12. What is the input-to-output contract of `call`?

In [`src/enttools/mcp.py`](src/enttools/mcp.py#L13), `call(name, arguments)` receives the inputs. The function computes these intermediate values:

- `blob = ' '.join((str(v) for v in (arguments or {}).values())).lower() + ' ' + name`

Its result is defined by:

- `{'ok': True, 'tool': name, 'echo': arguments or {}, 'applied': False}`
- `{'ok': False, 'reason': 'apply and delete are refused', 'applied': False}`

## 13. Which decision rules or boundary conditions should an interviewer challenge?

The implementation in [`src/enttools/mcp.py`](src/enttools/mcp.py#L13) branches on:

- `name not in TOOLS`
- `any((word in blob for word in FORBIDDEN))`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.

## 14. What does the operations plane add, and where is its limit?

[`src/enttools/ops.py`](src/enttools/ops.py) declares `GET /readyz`, `POST /workspaces`, `GET /workspaces`, `POST /workspaces/{workspace_id}/jobs`, `GET /jobs/{job_id}`, `POST /jobs/{job_id}/approve`, `GET /audit`, `GET /metrics`. Inspect the application’s `include_router` call for its URL prefix.

Its state containers are `_WORKSPACES`, `_JOBS`, `_AUDIT`, `_METRICS`. The job-approval handler defines whether a target is accepted or refused; check that branch and the associated tests instead of treating a recorded job as a successful infrastructure apply.
