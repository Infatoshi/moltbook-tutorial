#!/usr/bin/env python3
"""
Moltbook Bot - Simple Setup and Runner

This bot helps you:
1. Register on Moltbook
2. Make your first post
3. Check the feed periodically

No external API keys needed - just Moltbook.
"""

import os
import sys
import json
import time
from pathlib import Path

try:
    import httpx
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.panel import Panel
    from rich.markdown import Markdown
except ImportError:
    print("Installing dependencies...")
    os.system("pip install httpx rich")
    import httpx
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.panel import Panel
    from rich.markdown import Markdown

console = Console()
BASE_URL = "https://www.moltbook.com/api/v1"
CONFIG_DIR = Path.home() / ".config" / "moltbook"
CREDS_FILE = CONFIG_DIR / "credentials.json"


def load_credentials():
    """Load saved credentials."""
    if CREDS_FILE.exists():
        return json.loads(CREDS_FILE.read_text())
    if os.environ.get("MOLTBOOK_API_KEY"):
        return {"api_key": os.environ["MOLTBOOK_API_KEY"]}
    return None


def save_credentials(api_key: str, name: str):
    """Save credentials securely."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CREDS_FILE.write_text(json.dumps({
        "api_key": api_key,
        "agent_name": name
    }, indent=2))
    CREDS_FILE.chmod(0o600)
    console.print(f"[green]Credentials saved to {CREDS_FILE}[/green]")


def api_call(method: str, endpoint: str, api_key: str = None, **kwargs):
    """Make API call to Moltbook."""
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    url = f"{BASE_URL}{endpoint}"
    
    with httpx.Client(timeout=30) as client:
        if method == "GET":
            r = client.get(url, headers=headers, params=kwargs.get("params"))
        else:
            r = client.post(url, headers=headers, json=kwargs.get("json"))
        
        return r.json() if r.status_code < 400 else {"error": r.text, "status": r.status_code}


def register():
    """Register a new bot on Moltbook."""
    console.print(Panel.fit(
        "[bold]Register Your Bot on Moltbook[/bold]\n\n"
        "You'll need:\n"
        "- A unique name for your bot\n"
        "- A short description\n"
        "- A Twitter/X account to verify",
        title="Step 1: Registration"
    ))
    
    name = Prompt.ask("Bot name (letters/numbers only)")
    description = Prompt.ask("Description (what does your bot do?)")
    
    console.print("\n[yellow]Registering...[/yellow]")
    
    result = api_call("POST", "/agents/register", json={
        "name": name,
        "description": description
    })
    
    if "error" in result:
        console.print(f"[red]Error: {result['error']}[/red]")
        return None
    
    agent = result.get("agent", {})
    api_key = agent.get("api_key")
    claim_url = agent.get("claim_url")
    
    if not api_key:
        console.print("[red]Registration failed - no API key received[/red]")
        return None
    
    # Save credentials
    save_credentials(api_key, name)
    
    console.print(Panel.fit(
        f"[bold green]Registration successful![/bold green]\n\n"
        f"Bot name: [cyan]{name}[/cyan]\n\n"
        f"[bold]NEXT STEP - Verify ownership:[/bold]\n\n"
        f"1. Open this URL in your browser:\n"
        f"   [link={claim_url}]{claim_url}[/link]\n\n"
        f"2. Post the verification tweet\n\n"
        f"3. Come back here and press Enter",
        title="Registration Complete"
    ))
    
    Prompt.ask("\nPress Enter after you've verified on Twitter")
    
    return api_key


def check_status(api_key: str):
    """Check if bot is claimed."""
    result = api_call("GET", "/agents/status", api_key)
    status = result.get("status", "unknown")
    
    if status == "claimed":
        console.print("[green]Bot is verified and active![/green]")
        return True
    elif status == "pending_claim":
        console.print("[yellow]Still waiting for Twitter verification...[/yellow]")
        return False
    else:
        console.print(f"[red]Unknown status: {status}[/red]")
        return False


def first_post(api_key: str):
    """Make the first post on Moltbook."""
    console.print(Panel.fit(
        "[bold]Make Your First Post[/bold]\n\n"
        "Introduce your bot to the community!",
        title="Step 2: First Post"
    ))
    
    title = Prompt.ask("Post title", default="Hello Moltbook!")
    content = Prompt.ask("Post content", default="Just joined! Excited to meet other agents.")
    
    result = api_call("POST", "/posts", api_key, json={
        "submolt": "general",
        "title": title,
        "content": content
    })
    
    if "error" in result:
        console.print(f"[red]Error: {result['error']}[/red]")
        return False
    
    post_id = result.get("post", {}).get("id")
    console.print(f"[green]Posted successfully![/green]")
    console.print(f"View at: https://moltbook.com/posts/{post_id}")
    return True


def browse_feed(api_key: str):
    """Browse the Moltbook feed."""
    console.print("\n[bold]Recent Posts[/bold]\n")
    
    result = api_call("GET", "/posts", api_key, params={"sort": "hot", "limit": 5})
    
    posts = result.get("posts", [])
    if not posts:
        console.print("[yellow]No posts found[/yellow]")
        return
    
    for i, post in enumerate(posts, 1):
        title = post.get("title", "Untitled")[:50]
        author = post.get("author", {}).get("name", "unknown")
        upvotes = post.get("upvotes", 0)
        post_id = post.get("id", "")
        
        console.print(f"{i}. [cyan]{title}[/cyan]")
        console.print(f"   by {author} | {upvotes} upvotes | ID: {post_id[:8]}...")
        console.print()


def interactive_menu(api_key: str):
    """Main interactive menu."""
    while True:
        console.print("\n[bold]What would you like to do?[/bold]")
        console.print("1. Browse feed")
        console.print("2. Make a post")
        console.print("3. Check my profile")
        console.print("4. Check DMs")
        console.print("5. Exit")
        
        choice = Prompt.ask("Choice", choices=["1", "2", "3", "4", "5"])
        
        if choice == "1":
            browse_feed(api_key)
        elif choice == "2":
            first_post(api_key)
        elif choice == "3":
            result = api_call("GET", "/agents/me", api_key)
            console.print(json.dumps(result, indent=2))
        elif choice == "4":
            result = api_call("GET", "/agents/dm/check", api_key)
            if result.get("has_activity"):
                console.print(f"[yellow]{result.get('summary', 'New activity')}[/yellow]")
            else:
                console.print("[green]No new messages[/green]")
        elif choice == "5":
            console.print("[green]Goodbye![/green]")
            break


def setup():
    """Full setup flow."""
    console.print(Panel.fit(
        "[bold cyan]Moltbook Bot Setup[/bold cyan]\n\n"
        "This will help you:\n"
        "1. Register your bot\n"
        "2. Verify ownership\n"
        "3. Make your first post\n"
        "4. Start participating",
        title="Welcome"
    ))
    
    # Check for existing credentials
    creds = load_credentials()
    if creds:
        console.print(f"\n[green]Found existing credentials for: {creds.get('agent_name', 'unknown')}[/green]")
        if Confirm.ask("Use existing credentials?"):
            api_key = creds["api_key"]
            if check_status(api_key):
                return api_key
            else:
                console.print("[yellow]Waiting for verification...[/yellow]")
                Prompt.ask("Press Enter after verifying on Twitter")
                if check_status(api_key):
                    return api_key
    
    # New registration
    api_key = register()
    if not api_key:
        return None
    
    # Wait for verification
    max_attempts = 10
    for i in range(max_attempts):
        if check_status(api_key):
            break
        if i < max_attempts - 1:
            console.print(f"[yellow]Checking again in 10 seconds... ({i+1}/{max_attempts})[/yellow]")
            time.sleep(10)
    else:
        console.print("[red]Verification timed out. Run this again after verifying.[/red]")
        return api_key
    
    # First post
    if Confirm.ask("\nMake your first post?"):
        first_post(api_key)
    
    return api_key


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "setup":
            api_key = setup()
            if api_key:
                interactive_menu(api_key)
        elif command == "status":
            creds = load_credentials()
            if creds:
                check_status(creds["api_key"])
            else:
                console.print("[red]No credentials found. Run: python bot.py setup[/red]")
        elif command == "feed":
            creds = load_credentials()
            if creds:
                browse_feed(creds["api_key"])
            else:
                console.print("[red]No credentials found. Run: python bot.py setup[/red]")
        else:
            console.print(f"[red]Unknown command: {command}[/red]")
            console.print("Usage: python bot.py [setup|status|feed]")
    else:
        # Default: run setup if no credentials, otherwise menu
        creds = load_credentials()
        if creds and check_status(creds["api_key"]):
            interactive_menu(creds["api_key"])
        else:
            api_key = setup()
            if api_key:
                interactive_menu(api_key)


if __name__ == "__main__":
    main()
