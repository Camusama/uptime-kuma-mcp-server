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
async def add_monitor(name: str, url: str):
    """添加单个监控到 Uptime Kuma
    Args:
        name: 监控名称,从URL名称中获取或推断
        url: 监控URL,注意要带完整协议
    """
    api = await loginUptimeKuma()
    response = api.add_monitor(type=MonitorType.HTTP, name=name, url=url)
    return {
        "monitor_response": response,
        "kuma_url": os.getenv("KUMA_URL"),
        "kuma_username": os.getenv("KUMA_USERNAME")
    }

@mcp.tool()
async def add_monitors(urls: list[str]):
    """批量添加多个监控器到Uptime Kuma,注意对 url 列表去重
    Args:
        urls: 监控URL列表,注意要带完整协议
    """
    api = await loginUptimeKuma()

    def add_single_monitor(url):
        name = url.split('//')[-1].split('/')[0]
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
        "success_count": len([r for r in responses if r.get("ok")])
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
async def delete_monitor(id_: int):
    """删除指定监控器
    Args:
        id_: 要删除的监控器ID
    """
    api = await loginUptimeKuma()
    response = api.delete_monitor(id_)
    return {
        "delete_response": response,
        "deleted_id": id_,
    }

@mcp.tool()
async def delete_monitors(ids: list[int]):
    """批量删除多个监控器
    Args:
        ids: 要删除的监控器ID列表
    """
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
        "success_count": len([r for r in responses if r.get("msg") == "Deleted Successfully."])
    }

if __name__ == "__main__":
    mcp.run(transport="sse")
