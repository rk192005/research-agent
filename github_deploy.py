#!/usr/bin/env python3
import os
import sys
import time
import webbrowser
import subprocess

REPO_NAME = "research-agent"
GITHUB_USER = "rk192005"
SSH_URL = f"git@github.com:{GITHUB_USER}/{REPO_NAME}.git"

def create_and_push():
    print(f"🚀 Opening browser to create repository '{REPO_NAME}' on GitHub...")
    # Open the pre-filled GitHub repository creation page
    url = f"https://github.com/new?name={REPO_NAME}&description=Autopilot+Research+Agent+using+Gemini+and+DuckDuckGo&private=true"
    webbrowser.open(url)
    
    print("\n👉 Please click 'Create repository' on the web page that just opened.")
    print("⏳ Waiting for you to create the repository (timeout in 60 seconds)...")
    
    # Poll using git ls-remote to check when the repository becomes available
    start_time = time.time()
    repo_exists = False
    
    while time.time() - start_time < 60:
        # Run git ls-remote to check if we can connect to the remote repository
        # (This will succeed once the repo is created on GitHub)
        result = subprocess.run(
            ["git", "ls-remote", SSH_URL],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if result.returncode == 0:
            repo_exists = True
            break
        time.sleep(3)
        print(".", end="", flush=True)
    
    if not repo_exists:
        print("\n❌ Timeout: Could not detect the repository. Please make sure you created it on github.com.")
        sys.exit(1)
        
    print("\n✅ Repository detected!")
    print("📤 Pushing code to GitHub...")
    
    try:
        # Remove origin if it exists
        subprocess.run(["git", "remote", "remove", "origin"], stderr=subprocess.DEVNULL)
        # Add the SSH remote
        subprocess.run(["git", "remote", "add", "origin", SSH_URL], check=True)
        # Rename branch to main
        subprocess.run(["git", "branch", "-M", "main"], check=True)
        # Push to main
        subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
        print("\n🎉 Deployment complete! Your repository is now live at:")
        print(f"🔗 https://github.com/{GITHUB_USER}/{REPO_NAME}")
    except Exception as e:
        print(f"\n❌ Failed to push code: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_and_push()
