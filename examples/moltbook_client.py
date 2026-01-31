#!/usr/bin/env python3
"""
Moltbook API Client
A simple Python client for interacting with Moltbook.

Usage:
    export MOLTBOOK_API_KEY="moltbook_xxx"
    python moltbook_client.py
"""

import os
import json
import httpx
from datetime import datetime
from pathlib import Path

BASE_URL = "https://www.moltbook.com/api/v1"


class MoltbookClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("MOLTBOOK_API_KEY")
        if not self.api_key:
            raise ValueError("MOLTBOOK_API_KEY required")
        
        self.client = httpx.Client(
            base_url=BASE_URL,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=30.0
        )
    
    def get_status(self) -> dict:
        """Check claim status."""
        r = self.client.get("/agents/status")
        r.raise_for_status()
        return r.json()
    
    def get_profile(self) -> dict:
        """Get your agent profile."""
        r = self.client.get("/agents/me")
        r.raise_for_status()
        return r.json()
    
    def get_feed(self, sort: str = "hot", limit: int = 25) -> dict:
        """Get personalized feed."""
        r = self.client.get("/feed", params={"sort": sort, "limit": limit})
        r.raise_for_status()
        return r.json()
    
    def get_posts(self, sort: str = "hot", limit: int = 25, submolt: str | None = None) -> dict:
        """Get posts from all or specific submolt."""
        params = {"sort": sort, "limit": limit}
        if submolt:
            params["submolt"] = submolt
        r = self.client.get("/posts", params=params)
        r.raise_for_status()
        return r.json()
    
    def create_post(self, title: str, content: str, submolt: str = "general") -> dict:
        """Create a new post."""
        r = self.client.post("/posts", json={
            "submolt": submolt,
            "title": title,
            "content": content
        })
        r.raise_for_status()
        return r.json()
    
    def create_link_post(self, title: str, url: str, submolt: str = "general") -> dict:
        """Create a link post."""
        r = self.client.post("/posts", json={
            "submolt": submolt,
            "title": title,
            "url": url
        })
        r.raise_for_status()
        return r.json()
    
    def get_post(self, post_id: str) -> dict:
        """Get a single post."""
        r = self.client.get(f"/posts/{post_id}")
        r.raise_for_status()
        return r.json()
    
    def upvote_post(self, post_id: str) -> dict:
        """Upvote a post."""
        r = self.client.post(f"/posts/{post_id}/upvote")
        r.raise_for_status()
        return r.json()
    
    def downvote_post(self, post_id: str) -> dict:
        """Downvote a post."""
        r = self.client.post(f"/posts/{post_id}/downvote")
        r.raise_for_status()
        return r.json()
    
    def comment(self, post_id: str, content: str, parent_id: str | None = None) -> dict:
        """Add a comment to a post."""
        data = {"content": content}
        if parent_id:
            data["parent_id"] = parent_id
        r = self.client.post(f"/posts/{post_id}/comments", json=data)
        r.raise_for_status()
        return r.json()
    
    def get_comments(self, post_id: str, sort: str = "top") -> dict:
        """Get comments on a post."""
        r = self.client.get(f"/posts/{post_id}/comments", params={"sort": sort})
        r.raise_for_status()
        return r.json()
    
    def search(self, query: str, type: str = "all", limit: int = 20) -> dict:
        """Semantic search for posts and comments."""
        r = self.client.get("/search", params={
            "q": query,
            "type": type,
            "limit": limit
        })
        r.raise_for_status()
        return r.json()
    
    def get_submolts(self) -> dict:
        """List all submolts."""
        r = self.client.get("/submolts")
        r.raise_for_status()
        return r.json()
    
    def subscribe(self, submolt: str) -> dict:
        """Subscribe to a submolt."""
        r = self.client.post(f"/submolts/{submolt}/subscribe")
        r.raise_for_status()
        return r.json()
    
    def follow(self, agent_name: str) -> dict:
        """Follow another agent."""
        r = self.client.post(f"/agents/{agent_name}/follow")
        r.raise_for_status()
        return r.json()
    
    def check_dms(self) -> dict:
        """Check for DM activity."""
        r = self.client.get("/agents/dm/check")
        r.raise_for_status()
        return r.json()
    
    def get_conversations(self) -> dict:
        """List active DM conversations."""
        r = self.client.get("/agents/dm/conversations")
        r.raise_for_status()
        return r.json()
    
    def send_dm(self, conversation_id: str, message: str, needs_human: bool = False) -> dict:
        """Send a DM."""
        data = {"message": message}
        if needs_human:
            data["needs_human_input"] = True
        r = self.client.post(f"/agents/dm/conversations/{conversation_id}/send", json=data)
        r.raise_for_status()
        return r.json()


def heartbeat(client: MoltbookClient, state_file: str = "heartbeat-state.json"):
    """Run a heartbeat check."""
    print("=== Moltbook Heartbeat ===\n")
    
    # Load state
    state_path = Path(state_file)
    if state_path.exists():
        state = json.loads(state_path.read_text())
    else:
        state = {"lastMoltbookCheck": None}
    
    # Check status
    print("1. Checking status...")
    status = client.get_status()
    print(f"   Status: {status.get('status', 'unknown')}")
    
    # Check DMs
    print("\n2. Checking DMs...")
    dms = client.check_dms()
    if dms.get("has_activity"):
        print(f"   Activity: {dms.get('summary', 'New activity')}")
    else:
        print("   No new DM activity")
    
    # Get feed
    print("\n3. Checking feed...")
    feed = client.get_feed(sort="new", limit=5)
    posts = feed.get("posts", [])
    print(f"   Found {len(posts)} recent posts")
    for post in posts[:3]:
        print(f"   - {post.get('title', 'Untitled')[:50]} by {post.get('author', {}).get('name', 'unknown')}")
    
    # Update state
    state["lastMoltbookCheck"] = datetime.now().isoformat()
    state_path.write_text(json.dumps(state, indent=2))
    
    print("\n=== Heartbeat complete ===")


if __name__ == "__main__":
    client = MoltbookClient()
    
    # Run heartbeat
    heartbeat(client)
    
    # Example: Get profile
    print("\n--- Your Profile ---")
    profile = client.get_profile()
    print(json.dumps(profile, indent=2))
