from pydantic import Field
from mcp.server.fastmcp import FastMCP
from uptime_kuma_api import UptimeKumaApi, MonitorType
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()


async def loginUptimeKuma():
    """登录 Uptime Kuma API"""
    api = UptimeKumaApi(os.getenv("KUMA_URL"))
    api.login(os.getenv("KUMA_USERNAME"), os.getenv("KUMA_PASSWORD"))
    return api


mcp = FastMCP("UptimeKumaMcpServer")


@mcp.tool()
async def add_monitor(
    name: str = Field(description="监控名称,从URL名称中获取或推断"),
    url: str = Field(description="监控URL,必须包含完整协议(如https://bing.com)"),
):
    """添加单个监控到 Uptime Kuma"""
    api = await loginUptimeKuma()
    response = api.add_monitor(type=MonitorType.HTTP, name=name, url=url)
    return {
        "monitor_response": response,
        "kuma_url": os.getenv("KUMA_URL"),
        "kuma_username": os.getenv("KUMA_USERNAME"),
    }


@mcp.tool()
async def add_monitors(
    urls: list[str] = Field(
        description="监控URL列表,需要去重,且必须包含完整协议(如https://bing.com)"
    ),
):
    """批量添加多个监控器到Uptime Kuma"""
    api = await loginUptimeKuma()

    def add_single_monitor(url):
        name = url.split("//")[-1].split("/")[0]
        return api.add_monitor(type=MonitorType.HTTP, name=name, url=url)

    loop = asyncio.get_event_loop()
    tasks = []
    for url in urls:
        tasks.append(loop.run_in_executor(None, add_single_monitor, url))

    responses = await asyncio.gather(*tasks)

    return {
        "monitor_responses": responses,
        "kuma_url": os.getenv("KUMA_URL"),
        "kuma_username": os.getenv("KUMA_USERNAME"),
        "total_count": len(urls),
        "success_count": len([r for r in responses if r.get("ok")]),
    }


@mcp.tool()
async def get_monitors():
    """获取所有监控器列表"""
    api = await loginUptimeKuma()
    monitors = api.get_monitors()
    return {
        "monitors": monitors,
        "total_count": len(monitors),
    }


@mcp.tool()
async def delete_monitor(id_: int = Field(description="要删除的监控器ID")):
    """删除指定监控器"""
    api = await loginUptimeKuma()
    response = api.delete_monitor(id_)
    return {
        "delete_response": response,
        "deleted_id": id_,
    }


@mcp.tool()
async def delete_monitors(ids: list[int] = Field(description="要删除的监控器ID列表")):
    """批量删除多个监控器"""
    api = await loginUptimeKuma()

    def delete_single_monitor(id_):
        return api.delete_monitor(id_)

    loop = asyncio.get_event_loop()
    tasks = []
    for id_ in ids:
        tasks.append(loop.run_in_executor(None, delete_single_monitor, id_))

    responses = await asyncio.gather(*tasks)

    return {
        "delete_responses": responses,
        "deleted_ids": ids,
        "total_count": len(ids),
        "success_count": len(
            [r for r in responses if r.get("msg") == "Deleted Successfully."]
        ),
    }


if __name__ == "__main__":
    mcp.run(transport="sse")
