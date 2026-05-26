<!-- markdownlint-disable MD041 MD013 -->

<p align="right">
  <a href="jobs.pt-br.md">
    <img src="https://img.shields.io/badge/leia%20em-portugu%C3%AAs-6fa86f?style=flat-square" alt="Leia em Português">
  </a>
</p>

# Jobs

Background work, framed by the bureau. Two runners and a couple of value
types. The shortcut `Form.run_pending(jobs)` covers the simple "fan out and
wait" case; the runners give you control over callbacks, timeouts, safeguards,
and pipeline rollback.

## Value types

`from glory_to_protocol.jobs import Job, JobOutcome`

### `Job`

```python
@dataclass(frozen=True, slots=True)
class Job:
    label: str
    coro_factory: Callable[[], Awaitable[None]]
    critical: bool = False
```

| Field | Purpose |
| --- | --- |
| `label` | Shown in the live ticker and in the resulting `JobOutcome.label`. |
| `coro_factory` | Factory that returns the coroutine to await. **Factory, not coroutine.** See [Why a factory](#why-a-factory). |
| `critical` | Tag-only today; reserved for future fail-fast semantics. Callers can already tag jobs (audit vs best-effort) without a later schema change. |

### `JobOutcome`

```python
@dataclass(frozen=True, slots=True)
class JobOutcome:
    label: str
    status: JobStatus
    error: BaseException | None
    duration_ms: int
```

| Field | Meaning |
| --- | --- |
| `label` | Echoes `Job.label`. |
| `status` | `JobStatus.OK` / `JobStatus.FAIL` / `JobStatus.SKIPPED`. `SKIPPED` is only set by `PipelineRunner` for unreached jobs. |
| `error` | The exception, if `status == FAIL`. |
| `duration_ms` | Wall-clock duration of the job. |

`JobStatus` is a `StrEnum` (`"pending"`, `"ok"`, `"fail"`, `"skipped"`) — string
comparisons against the old literals keep working; new code should use the enum.

## `Form.run_pending` (shortcut)

```python
import asyncio
from glory_to_protocol.jobs.types import Job
from glory_to_protocol.tui.forms import Form
from glory_to_protocol.tui import theme

async def fetch_quota() -> None:
    await asyncio.sleep(2)

jobs = [
    Job(label="fetching quota", coro_factory=fetch_quota),
    Job(label="archiving ledger", coro_factory=lambda: asyncio.sleep(3)),
]

with Form(title="sync") as form:
    form.line("Reconciling with the bureau...", style=theme.MUTED)
    outcomes = asyncio.run(form.run_pending(jobs))

for outcome in outcomes:
    print(outcome.label, outcome.status, outcome.duration_ms)
```

`run_pending` fans the jobs out as async tasks, renders a live ticker until all
reach a terminal state, and returns the outcomes. Failures are isolated —
siblings keep running. The runner never raises on individual job failure; the
caller decides how a failed background job affects the foreground stamp.

## `JobRunner`

`from glory_to_protocol.jobs import JobRunner`

Async context manager that fans out independent background jobs.
Failures are isolated.

```python
from glory_to_protocol.jobs import Job, JobOutcome, JobRunner

async def write_temp_file() -> None: ...
async def remove_temp_file(outcome: JobOutcome) -> None: ...
async def audit(outcome: JobOutcome) -> None: ...

async with JobRunner() as runner:
    runner.spawn(
        Job("stage temp file", write_temp_file),
        rollback=remove_temp_file,
        on_success=audit,
        timeout=5.0,
    )

for outcome in runner.outcomes:
    print(outcome.label, outcome.status)
```

### Constructor

| Kwarg | Default | Effect |
| --- | --- | --- |
| `max_children` | `12` | Cap on jobs registered via `spawn`. `0` disables the cap. Exceeding always raises (programmer error). |
| `on_recursion` | `RecursionPolicy.RAISE` | Behaviour when `spawn` is called after `__aexit__` begins (e.g. from a callback). |

### `spawn`

```python
def spawn(
    self,
    job: Job,
    *,
    rollback: Callable[[JobOutcome], Awaitable[None]] | None = None,
    on_success: Callable[[JobOutcome], Awaitable[None]] | None = None,
    timeout: float | None = None,
) -> JobHandle:
```

| Kwarg | Fires when | Signature |
| --- | --- | --- |
| `rollback` | job ends in `FAIL` | `async (outcome: JobOutcome) -> None` |
| `on_success` | job ends in `OK` | `async (outcome: JobOutcome) -> None` |
| `timeout` | wall-clock cap in seconds | `float` |

`rollback` and `on_success` are mutually exclusive in practice — only one runs
per job. Cancellation skips both. If a callback itself raises, the error is
logged and swallowed so it cannot mask the original outcome or break sibling
isolation.

`timeout` wraps the job's coroutine in `asyncio.wait_for`; an expired timeout
produces a `FAIL` outcome with a `TimeoutError`, which then triggers `rollback`
like any other failure.

### Cancellation

A job task receiving `CancelledError` is **not** converted into a `"fail"`
outcome; it stays pending and the `CancelledError` flows up through
`__aexit__`. If the context body raises, pending tasks are cancelled before
`gather` is awaited.

## `PipelineRunner`

`from glory_to_protocol.jobs import PipelineRunner, PipelineFailed`

Sequential counterpart to `JobRunner`. Jobs registered with `spawn` execute in
order on context exit; the first failure aborts the pipeline, triggers LIFO
rollback of previously-completed jobs, marks unreached jobs as `SKIPPED`, and
re-raises as `PipelineFailed`.

```python
from glory_to_protocol.jobs import Job, JobOutcome, PipelineFailed, PipelineRunner

async def reserve_quota() -> None: ...
async def write_ledger() -> None: ...
async def notify_director() -> None: ...

async def release_quota(o: JobOutcome) -> None: ...
async def revert_ledger(o: JobOutcome) -> None: ...

try:
    async with PipelineRunner() as p:
        p.spawn(Job("reserve quota", reserve_quota), rollback=release_quota)
        p.spawn(Job("write ledger", write_ledger), rollback=revert_ledger)
        p.spawn(Job("notify director", notify_director))
except PipelineFailed as exc:
    print(exc.failed.label, exc.rolled_back, exc.rollback_errors)
```

### Semantics

| Aspect | Behaviour |
| --- | --- |
| **Order** | Jobs run in the order they were `spawn`ed. |
| **Abort** | On first failure, no subsequent job runs; remaining handles flip to `SKIPPED`. |
| **LIFO rollback** | Successfully-completed jobs have their rollback invoked in reverse order. |
| **Rollback errors** | Logged and collected in `PipelineFailed.rollback_errors`; the chain continues regardless. |
| **First-job failure** | Nothing to undo — `rolled_back` is empty. |
| **Body exception** | If the `async with` body raises before exit, no job runs and the body's exception propagates unchanged. |

### `PipelineFailed`

| Attribute | Type | Meaning |
| --- | --- | --- |
| `failed` | `JobOutcome` | The job that broke the pipeline. |
| `rolled_back` | `list[str]` | Labels rolled back, in LIFO order. |
| `rollback_errors` | `list[tuple[str, BaseException]]` | Exceptions raised by rollback callbacks. |

Same constructor kwargs as `JobRunner` (`max_children`, `on_recursion`).

## Safeguards

Both runners share two ctor kwargs that bound fan-out and protect against
callback-induced recursion:

| Kwarg | Default | Effect |
| --- | --- | --- |
| `max_children` | `12` | Cap on jobs registered via `spawn`. `0` disables the cap. Exceeding always raises (programmer error). |
| `on_recursion` | `RecursionPolicy.RAISE` | `spawn` called after the context starts closing raises. `WARN` logs and returns a synthetic `SKIPPED` handle that is not enrolled. |

```python
from glory_to_protocol.jobs import JobRunner
from glory_to_protocol.jobs.types import RecursionPolicy

runner = JobRunner(max_children=0, on_recursion=RecursionPolicy.WARN)
```

## Why a factory?

`coro_factory` returns a coroutine on each call — it is **not** a coroutine
itself.

```python
# right
Job(label="fetch", coro_factory=fetch)
Job(label="sleep 3s", coro_factory=lambda: asyncio.sleep(3))

# wrong
Job(label="fetch", coro_factory=fetch())            # coroutine bound to current loop
Job(label="sleep 3s", coro_factory=asyncio.sleep(3))
```

Passing the coroutine directly binds it to whichever event loop is current at
construction time. That loop might not be the one the runner uses, and a
coroutine can only be awaited once — the runner spawning the same `Job` twice
would hit a runtime error. The factory contract lets each spawn produce a fresh
awaitable, bound at the right time.

## Roadmap

Today `JobRunner` and `PipelineRunner` produce Rich renderables (live regions,
stamps) that work inside `Form` and the Rich fallback. A live `JobsTicker`
widget hosted directly inside the Textual surface lands in `0.5.0`.
