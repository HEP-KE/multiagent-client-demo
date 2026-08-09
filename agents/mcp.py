"""Load MCP tools as LangChain tools.

The config dict maps server names to connection settings, e.g.

    {"spectra": {"transport": "streamable_http", "url": "http://127.0.0.1:8000/mcp"}}
    {"spectra": {"transport": "stdio", "command": "python",
                 "args": ["-m", "mcp_server"], "cwd": "/path/to/spectra-mcp-server"}}

Note the spelling: LangChain's adapter says "streamable_http" (underscore) while
the server CLI says --transport streamable-http (hyphen).

Our tools are stateless (everything lives in files), so we don't need a
persistent session — each tool call opens a fresh connection. Production
clients often manage long-lived sessions instead; this is the simplest thing
that works.
"""

from langchain_mcp_adapters.client import MultiServerMCPClient


async def load_tools(config: dict) -> list:
    client = MultiServerMCPClient(config)
    return await client.get_tools()
