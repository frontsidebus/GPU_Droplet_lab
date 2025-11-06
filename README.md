# DigitalOcean GPU Droplet Deployment Script

A Python 3.11 script to deploy GPU-enabled droplets from snapshots using the DigitalOcean API v2.

## Prerequisites

- Python 3.11 or higher
- DigitalOcean API token with write permissions
- A snapshot ID of the image you want to deploy

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The script uses environment variables for configuration. Set the following:

### Required Variables

- `DIGITALOCEAN_API_TOKEN`: Your DigitalOcean API token
- `SNAPSHOT_ID`: The ID or slug of the snapshot to deploy from

### Optional Variables

- `DROPLET_NAME`: Name for the droplet (default: `gpu-droplet`)
- `DROPLET_REGION`: Region slug (default: `nyc1`)
  - Common regions: `nyc1`, `nyc3`, `sfo3`, `sgp1`, `lon1`, `fra1`, `tor1`, `blr1`, `ams3`
- `DROPLET_SIZE`: GPU droplet size slug (default: `g-2vcpu-16gb`)
  - Common GPU sizes: `g-2vcpu-16gb`, `g-4vcpu-32gb`, `g-8vcpu-64gb`, `g-16vcpu-128gb`
- `SSH_KEYS`: Comma-separated list of SSH key IDs or fingerprints
- `DROPLET_TAGS`: Comma-separated list of tags
- `MONITORING`: Enable monitoring (default: `false`)
- `IPV6`: Enable IPv6 (default: `false`)
- `PRIVATE_NETWORKING`: Enable private networking (default: `true`)
- `WAIT_FOR_ACTIVE`: Wait for droplet to become active (default: `true`)

## Usage

### Basic Usage

```bash
export DIGITALOCEAN_API_TOKEN="your-api-token"
export SNAPSHOT_ID="snapshot-id-or-slug"
python deploy_gpu_droplet.py
```

### Advanced Usage

```bash
export DIGITALOCEAN_API_TOKEN="your-api-token"
export SNAPSHOT_ID="snapshot-id-or-slug"
export DROPLET_NAME="my-gpu-server"
export DROPLET_REGION="sfo3"
export DROPLET_SIZE="g-4vcpu-32gb"
export SSH_KEYS="key-id-1,key-id-2"
export DROPLET_TAGS="production,gpu"
export MONITORING="true"
python deploy_gpu_droplet.py
```

### Windows PowerShell

```powershell
$env:DIGITALOCEAN_API_TOKEN="your-api-token"
$env:SNAPSHOT_ID="snapshot-id-or-slug"
$env:DROPLET_NAME="my-gpu-server"
python deploy_gpu_droplet.py
```

## Getting Your API Token

1. Log in to your DigitalOcean account
2. Go to API → Tokens/Keys
3. Generate a new token with write permissions
4. Copy the token and set it as `DIGITALOCEAN_API_TOKEN`

## Finding Your Snapshot ID

1. Log in to your DigitalOcean account
2. Go to Images → Snapshots
3. Find your snapshot and copy its ID or slug

## Finding Available GPU Sizes

The script will display available GPU sizes when run. You can also check the DigitalOcean documentation or use the API directly:

```bash
curl -X GET \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  "https://api.digitalocean.com/v2/sizes" | grep -i gpu
```

## Error Handling

The script includes comprehensive error handling:
- Validates API token presence
- Verifies snapshot exists before deployment
- Checks droplet status and waits for activation
- Provides clear error messages for common issues

## Output

The script outputs:
- Droplet creation confirmation
- Droplet ID and status
- Network information (IP addresses)
- Full droplet information in JSON format

## Example Output

```
Initializing DigitalOcean API client...
Verifying snapshot: snapshot-id-12345
Snapshot found: My GPU Snapshot (snapshot-id-12345)

Fetching available GPU sizes...
Available GPU sizes:
  - g-2vcpu-16gb: GPU-Optimized 2 vCPU, 16 GB RAM
  - g-4vcpu-32gb: GPU-Optimized 4 vCPU, 32 GB RAM

Creating droplet 'gpu-droplet'...
  Region: nyc1
  Size: g-2vcpu-16gb
  Snapshot: snapshot-id-12345

✓ Droplet created successfully!
  Droplet ID: 123456789
  Name: gpu-droplet
  Status: new

Waiting for droplet to become active...
✓ Droplet is now active!

Network Information:
  PUBLIC: 123.45.67.89
  PRIVATE: 10.0.0.5
```

## Notes

- GPU droplets are only available in certain regions. Check DigitalOcean's documentation for current availability.
- Snapshot must be compatible with GPU droplet sizes.
- The script waits up to 5 minutes for the droplet to become active by default.

