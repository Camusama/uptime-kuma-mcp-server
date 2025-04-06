from uptime_kuma_api import UptimeKumaApi, MonitorType


api = UptimeKumaApi("https://kuma2.896324.xyz:3306")
api.login("marquezyang", "kuma123")

result = api.add_monitor(type=MonitorType.HTTP, name="Google", url="https://google.com")
print(result)


def main():
    print("Hello from uptime-kuma-mcp-server!")


if __name__ == "__main__":
    main()
