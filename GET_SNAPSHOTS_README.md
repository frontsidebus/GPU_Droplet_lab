# DigitalOcean - Get Snapshot IDs from Projects

## Overview
How to retrieve snapshot IDs from DigitalOcean projects using the API and web interface.

## Method 1: Using the Web Interface

### Steps:
1. Log in to [DigitalOcean Control Panel](https://cloud.digitalocean.com)
2. Navigate to **Images** → **Snapshots**
3. Find your snapshot in the list
4. The snapshot ID is displayed in the format:
   - Numeric ID (e.g., `12345678`)
   - Or a slug format (e.g., `my-snapshot-name`)

### Filtering by Project:
- Use the filter dropdown to filter snapshots by project
- Select your project from the filter list
- All snapshots associated with that project will be displayed

---

## Method 2: Using the DigitalOcean API

### Get All Snapshots (Including Project Association)

```bash
curl -X GET \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  "https://api.digitalocean.com/v2/snapshots"
```

### Get Snapshots for a Specific Project

First, get your project ID:
```bash
curl -X GET \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  "https://api.digitalocean.com/v2/projects"
```

Then filter snapshots by project (note: API doesn't directly filter by project, but you can use the response):

```bash
# Get all snapshots
curl -X GET \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  "https://api.digitalocean.com/v2/snapshots?resource_type=droplet" | jq
```

### Using Python Script

Create a helper script to list snapshots:

```python
import requests
import os

API_TOKEN = os.getenv("DIGITALOCEAN_API_TOKEN")
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# Get all snapshots
response = requests.get(
    "https://api.digitalocean.com/v2/snapshots?resource_type=droplet",
    headers=headers
)

snapshots = response.json().get("snapshots", [])

print("Snapshots:")
for snapshot in snapshots:
    print(f"  ID: {snapshot['id']}")
    print(f"  Name: {snapshot['name']}")
    print(f"  Created: {snapshot['created_at']}")
    print(f"  Regions: {', '.join(snapshot['regions'])}")
    print(f"  Min Disk Size: {snapshot['min_disk_size']} GB")
    print("---")
```

---

## Method 3: Using doctl CLI

### Install doctl
```bash
# Windows (using scoop)
scoop install doctl

# Or download from: https://github.com/digitalocean/doctl/releases
```

### Authenticate
```bash
doctl auth init
```

### List Snapshots
```bash
# List all snapshots
doctl compute snapshot list

# List snapshots with more details
doctl compute snapshot list --format ID,Name,ResourceType,Regions,MinDiskSize,CreatedAt

# List only droplet snapshots
doctl compute snapshot list --resource droplet
```

### Filter by Project (via doctl)
```bash
# Get project ID first
doctl projects list

# Get resources in project (includes snapshots)
doctl projects resources list PROJECT_ID
```

---

## Method 4: Using the Deployment Script Helper

You can modify the `deploy_gpu_droplet.py` script to list snapshots:

```python
# Add this method to the DigitalOceanAPI class:

def list_snapshots(self, resource_type: str = "droplet") -> list:
    """
    List all snapshots.
    
    Args:
        resource_type: Type of resource ('droplet' or 'volume')
        
    Returns:
        List of snapshot dictionaries
    """
    response = self._make_request("GET", f"/snapshots?resource_type={resource_type}")
    return response.get("snapshots", [])
```

Then use it:
```python
api = DigitalOceanAPI(api_token)
snapshots = api.list_snapshots()

for snapshot in snapshots:
    print(f"{snapshot['id']}: {snapshot['name']}")
```

---

## Understanding Snapshot IDs

### Types of Identifiers:
1. **Numeric ID**: Unique numeric identifier (e.g., `12345678`)
2. **Slug/Name**: Human-readable name (e.g., `my-gpu-snapshot-2024`)

Both can be used in API calls and the deployment script.

### Important Notes:
- Snapshot IDs are unique across your account
- Snapshots can be associated with multiple projects
- You can filter by project in the web UI but the API requires manual filtering
- Snapshot names can have duplicates, but IDs are always unique

---

## Quick Reference

### API Endpoints:
- List all snapshots: `GET /v2/snapshots`
- Get specific snapshot: `GET /v2/snapshots/{snapshot_id}`
- List projects: `GET /v2/projects`
- List project resources: `GET /v2/projects/{project_id}/resources`

### Environment Variables:
```bash
export DIGITALOCEAN_API_TOKEN="your-token"
export SNAPSHOT_ID="snapshot-id-or-slug"
```

### Useful Filters:
- `?resource_type=droplet` - Only droplet snapshots
- `?resource_type=volume` - Only volume snapshots

---

## Troubleshooting

### Snapshot Not Found:
- Verify the snapshot ID is correct
- Check that the snapshot hasn't been deleted
- Ensure you're using the correct API token

### Project Association:
- The API doesn't directly filter snapshots by project
- Use the web interface or filter results programmatically
- Project resources endpoint shows all resources including snapshots

---

## Related Notes
- [[DigitalOcean API Reference]]
- [[GPU Droplet Deployment]]
- [[doctl CLI Commands]]

