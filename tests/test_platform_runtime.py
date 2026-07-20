import asyncio

from custom_components.btdoor_security_plus.core import (
    BTDoorPlatformRuntime,
    LifecycleState,
)


def test_runtime_lifecycle_order() -> None:
    calls: list[str] = []

    async def start_one() -> None:
        calls.append("start-one")

    async def stop_one() -> None:
        calls.append("stop-one")

    async def start_two() -> None:
        calls.append("start-two")

    async def stop_two() -> None:
        calls.append("stop-two")

    runtime = BTDoorPlatformRuntime()
    runtime.register(start=start_one, stop=stop_one)
    runtime.register(start=start_two, stop=stop_two)
    asyncio.run(runtime.async_start())
    asyncio.run(runtime.async_stop())

    assert calls == ["start-one", "start-two", "stop-two", "stop-one"]
    assert runtime.state is LifecycleState.STOPPED
