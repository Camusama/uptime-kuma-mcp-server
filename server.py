from pydantic import Field
from mcp.server.fastmcp import FastMCP
from uptime_kuma_api import UptimeKumaApi, MonitorType
import os
import asyncio
from dotenv import load_dotenv
import logging

load_dotenv()


async def loginUptimeKuma():
    """登录 Uptime Kuma API"""
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
        description="监控URL列表,需要去重,且必须包含完整协议(如https://bing.com)"
    ),
):
    """批量添加多个监控器到Uptime Kuma,添加完成后返回 Uptime Kuma 的页面地址,显示出来"""
    try:
        api = await loginUptimeKuma()

        def add_single_monitor(url):
            try:
                name = url.split("//")[-1].split("/")[0]
                logger.info(f"正在添加监控器: {name} ({url})")
                response = api.add_monitor(
                    type=MonitorType.HTTP, name=name, url=url)
                logger.info(f"成功添加监控器: {name} ({url})")
                return response
            except Exception as e:
                logger.error(f"添加监控器 {url} 时出错: {str(e)}")
                return {"ok": False, "error": str(e)}

        loop = asyncio.get_event_loop()
        tasks = []
        for url in urls:
            tasks.append(loop.run_in_executor(None, add_single_monitor, url))

        responses = await asyncio.gather(*tasks)
        success_count = len([r for r in responses if r.get("ok")])
        logger.info(f"批量添加完成，成功数: {success_count}/{len(urls)}")

        return {
            "monitor_responses": responses,
            "kuma_url": os.getenv("KUMA_URL"),
            "kuma_username": os.getenv("KUMA_USERNAME"),
            "total_count": len(urls),
            "success_count": success_count,
        }
    except Exception as e:
        logger.error(f"批量添加监控器时发生错误: {str(e)}")
        raise


@mcp.tool()
async def get_monitors():
    """获取所有监控器列表，返回已裁剪字段防止上下文过长,完成后返回 Uptime Kuma 的页面地址,显示出来"""
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
        logger.error(f"获取监控器列表时发生错误: {str(e)}")
        raise


@mcp.tool()
async def delete_monitors(ids: list[int] = Field(description="要删除的监控器ID列表")):
    """批量删除多个监控器,完成后返回 Uptime Kuma 的页面地址,显示出来"""
    try:

        api = await loginUptimeKuma()

        def delete_single_monitor(id_):
            try:
                response = api.delete_monitor(id_)
                return response
            except Exception as e:
                logger.error(f"删除监控器 {id_} 时出错: {str(e)}")
                return {"msg": f"Error: {str(e)}"}

        loop = asyncio.get_event_loop()
        tasks = []
        for id_ in ids:
            tasks.append(loop.run_in_executor(
                None, delete_single_monitor, id_))

        responses = await asyncio.gather(*tasks)
        success_count = len(
            [r for r in responses if r.get("msg") == "Deleted Successfully."]
        )
        logger.info(f"批量删除完成，成功数: {success_count}/{len(ids)}")

        return {
            "delete_responses": responses,
            "deleted_ids": ids,
            "total_count": len(ids),
            "success_count": success_count,
            "kuma_url": os.getenv("KUMA_URL"),
        }
    except Exception as e:
        logger.error(f"批量删除监控器时发生错误: {str(e)}")
        raise


if __name__ == "__main__":
    mcp.run(transport="sse")
