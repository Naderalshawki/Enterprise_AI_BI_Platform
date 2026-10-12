import asyncio

from src.bootstrap import _build_factory
from src.modules.llm.infrastructure.health.health_monitor import HealthMonitor


async def main():
    print("=" * 50)
    print("HEALTH MONITOR TEST")
    print("=" * 50)

    factory = _build_factory()

    print("\nRegistered providers:")

    for provider in factory.providers.values():
        print(f"- {provider.provider_name}")

    monitor = HealthMonitor(factory)

    print("\nChecking provider health...\n")

    results = await monitor.check_all()

    for result in results:
        print(
            f"{result.provider}: "
            f"{result.status.value}"
            + (
                f" | Error: {result.error}"
                if result.error
                else ""
            )
        )

    print("\n" + "=" * 50)
    print("HEALTH MONITOR TEST COMPLETED")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())