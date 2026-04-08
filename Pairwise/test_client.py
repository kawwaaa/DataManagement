from fastmcp import FastMCPClient

client = FastMCPClient("http://localhost:8000")
result = client.call_tool("get_ice_cream_forecast")
print(result)
