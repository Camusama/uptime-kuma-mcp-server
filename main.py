from uptime_kuma_api import UptimeKumaApi, MonitorType
import os
from dotenv import load_dotenv

load_dotenv()

api = UptimeKumaApi(os.getenv("KUMA_URL"))
api.login(os.getenv("KUMA_USERNAME"), os.getenv("KUMA_PASSWORD"))

result = api.add_monitor(type=MonitorType.HTTP, name="Bing", url="https://bing.com")
print(result)


# def main():
#     print("Hello from uptime-kuma-mcp-server!")


# if __name__ == "__main__":
#     main()
