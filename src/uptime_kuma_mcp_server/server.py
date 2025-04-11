from pydantic import Field
from mcp.server.fastmcp import FastMCP
from uptime_kuma_api import UptimeKumaApi, MonitorType
import os
import asyncio
from dotenv import load_dotenv
import logging


load_dotenv()


async def loginUptimeKuma():
    """Login to Uptime Kuma API"""
    api = UptimeKumaApi(os.getenv("KUMA_URL"))
    api.login(os.getenv("KUMA_USERNAME"), os.getenv("KUMA_PASSWORD"))
    return api


mcp = FastMCP("UptimeKumaMcpServer")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@mcp.tool()
async def add_monitors(
    urls: list[str] = Field(
        description="List of monitoring URLs, must be deduplicated and include full protocol (e.g. https://bing.com)"
    ),
):
    """Batch add multiple monitors to Uptime Kuma, returns Uptime Kuma page URL after completion"""
    try:
        api = await loginUptimeKuma()

        def add_single_monitor(url):
            try:
                name = url.split("//")[-1].split("/")[0]
                logger.info(f"Adding monitor: {name} ({url})")
                response = api.add_monitor(type=MonitorType.HTTP, name=name, url=url)
                logger.info(f"Successfully added monitor: {name} ({url})")
                return response
            except Exception as e:
                logger.error(f"Error adding monitor {url}: {str(e)}")
                return {"ok": False, "error": str(e)}

        loop = asyncio.get_event_loop()
        tasks = []
        for url in urls:
            tasks.append(loop.run_in_executor(None, add_single_monitor, url))

        responses = await asyncio.gather(*tasks)
        success_count = len([r for r in responses if r.get("ok")])
        logger.info(f"Batch addition completed, success count: {success_count}/{len(urls)}")

        return {
            "monitor_responses": responses,
            "kuma_url": os.getenv("KUMA_URL"),
            "kuma_username": os.getenv("KUMA_USERNAME"),
            "total_count": len(urls),
            "success_count": success_count,
        }
    except Exception as e:
        logger.error(f"Error occurred during batch monitor addition: {str(e)}")
        raise


@mcp.tool()
async def get_monitors():
    """Get all monitors list, returns trimmed fields to prevent long context, returns Uptime Kuma page URL after completion"""
    try:
        api = await loginUptimeKuma()
        monitors = api.get_monitors()
        return {
            "monitors": [
                {
                    "id": m["id"],
                    "url": m["url"],
                    "type": m["type"],
                    "active": m["active"],
                }
                for m in monitors
            ],
            "total_count": len(monitors),
            "kuma_url": os.getenv("KUMA_URL"),
        }
    except Exception as e:
        logger.error(f"Error occurred while getting monitor list: {str(e)}")
        raise


@mcp.tool()
async def delete_monitors(ids: list[int] = Field(description="List of monitor IDs to delete")):
    """Batch delete multiple monitors, returns Uptime Kuma page URL after completion"""
    try:
        api = await loginUptimeKuma()

        def delete_single_monitor(id_):
            try:
                response = api.delete_monitor(id_)
                return response
            except Exception as e:
                logger.error(f"Error deleting monitor {id_}: {str(e)}")
                return {"msg": f"Error: {str(e)}"}

        loop = asyncio.get_event_loop()
        tasks = []
        for id_ in ids:
            tasks.append(loop.run_in_executor(None, delete_single_monitor, id_))

        responses = await asyncio.gather(*tasks)
        success_count = len(
            [r for r in responses if r.get("msg") == "Deleted Successfully."]
        )
        logger.info(f"Batch deletion completed, success count: {success_count}/{len(ids)}")

        return {
            "delete_responses": responses,
            "deleted_ids": ids,
            "total_count": len(ids),
            "success_count": success_count,
            "kuma_url": os.getenv("KUMA_URL"),
        }
    except Exception as e:
        logger.error(f"Error occurred during batch monitor deletion: {str(e)}")
        raise


def main():
    mcp.run(transport="stdio")


def run_sse():
    mcp.run(transport="sse")


if __name__ == "__main__":
    main()
