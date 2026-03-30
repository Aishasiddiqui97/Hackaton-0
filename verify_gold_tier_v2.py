import os
import json
import json
import sys
import subprocess
from dotenv import load_dotenv

load_dotenv()

VAULT_PATH = os.path.join(os.environ.get("USERPROFILE"), "AI_Employee_Vault")

def call_mcp(script_name, tool, params=None):
    params = params or {}
    script_path = os.path.join(os.getcwd(), script_name)
    if not os.path.exists(script_path):
        return {"error": f"File {script_name} not found"}
    
    input_data = json.dumps({"tool": tool, "params": params})
    try:
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=input_data)
        if process.returncode != 0:
            return {"error": stderr or "Unknown error"}
        if not stdout.strip():
            return {"error": "No output from MCP server"}
        return json.loads(stdout.strip())
    except Exception as e:
        return {"error": str(e)}

def verify():
    print("="*60)
    print("GOLD TIER INTEGRATION VERIFICATION")
    print("="*60)
    
    platforms = {
        "Facebook": "facebook_mcp_server.py",
        "Instagram": "instagram_mcp_server.py",
        "Twitter": "twitter_mcp_server.py"
    }
    
    for name, script in platforms.items():
        print(f"\n--- Checking {name} ---")
        res = call_mcp(script, "get_account_summary" if name != "Facebook" else "get_page_summary")
        if res.get("success"):
            print(f"OK: {name} Connection: SUCCESS")
            print(f"Stats: {json.dumps(res, indent=2)}")
        else:
            print(f"ERROR: {name} Connection: FAILED")
            # print(f"WARNING: Error: {res.get('error')}")
            # Check if .env has the keys
            keys = {
                "Facebook": ["FACEBOOK_PAGE_ID", "FACEBOOK_ACCESS_TOKEN"],
                "Instagram": ["INSTAGRAM_ACCOUNT_ID", "INSTAGRAM_ACCESS_TOKEN"],
                "Twitter": ["TWITTER_API_KEY", "TWITTER_BEARER_TOKEN", "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_TOKEN_SECRET"]
            }
            missing = [k for k in keys[name] if not os.getenv(k)]
            if missing:
                print(f"MISSING .env keys: {', '.join(missing)}")
            else:
                print(f"API Error: {res.get('error')}")

    print("\n--- Checking Vault Structure ---")
    folders = ["Needs_Action", "Plans", "Done", "Briefings", "Logs", "Signals"]
    for f in folders:
        path = os.path.join(VAULT_PATH, f)
        if os.path.exists(path):
            print(f"OK: Vault/{f}: OK")
        else:
            print(f"ERROR: Vault/{f}: MISSING")

    print("\n" + "="*60)
    print("Verification Complete.")

if __name__ == "__main__":
    verify()
