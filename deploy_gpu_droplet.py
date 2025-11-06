#!/usr/bin/env python3
"""
DigitalOcean GPU Droplet Deployment Script

This script deploys a GPU-enabled droplet from a snapshot using the DigitalOcean API v2.
"""

import os
import sys
import json
import time
import requests
from typing import Optional, Dict, Any


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
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make an API request to DigitalOcean.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            data: Optional JSON data for POST/PUT requests
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.headers)
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
    
    def get_gpu_sizes(self) -> list:
        """Get list of available GPU droplet sizes."""
        response = self._make_request("GET", "/sizes")
        sizes = response.get("sizes", [])
        # Filter for GPU-enabled sizes
        gpu_sizes = [size for size in sizes if size.get("description", "").lower().find("gpu") != -1]
        return gpu_sizes
    
    def get_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """
        Get snapshot information.
        
        Args:
            snapshot_id: Snapshot ID or slug
            
        Returns:
            Snapshot information dictionary
        """
        response = self._make_request("GET", f"/snapshots/{snapshot_id}")
        return response.get("snapshot", {})
    
    def create_droplet(
        self,
        name: str,
        region: str,
        size: str,
        snapshot_id: str,
        ssh_keys: Optional[list] = None,
        tags: Optional[list] = None,
        user_data: Optional[str] = None,
        monitoring: bool = False,
        ipv6: bool = False,
        private_networking: bool = True
    ) -> Dict[str, Any]:
        """
        Create a droplet from a snapshot.
        
        Args:
            name: Droplet name
            region: Region slug (e.g., 'nyc1', 'sfo3')
            size: Droplet size slug (e.g., 'g-2vcpu-16gb' for GPU)
            snapshot_id: Snapshot ID or slug
            ssh_keys: Optional list of SSH key IDs or fingerprints
            tags: Optional list of tags
            user_data: Optional cloud-init user data
            monitoring: Enable monitoring
            ipv6: Enable IPv6
            private_networking: Enable private networking
            
        Returns:
            Created droplet information dictionary
        """
        droplet_data = {
            "name": name,
            "region": region,
            "size": size,
            "image": snapshot_id,
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
    
    def get_droplet(self, droplet_id: int) -> Dict[str, Any]:
        """
        Get droplet information.
        
        Args:
            droplet_id: Droplet ID
            
        Returns:
            Droplet information dictionary
        """
        response = self._make_request("GET", f"/droplets/{droplet_id}")
        return response.get("droplet", {})
    
    def wait_for_droplet(self, droplet_id: int, timeout: int = 300) -> Dict[str, Any]:
        """
        Wait for droplet to become active.
        
        Args:
            droplet_id: Droplet ID
            timeout: Maximum wait time in seconds
            
        Returns:
            Active droplet information dictionary
            
        Raises:
            TimeoutError: If droplet doesn't become active within timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            droplet = self.get_droplet(droplet_id)
            status = droplet.get("status", "")
            
            if status == "active":
                return droplet
            elif status == "error":
                raise Exception(f"Droplet {droplet_id} entered error state")
            
            time.sleep(5)
        
        raise TimeoutError(f"Droplet {droplet_id} did not become active within {timeout} seconds")


def main():
    """Main function to deploy GPU droplet from snapshot."""
    
    # Get API token from environment variable
    api_token = os.getenv("DIGITALOCEAN_API_TOKEN")
    if not api_token:
        print("Error: DIGITALOCEAN_API_TOKEN environment variable not set")
        print("Please set it using: export DIGITALOCEAN_API_TOKEN='your-token'")
        sys.exit(1)
    
    # Configuration - modify these values as needed
    config = {
        "droplet_name": os.getenv("DROPLET_NAME", "gpu-droplet"),
        "region": os.getenv("DROPLET_REGION", "nyc1"),  # Change to your preferred region
        "size": os.getenv("DROPLET_SIZE", "g-2vcpu-16gb"),  # GPU size slug
        "snapshot_id": os.getenv("SNAPSHOT_ID"),  # Required: Your snapshot ID
        "ssh_keys": os.getenv("SSH_KEYS", "").split(",") if os.getenv("SSH_KEYS") else None,
        "tags": os.getenv("DROPLET_TAGS", "").split(",") if os.getenv("DROPLET_TAGS") else None,
        "monitoring": os.getenv("MONITORING", "false").lower() == "true",
        "ipv6": os.getenv("IPV6", "false").lower() == "true",
        "private_networking": os.getenv("PRIVATE_NETWORKING", "true").lower() == "true",
        "wait_for_active": os.getenv("WAIT_FOR_ACTIVE", "true").lower() == "true"
    }
    
    # Validate required configuration
    if not config["snapshot_id"]:
        print("Error: SNAPSHOT_ID environment variable is required")
        print("Please set it using: export SNAPSHOT_ID='snapshot-id-or-slug'")
        sys.exit(1)
    
    # Initialize API client
    print("Initializing DigitalOcean API client...")
    api = DigitalOceanAPI(api_token)
    
    try:
        # Verify snapshot exists
        print(f"Verifying snapshot: {config['snapshot_id']}")
        snapshot = api.get_snapshot(config["snapshot_id"])
        print(f"Snapshot found: {snapshot.get('name', 'N/A')} ({snapshot.get('id', 'N/A')})")
        
        # List available GPU sizes (optional, for reference)
        print("\nFetching available GPU sizes...")
        gpu_sizes = api.get_gpu_sizes()
        if gpu_sizes:
            print("Available GPU sizes:")
            for size in gpu_sizes[:5]:  # Show first 5
                print(f"  - {size.get('slug')}: {size.get('description')}")
        else:
            print("Warning: No GPU sizes found. Make sure you're using a GPU-enabled size slug.")
        
        # Create droplet
        print(f"\nCreating droplet '{config['droplet_name']}'...")
        print(f"  Region: {config['region']}")
        print(f"  Size: {config['size']}")
        print(f"  Snapshot: {config['snapshot_id']}")
        
        droplet = api.create_droplet(
            name=config["droplet_name"],
            region=config["region"],
            size=config["size"],
            snapshot_id=config["snapshot_id"],
            ssh_keys=config["ssh_keys"],
            tags=config["tags"],
            monitoring=config["monitoring"],
            ipv6=config["ipv6"],
            private_networking=config["private_networking"]
        )
        
        droplet_id = droplet.get("id")
        print(f"\n✓ Droplet created successfully!")
        print(f"  Droplet ID: {droplet_id}")
        print(f"  Name: {droplet.get('name')}")
        print(f"  Status: {droplet.get('status')}")
        
        # Wait for droplet to become active
        if config["wait_for_active"]:
            print("\nWaiting for droplet to become active...")
            droplet = api.wait_for_droplet(droplet_id)
            print(f"✓ Droplet is now active!")
            
            # Display network information
            networks = droplet.get("networks", {})
            v4_addresses = networks.get("v4", [])
            
            if v4_addresses:
                print("\nNetwork Information:")
                for addr in v4_addresses:
                    addr_type = addr.get("type", "unknown")
                    ip = addr.get("ip_address", "N/A")
                    print(f"  {addr_type.upper()}: {ip}")
        
        # Output JSON for programmatic use
        print("\n" + "="*50)
        print("Droplet Information (JSON):")
        print(json.dumps(droplet, indent=2))
        
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

