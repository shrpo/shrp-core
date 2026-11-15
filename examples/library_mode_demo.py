from shrp_ai import CoreEngine, Request
import asyncio


async def main():
    core = CoreEngine()
    await core.initialize()
    try:
        # EchoModule is registered by default
        resp = await core.handle_request(Request("demo-1", "echo", {"hello": "world"}))
        print(resp.status)
        print(resp.result)
    finally:
        await core.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
