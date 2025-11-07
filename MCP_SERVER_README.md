# DigitalOcean MCP Server

An MCP (Model Context Protocol) server that provides tools to interact with the DigitalOcean API v2 using API token authentication.

## Features

This MCP server exposes the following DigitalOcean API operations as MCP tools:

- **Regions**: List available regions
- **Sizes**: List available droplet sizes (including GPU sizes)
- **Snapshots**: List and get snapshot information
- **Droplets**: List, get, create, and delete droplets
- **SSH Keys**: List SSH keys
- **Account**: Get account information

## Prerequisites

- Python 3.11 or higher
- DigitalOcean API token with appropriate permissions
- MCP client (e.g., Cursor, Claude Desktop)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

**Note**: If you encounter import errors with the `mcp` package, you may need to install it from the official source:
```bash
pip install git+https://github.com/modelcontextprotocol/python-sdk.git
```

Alternatively, check the [MCP Python SDK documentation](https://github.com/modelcontextprotocol/python-sdk) for the latest installation instructions.

2. Get your DigitalOcean API token:
   - Log in to your DigitalOcean account
   - Go to API → Tokens/Keys
   - Generate a new token with read/write permissions
   - Copy the token

## Configuration

### For Cursor

Add the following to your Cursor MCP configuration file (typically `~/.cursor/mcp.json` or similar):

```json
{
  "mcpServers": {
    "digitalocean": {
      "command": "python",
      "args": ["C:\\Users\\bould\\source\\GPU_Droplet_lab\\mcp_server.py"],
      "env": {
        "DIGITALOCEAN_API_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

**Important**: Replace `your-api-token-here` with your actual DigitalOcean API token.

### For Claude Desktop

Add the following to your Claude Desktop MCP configuration file (typically `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS or `%APPDATA%\\Claude\\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "digitalocean": {
      "command": "python",
      "args": ["C:\\Users\\bould\\source\\GPU_Droplet_lab\\mcp_server.py"],
      "env": {
        "DIGITALOCEAN_API_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

**Note**: Update the path to `mcp_server.py` to match your actual file location.

## Available Tools

### `do_list_regions`
List all available DigitalOcean regions.

**Parameters**: None

**Example**:
```json
{
  "name": "do_list_regions",
  "arguments": {}
}
```

### `do_list_sizes`
List all available droplet sizes.

**Parameters**:
- `gpu_only` (boolean, optional): If true, only return GPU-enabled sizes. Default: false

**Example**:
```json
{
  "name": "do_list_sizes",
  "arguments": {
    "gpu_only": true
  }
}
```

### `do_list_snapshots`
List all available snapshots in your account.

**Parameters**: None

### `do_get_snapshot`
Get information about a specific snapshot.

**Parameters**:
- `snapshot_id` (string, required): Snapshot ID or slug

**Example**:
```json
{
  "name": "do_get_snapshot",
  "arguments": {
    "snapshot_id": "snapshot-id-12345"
  }
}
```

### `do_list_droplets`
List all droplets in your account.

**Parameters**: None

### `do_get_droplet`
Get information about a specific droplet.

**Parameters**:
- `droplet_id` (integer, required): Droplet ID

**Example**:
```json
{
  "name": "do_get_droplet",
  "arguments": {
    "droplet_id": 123456789
  }
}
```

### `do_create_droplet`
Create a new droplet.

**Parameters**:
- `name` (string, required): Droplet name
- `region` (string, required): Region slug (e.g., 'nyc1', 'sfo3')
- `size` (string, required): Droplet size slug (e.g., 's-1vcpu-1gb', 'g-2vcpu-16gb')
- `image` (string, required): Image ID, snapshot ID, or image slug
- `ssh_keys` (array of strings, optional): List of SSH key IDs or fingerprints
- `tags` (array of strings, optional): List of tags
- `user_data` (string, optional): Cloud-init user data
- `monitoring` (boolean, optional): Enable monitoring. Default: false
- `ipv6` (boolean, optional): Enable IPv6. Default: false
- `private_networking` (boolean, optional): Enable private networking. Default: true

**Example**:
```json
{
  "name": "do_create_droplet",
  "arguments": {
    "name": "my-gpu-server",
    "region": "nyc1",
    "size": "g-2vcpu-16gb",
    "image": "snapshot-id-12345",
    "ssh_keys": ["key-id-1"],
    "tags": ["production", "gpu"],
    "monitoring": true,
    "private_networking": true
  }
}
```

### `do_delete_droplet`
Delete a droplet.

**Parameters**:
- `droplet_id` (integer, required): Droplet ID to delete

**Example**:
```json
{
  "name": "do_delete_droplet",
  "arguments": {
    "droplet_id": 123456789
  }
}
```

### `do_list_ssh_keys`
List all SSH keys in your account.

**Parameters**: None

### `do_get_account_info`
Get account information.

**Parameters**: None

## Usage

Once configured, you can use the MCP server through your MCP client. The tools will be available for the AI assistant to call when needed.

For example, you can ask:
- "List all my DigitalOcean droplets"
- "Create a GPU droplet in NYC1 region"
- "Show me available GPU sizes"
- "Get information about snapshot X"

## Security Notes

- **Never commit your API token** to version control
- Store your API token securely (use environment variables or secure configuration)
- The API token should have only the minimum required permissions
- Consider using read-only tokens when possible

## Troubleshooting

### Server not starting
- Verify Python 3.11+ is installed: `python --version`
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify the path to `mcp_server.py` in your configuration is correct

### Authentication errors
- Verify your `DIGITALOCEAN_API_TOKEN` is set correctly
- Check that the token has not expired
- Ensure the token has the required permissions

### API errors
- Check the error message for specific details
- Verify your account has sufficient resources/quota
- Ensure the requested resources (regions, sizes) are available

## Development

To test the server directly:

```bash
export DIGITALOCEAN_API_TOKEN="your-token"
python mcp_server.py
```

The server communicates via stdio using the MCP protocol, so it's designed to be run by an MCP client, not directly.

## License

This MCP server is provided as-is for use with the DigitalOcean API.

