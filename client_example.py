import asyncio
from fastmcp import Client

async def main():
    # The client connects to the Streamable HTTP endpoint of the FastMCP server.
    # The default URL is http://127.0.0.1:8000/mcp/
    # Ensure your server in gateway/main.py is running first.
    client = Client("http://127.0.0.1:8000/mcp/")

    async with client:
        print("Successfully connected to the AD-Context server.")
        
        # Example: Calling the 'search_memory' tool
        try:
            query = "What do you remember about my preferences?"
            print(f"\nCalling 'search_memory' with query: '{query}'")
            result = await client.call_tool("search_memory", {"query_text": query})
            print("Server response:")
            print(result.data)
        except Exception as e:
            print(f"An error occurred while calling the tool: {e}")

        # Example: Calling the 'add_memory' tool
        try:
            memory_text = "I prefer dark mode for my applications."
            print(f"\nCalling 'add_memory' with text: '{memory_text}'")
            result = await client.call_tool("add_memory", {"text": memory_text})
            print("Server response:")
            print(result.data)
        except Exception as e:
            print(f"An error occurred while calling the tool: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 