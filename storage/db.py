from mem0 import MemoryClient
import os

api_key = os.environ.get("MEM0_API_KEY")

client = MemoryClient(api_key=api_key) if api_key else None







