#!/usr/bin/env python3
"""
MCP Server for DigitalOcean API

This MCP server provides tools to interact with the DigitalOcean API v2
using API token authentication.
"""

import os
import sys
import json
import asyncio
from typing import Any, Optional
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    # Fallback for different package structure
    try:
        from mcp_python.server import Server
        from mcp_python.server.stdio import stdio_server
        from mcp_python.types import Tool, TextContent
    except ImportError:
        print("Error: MCP package not found. Install with: pip install mcp", file=sys.stderr)
        sys.exit(1)
import requests


class DigitalOceanAPI:
    """Wrapper class for DigitalOcean API v2 operations."""
    
    BASE_URL = "https://api.digitalocean.com/v2"
    
    def __init__(self, api_token: str):
        """
        Initialize the DigitalOcean API client.
        
        Args:
            api_token: DigitalOcean API token
        """
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[dict] = None) -> dict:
        """
        Make an API request to DigitalOcean.
        
        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint (without base URL)
            data: Optional JSON data for POST/PUT requests
            
        Returns:
            JSON response as dictionary
            
        Raises:
            Exception: If API request fails
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.headers)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_msg = f"API Error: {e}"
            if hasattr(e.response, 'text'):
                try:
                    error_data = e.response.json()
                    if 'message' in error_data:
                        error_msg = f"API Error: {error_data['message']}"
                except:
                    error_msg = f"API Error: {e.response.text}"
            raise Exception(error_msg) from e
    
    def get_regions(self) -> list:
        """Get list of available regions."""
        response = self._make_request("GET", "/regions")
        return response.get("regions", [])
    
    def get_sizes(self) -> list:
        """Get list of available droplet sizes."""
        response = self._make_request("GET", "/sizes")
        return response.get("sizes", [])
    
    def get_gpu_sizes(self) -> list:
        """Get list of available GPU droplet sizes."""
        sizes = self.get_sizes()
        gpu_sizes = [size for size in sizes if size.get("description", "").lower().find("gpu") != -1]
        return gpu_sizes
    
    def get_images(self) -> list:
        """Get list of available images."""
        response = self._make_request("GET", "/images")
        return response.get("images", [])
    
    def get_snapshots(self) -> list:
        """Get list of available snapshots."""
        images = self.get_images()
        snapshots = [img for img in images if img.get("type") == "snapshot"]
        return snapshots
    
    def get_snapshot(self, snapshot_id: str) -> dict:
        """Get snapshot information by ID."""
        response = self._make_request("GET", f"/snapshots/{snapshot_id}")
        return response.get("snapshot", {})
    
    def get_droplets(self) -> list:
        """Get list of all droplets."""
        response = self._make_request("GET", "/droplets")
        return response.get("droplets", [])
    
    def get_droplet(self, droplet_id: int) -> dict:
        """Get droplet information by ID."""
        response = self._make_request("GET", f"/droplets/{droplet_id}")
        return response.get("droplet", {})
    
    def create_droplet(
        self,
        name: str,
        region: str,
        size: str,
        image: str,
        ssh_keys: Optional[list] = None,
        tags: Optional[list] = None,
        user_data: Optional[str] = None,
        monitoring: bool = False,
        ipv6: bool = False,
        private_networking: bool = True
    ) -> dict:
        """Create a new droplet."""
        droplet_data = {
            "name": name,
            "region": region,
            "size": size,
            "image": image,
            "monitoring": monitoring,
            "ipv6": ipv6,
            "private_networking": private_networking
        }
        
        if ssh_keys:
            droplet_data["ssh_keys"] = ssh_keys
        if tags:
            droplet_data["tags"] = tags
        if user_data:
            droplet_data["user_data"] = user_data
        
        response = self._make_request("POST", "/droplets", data=droplet_data)
        return response.get("droplet", {})
    
    def delete_droplet(self, droplet_id: int) -> dict:
        """Delete a droplet."""
        response = self._make_request("DELETE", f"/droplets/{droplet_id}")
        return response
    
    def get_ssh_keys(self) -> list:
        """Get list of SSH keys."""
        response = self._make_request("GET", "/account/keys")
        return response.get("ssh_keys", [])
    
    def get_account_info(self) -> dict:
        """Get account information."""
        response = self._make_request("GET", "/account")
        return response.get("account", {})


# Initialize the MCP server
server = Server("digitalocean-mcp")

# Global API client (will be initialized with token from environment)
api_client: Optional[DigitalOceanAPI] = None


def get_api_client() -> DigitalOceanAPI:
    """Get or initialize the DigitalOcean API client."""
    global api_client
    if api_client is None:
        api_token = os.getenv("DIGITALOCEAN_API_TOKEN")
        if not api_token:
            raise ValueError("DIGITALOCEAN_API_TOKEN environment variable is not set")
        api_client = DigitalOceanAPI(api_token)
    return api_client


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="do_list_regions",
            description="List all available DigitalOcean regions",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="do_list_sizes",
            description="List all available droplet sizes (including GPU sizes)",
            inputSchema={
                "type": "object",
                "properties": {
                    "gpu_only": {
                        "type": "boolean",
                        "description": "If true, only return GPU-enabled sizes",
                        "default": False
                    }
                }
            }
        ),
        Tool(
            name="do_list_snapshots",
            description="List all available snapshots",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="do_get_snapshot",
            description="Get information about a specific snapshot by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "snapshot_id": {
                        "type": "string",
                        "description": "Snapshot ID or slug"
                    }
                },
                "required": ["snapshot_id"]
            }
        ),
        Tool(
            name="do_list_droplets",
            description="List all droplets in your account",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="do_get_droplet",
            description="Get information about a specific droplet by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "droplet_id": {
                        "type": "integer",
                        "description": "Droplet ID"
                    }
                },
                "required": ["droplet_id"]
            }
        ),
        Tool(
            name="do_create_droplet",
            description="Create a new droplet",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Droplet name"
                    },
                    "region": {
                        "type": "string",
                        "description": "Region slug (e.g., 'nyc1', 'sfo3')"
                    },
                    "size": {
                        "type": "string",
                        "description": "Droplet size slug (e.g., 's-1vcpu-1gb', 'g-2vcpu-16gb')"
                    },
                    "image": {
                        "type": "string",
                        "description": "Image ID, snapshot ID, or image slug"
                    },
                    "ssh_keys": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of SSH key IDs or fingerprints"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of tags"
                    },
                    "user_data": {
                        "type": "string",
                        "description": "Optional cloud-init user data"
                    },
                    "monitoring": {
                        "type": "boolean",
                        "description": "Enable monitoring",
                        "default": False
                    },
                    "ipv6": {
                        "type": "boolean",
                        "description": "Enable IPv6",
                        "default": False
                    },
                    "private_networking": {
                        "type": "boolean",
                        "description": "Enable private networking",
                        "default": True
                    }
                },
                "required": ["name", "region", "size", "image"]
            }
        ),
        Tool(
            name="do_delete_droplet",
            description="Delete a droplet by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "droplet_id": {
                        "type": "integer",
                        "description": "Droplet ID to delete"
                    }
                },
                "required": ["droplet_id"]
            }
        ),
        Tool(
            name="do_list_ssh_keys",
            description="List all SSH keys in your account",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="do_get_account_info",
            description="Get account information",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    try:
        api = get_api_client()
    except ValueError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    try:
        if name == "do_list_regions":
            regions = api.get_regions()
            return [TextContent(type="text", text=json.dumps(regions, indent=2))]
        
        elif name == "do_list_sizes":
            gpu_only = arguments.get("gpu_only", False)
            if gpu_only:
                sizes = api.get_gpu_sizes()
            else:
                sizes = api.get_sizes()
            return [TextContent(type="text", text=json.dumps(sizes, indent=2))]
        
        elif name == "do_list_snapshots":
            snapshots = api.get_snapshots()
            return [TextContent(type="text", text=json.dumps(snapshots, indent=2))]
        
        elif name == "do_get_snapshot":
            snapshot_id = arguments.get("snapshot_id")
            snapshot = api.get_snapshot(snapshot_id)
            return [TextContent(type="text", text=json.dumps(snapshot, indent=2))]
        
        elif name == "do_list_droplets":
            droplets = api.get_droplets()
            return [TextContent(type="text", text=json.dumps(droplets, indent=2))]
        
        elif name == "do_get_droplet":
            droplet_id = arguments.get("droplet_id")
            droplet = api.get_droplet(droplet_id)
            return [TextContent(type="text", text=json.dumps(droplet, indent=2))]
        
        elif name == "do_create_droplet":
            droplet = api.create_droplet(
                name=arguments["name"],
                region=arguments["region"],
                size=arguments["size"],
                image=arguments["image"],
                ssh_keys=arguments.get("ssh_keys"),
                tags=arguments.get("tags"),
                user_data=arguments.get("user_data"),
                monitoring=arguments.get("monitoring", False),
                ipv6=arguments.get("ipv6", False),
                private_networking=arguments.get("private_networking", True)
            )
            return [TextContent(type="text", text=json.dumps(droplet, indent=2))]
        
        elif name == "do_delete_droplet":
            droplet_id = arguments.get("droplet_id")
            result = api.delete_droplet(droplet_id)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "do_list_ssh_keys":
            ssh_keys = api.get_ssh_keys()
            return [TextContent(type="text", text=json.dumps(ssh_keys, indent=2))]
        
        elif name == "do_get_account_info":
            account = api.get_account_info()
            return [TextContent(type="text", text=json.dumps(account, indent=2))]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Main entry point for the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())

