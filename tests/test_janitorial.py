from __future__ import annotations

import typer

from glory_to_protocol.jobs.runner import JobHandle
from glory_to_protocol.jobs.runner import JobRunner
from glory_to_protocol.jobs.types import Job
from glory_to_protocol.jobs.types import JobOutcome
from glory_to_protocol.tui.help import ProtocolTyperCommand
from glory_to_protocol.tui.help import ProtocolTyperGroup
from glory_to_protocol.typer import ProtocolTyper
from glory_to_protocol.typer import make_app


def test_should_derive_outcomes_from_handles_when_outcomes_property_accessed() -> None:
    import asyncio

    async def ok() -> None:
        await asyncio.sleep(0)

    async def driver() -> JobRunner:
        async with JobRunner() as runner:
            runner.spawn(Job("alpha", ok))
            runner.spawn(Job("beta", ok))
        return runner

    runner = asyncio.run(driver())
    labels = [o.label for o in runner.outcomes]
    assert labels == ["alpha", "beta"]


def test_should_expose_slots_when_inspecting_handle_and_types() -> None:
    handle = JobHandle(label="x")
    assert hasattr(JobHandle, "__slots__")
    assert hasattr(Job, "__slots__")
    assert hasattr(JobOutcome, "__slots__")
    assert handle.label == "x"


def test_should_apply_protocol_help_to_subapp_when_added_via_add_typer() -> None:
    parent: ProtocolTyper = make_app(name="parent")
    child = typer.Typer(name="child")
    parent.add_typer(child)
    registered = parent.registered_groups[-1]
    assert registered.typer_instance is child
    assert registered.cls is ProtocolTyperGroup


def test_should_apply_protocol_command_class_when_command_decorator_used() -> None:
    app: ProtocolTyper = make_app(name="cmd-app")

    @app.command("greet")
    def _greet() -> None:
        pass

    assert app.registered_commands[-1].cls is ProtocolTyperCommand
