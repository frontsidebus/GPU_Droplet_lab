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

- Python 3.11 or higher (for local installation)
- OR Docker and Docker Compose (for containerized installation)
- DigitalOcean API token with appropriate permissions
- MCP client (e.g., Cursor, Claude Desktop)

## Setting Up Your DigitalOcean API Token

The MCP server requires a DigitalOcean API token for authentication. You can provide it via environment variable or command-line options. Setting it as an environment variable is recommended for security and convenience.

### Getting Your API Token

1. Log in to your DigitalOcean account
2. Navigate to [API → Tokens/Keys](https://cloud.digitalocean.com/account/api/tokens)
3. Click "Generate New Token"
4. Provide a descriptive name (e.g., "MCP Server")
5. Set the desired expiration period
6. Assign the necessary scopes/permissions
7. Click "Generate Token" and **copy the token immediately** (it won't be shown again)

### Setting the Environment Variable

#### Linux/macOS (Bash/Zsh)

**Temporary (current session only):**
```bash
export DIGITALOCEAN_API_TOKEN="your-api-token-here"
```

**Permanent (add to shell profile):**
```bash
# Add to ~/.bashrc (Bash) or ~/.zshrc (Zsh)
echo 'export DIGITALOCEAN_API_TOKEN="your-api-token-here"' >> ~/.bashrc

# Reload your shell configuration
source ~/.bashrc
```

**Verify it's set:**
```bash
echo $DIGITALOCEAN_API_TOKEN
```

#### Windows (PowerShell)

**Temporary (current session only):**
```powershell
$env:DIGITALOCEAN_API_TOKEN = "your-api-token-here"
```

**Permanent (User-level environment variable):**
```powershell
# Set for current user
[System.Environment]::SetEnvironmentVariable('DIGITALOCEAN_API_TOKEN', 'your-api-token-here', 'User')

# Restart PowerShell or reload environment
$env:DIGITALOCEAN_API_TOKEN = [System.Environment]::GetEnvironmentVariable('DIGITALOCEAN_API_TOKEN', 'User')
```

**Via System Properties (GUI):**
1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Go to "Advanced" tab → "Environment Variables"
3. Under "User variables", click "New"
4. Variable name: `DIGITALOCEAN_API_TOKEN`
5. Variable value: `your-api-token-here`
6. Click "OK" on all dialogs
7. Restart your terminal/PowerShell

**Verify it's set:**
```powershell
echo $env:DIGITALOCEAN_API_TOKEN
```

#### Windows (Command Prompt)

**Temporary (current session only):**
```cmd
set DIGITALOCEAN_API_TOKEN=your-api-token-here
```

**Permanent (User-level environment variable):**
```cmd
setx DIGITALOCEAN_API_TOKEN "your-api-token-here"
```

**Note:** After using `setx`, you need to open a new Command Prompt window for the variable to be available.

**Verify it's set:**
```cmd
echo %DIGITALOCEAN_API_TOKEN%
```

### Using .env File (Docker Compose)

For Docker Compose, you can also use a `.env` file:

1. Create a `.env` file in the project directory:
```bash
echo "DIGITALOCEAN_API_TOKEN=your-api-token-here" > .env
```

2. Docker Compose will automatically load variables from `.env`

**Important:** Add `.env` to your `.gitignore` to avoid committing your token:
```bash
echo ".env" >> .gitignore
```

### Security Best Practices

- ✅ **Do:** Store tokens in environment variables
- ✅ **Do:** Use `.env` files for Docker Compose (and add to `.gitignore`)
- ✅ **Do:** Use read-only tokens when possible
- ✅ **Do:** Rotate tokens regularly
- ❌ **Don't:** Hardcode tokens in scripts or configuration files
- ❌ **Don't:** Commit tokens to version control
- ❌ **Don't:** Share tokens in chat or email

## Quick Start (Docker)

### Using the Wrapper Scripts (Recommended)

**Linux/macOS (Bash):**
```bash
# Build and run in one command
./docker-run.sh build-run --token "your-token"

# Or separately
./docker-run.sh build
./docker-run.sh run --token "your-token"

# View help
./docker-run.sh --help
```

**Windows (PowerShell):**
```powershell
# Build and run in one command
.\docker-run.ps1 build-run -Token "your-token"

# Or separately
.\docker-run.ps1 build
.\docker-run.ps1 run -Token "your-token"

# View help
.\docker-run.ps1 help
```

### Manual Docker Commands

```bash
# 1. Build the image
docker build -t digitalocean-mcp-server .

# 2. Run with your API token
docker run -it --rm -e DIGITALOCEAN_API_TOKEN="your-token" digitalocean-mcp-server
```

## Installation

### Option 1: Docker Installation (Recommended)

#### Using Wrapper Scripts

**Linux/macOS:**
```bash
# Make script executable (first time only)
chmod +x docker-run.sh

# Build and run
./docker-run.sh build-run --token "your-api-token-here"

# See all options
./docker-run.sh --help
```

**Windows PowerShell:**
```powershell
# Build and run
.\docker-run.ps1 build-run -Token "your-api-token-here"

# See all options
.\docker-run.ps1 help
```

#### Manual Docker Commands

1. **Build the Docker image:**
```bash
docker build -t digitalocean-mcp-server .
```

2. **Run the container:**
```bash
docker run -it --rm \
  -e DIGITALOCEAN_API_TOKEN="your-api-token-here" \
  digitalocean-mcp-server
```

Or use Docker Compose:
```bash
# Option 1: Set your API token as environment variable
export DIGITALOCEAN_API_TOKEN="your-api-token-here"
docker-compose up

# Option 2: Create a .env file (recommended)
# Create .env file with: DIGITALOCEAN_API_TOKEN=your-api-token-here
docker-compose up

# Build and run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f
```

**For MCP Client Configuration with Docker:**

Update your MCP client configuration to use Docker:

```json
{
  "mcpServers": {
    "digitalocean": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "DIGITALOCEAN_API_TOKEN=$DIGITALOCEAN_API_TOKEN",
        "digitalocean-mcp-server"
      ]
    }
  }
}
```

**Note**: Replace `your-api-token-here` with your actual DigitalOcean API token. For security, consider using environment variables or a secrets management system instead of hardcoding the token.

### Option 2: Local Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

**Note**: If you encounter import errors with the `mcp` package, you may need to install it from the official source:
```bash
pip install git+https://github.com/modelcontextprotocol/python-sdk.git
```

Alternatively, check the [MCP Python SDK documentation](https://github.com/modelcontextprotocol/python-sdk) for the latest installation instructions.

2. **Set up your DigitalOcean API token:**
   - See the [Setting Up Your DigitalOcean API Token](#setting-up-your-digitalocean-api-token) section above for detailed instructions
   - Set the `DIGITALOCEAN_API_TOKEN` environment variable using the methods described above

## MCP Catalog Configuration

A catalog YAML file (`digitalocean-mcp-catalog.yaml`) is provided for easy integration with MCP clients that support catalog-based server registration.

### Using the Catalog File

The catalog file contains all the necessary configuration for the DigitalOcean MCP server, including:
- Server metadata and description
- All available tools and their parameters
- Environment variable configuration
- Installation instructions
- Usage examples
- Client-specific configurations (Cursor, Claude Desktop, Docker)

**To use with MCP clients that support catalogs:**
1. Reference the catalog file in your MCP client configuration
2. Ensure the `DIGITALOCEAN_API_TOKEN` environment variable is set
3. The client will automatically configure the server based on the catalog

**Note:** Update the `homepage`, `repository`, and `documentation` URLs in the catalog file to match your actual repository location.

### Docker Desktop MCP Gateway

Docker Desktop (v4.32 or later) includes an MCP Gateway that can consume custom catalogs. The steps below assume the Docker MCP Toolkit feature is enabled in Docker Desktop (Settings → Beta features → **Enable Docker MCP Toolkit**).

1. **Build the Docker image (optional but recommended):**
   ```bash
   docker build -t digitalocean-mcp-server .
   ```

2. **Add the catalog to Docker's MCP gateway:**
   ```bash
   docker mcp catalog add my-catalog digitalocean-mcp ./digitalocean-mcp-catalog.yaml
   ```
   - `my-catalog` is an arbitrary catalog name you choose
   - `digitalocean-mcp` is the server identifier used inside the gateway

3. **Verify the catalog entry (optional):**
   ```bash
   docker mcp catalog list
   ```

4. **Set your API token in the current shell (examples):**
   ```bash
   # macOS / Linux
   export DIGITALOCEAN_API_TOKEN="your-api-token-here"

   # Windows PowerShell
   $env:DIGITALOCEAN_API_TOKEN = "your-api-token-here"
   ```

5. **Launch the MCP gateway using the catalog:**
   ```bash
   docker mcp gateway run --catalog my-catalog
   ```
   Keep this process running while you use your MCP client. Use `Ctrl+C` to stop the gateway.

6. **Connect your MCP client via Docker Desktop:**
   - Open Docker Desktop → **MCP Toolkit** → **Clients**
   - Click **Connect** for your client (e.g., Cursor, Claude Desktop)
   - Follow any prompts from the client to authorize the gateway

**Tip:** If you prefer running the server via Docker inside the gateway, ensure the `digitalocean-mcp` image is available locally (step 1). The catalog already contains both stdio and Docker runtime definitions.

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

### Docker Issues

**Container won't start:**
- Verify Docker is running: `docker --version`
- Check the image was built: `docker images | grep digitalocean-mcp-server`
- View container logs: `docker logs digitalocean-mcp-server`
- Ensure the API token environment variable is set correctly

**MCP client can't connect to Docker container:**
- Verify the Docker command in your MCP configuration is correct
- Ensure `-i` flag is included for interactive mode (stdio)
- Check that the container name matches: `digitalocean-mcp-server`
- Test the container manually: `docker run -it --rm -e DIGITALOCEAN_API_TOKEN="test" digitalocean-mcp-server`

**Permission errors:**
- On Linux, you may need to add your user to the docker group: `sudo usermod -aG docker $USER`
- Restart your session after adding to docker group

### Server not starting (Local Installation)
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

## Wrapper Scripts

Convenience scripts are provided to simplify Docker operations:

### Bash Script (`docker-run.sh`)

Available commands:
- `build` - Build the Docker image
- `run` - Run the Docker container
- `build-run` - Build and run in one command
- `stop` - Stop the running container
- `logs` - View container logs
- `clean` - Remove image and container

**Options:**
- `-t, --token TOKEN` - Set DigitalOcean API token
- `-i, --image NAME` - Custom image name
- `-c, --container NAME` - Custom container name
- `-h, --help` - Show help message

**Examples:**
```bash
# Build and run
./docker-run.sh build-run --token "your-token"

# Run with environment variable
export DIGITALOCEAN_API_TOKEN="your-token"
./docker-run.sh run

# View logs
./docker-run.sh logs

# Clean up
./docker-run.sh clean
```

### PowerShell Script (`docker-run.ps1`)

Same functionality as the bash script, optimized for Windows PowerShell.

**Examples:**
```powershell
# Build and run
.\docker-run.ps1 build-run -Token "your-token"

# Run with environment variable
$env:DIGITALOCEAN_API_TOKEN = "your-token"
.\docker-run.ps1 run

# View logs
.\docker-run.ps1 logs

# Clean up
.\docker-run.ps1 clean
```

## Development

To test the server directly:

```bash
export DIGITALOCEAN_API_TOKEN="your-token"
python mcp_server.py
```

The server communicates via stdio using the MCP protocol, so it's designed to be run by an MCP client, not directly.

## License

This MCP server is provided as-is for use with the DigitalOcean API.

