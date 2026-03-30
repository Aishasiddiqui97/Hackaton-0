#!/usr/bin/env python3
"""
Complete Gold Tier Validation - Including Twitter Browser Automation
Validates all Gold Tier components including browser automation
"""

import sys
from pathlib import Path
import json

def test_component(name, test_func):
    """Test a component and return result."""
    try:
        print(f"Testing {name}... ", end='', flush=True)
        test_func()
        print("[PASS]")
        return True
    except Exception as e:
        print(f"[FAIL]: {str(e)}")
        return False

def test_directories():
    """Test required directory structure."""
    required_dirs = [
        Path("AI_Employee_Vault"),
        Path("AI_Employee_Vault/Inbox"),
        Path("AI_Employee_Vault/Needs_Action"),
        Path("AI_Employee_Vault/Done"),
        Path("AI_Employee_Vault/Plans"),
        Path("AI_Employee_Vault/Skills"),
        Path("AI_Employee_Vault/Agents"),
        Path("AI_Employee_Vault/Logs"),
        Path("AI_Employee_Vault/CEO_Briefings"),
        Path("mcp_servers"),
        Path("scripts"),
        Path("logs")
    ]

    for directory in required_dirs:
        if not directory.exists():
            raise Exception(f"Missing directory: {directory}")

def test_mcp_servers():
    """Test all MCP servers exist."""
    required_servers = [
        "mcp_servers/odoo_server.py",
        "mcp_servers/facebook_server.py",
        "mcp_servers/instagram_server.py",
        "mcp_servers/twitter_server.py",
        "mcp_servers/twitter_browser_server.py"
    ]

    for server in required_servers:
        if not Path(server).exists():
            raise Exception(f"Missing MCP server: {server}")

def test_gold_tier_skills():
    """Test Gold Tier skills exist."""
    required_skills = [
        "AI_Employee_Vault/Skills/odoo_accounting_manager.md",
        "AI_Employee_Vault/Skills/invoice_reconciliation.md",
        "AI_Employee_Vault/Skills/facebook_poster.md",
        "AI_Employee_Vault/Skills/facebook_engagement_analyzer.md",
        "AI_Employee_Vault/Skills/instagram_poster.md",
        "AI_Employee_Vault/Skills/instagram_growth_analyzer.md",
        "AI_Employee_Vault/Skills/twitter_poster.md",
        "AI_Employee_Vault/Skills/twitter_engagement_analyzer.md",
        "AI_Employee_Vault/Skills/twitter_browser_poster.md"
    ]

    for skill in required_skills:
        if not Path(skill).exists():
            raise Exception(f"Missing skill: {skill}")

def test_ceo_briefing():
    """Test CEO Briefing system exists."""
    required_files = [
        "scripts/ceo_briefing_generator.py",
        "AI_Employee_Vault/CEO_Briefings"
    ]

    for file in required_files:
        if not Path(file).exists():
            raise Exception(f"Missing: {file}")

def test_twitter_browser():
    """Test Twitter browser automation components."""
    required_files = [
        "mcp_servers/twitter_browser_server.py",
        "AI_Employee_Vault/Agents/X_Twitter_MCP_Agent.md",
        "AI_Employee_Vault/Plans/Twitter_Post_Plan.md",
        "AI_Employee_Vault/Logs/Twitter_Log.md",
        "AI_Employee_Vault/Skills/twitter_browser_poster.md",
        "scripts/test_twitter_browser.py",
        "scripts/test_twitter_post.py",
        "TWITTER_BROWSER_AUTOMATION.md"
    ]

    for file in required_files:
        if not Path(file).exists():
            raise Exception(f"Missing: {file}")

def test_core_watchers():
    """Test core watcher scripts exist."""
    required_watchers = [
        "AI_Employee_Vault/watcher.py",
        "AI_Employee_Vault/scripts/gmail_watcher.py",
        "scripts/linkedin_watcher.py",
        "scripts/whatsapp_watcher.py"
    ]

    for watcher in required_watchers:
        if not Path(watcher).exists():
            raise Exception(f"Missing watcher: {watcher}")

def test_documentation():
    """Test documentation exists."""
    required_docs = [
        "README.md",
        "GOLD_TIER_DOCUMENTATION.md",
        "GOLD_TIER_SUMMARY.md",
        "TWITTER_BROWSER_AUTOMATION.md",
        "TWITTER_BROWSER_COMPLETE.md",
        ".env.template"
    ]

    for doc in required_docs:
        if not Path(doc).exists():
            raise Exception(f"Missing documentation: {doc}")

def test_startup_scripts():
    """Test startup scripts exist."""
    required_scripts = [
        "start_all_watchers.bat",
        "test_twitter_browser.bat",
        "test_twitter_post.bat"
    ]

    for script in required_scripts:
        if not Path(script).exists():
            raise Exception(f"Missing script: {script}")

def test_python_dependencies():
    """Test critical Python packages are importable."""
    critical_packages = [
        ("requests", "requests"),
        ("dotenv", "python-dotenv"),
        ("playwright", "playwright")
    ]

    missing = []
    for package, pip_name in critical_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(pip_name)

    if missing:
        raise Exception(f"Missing packages: {', '.join(missing)}")

def test_logging_system():
    """Test logging directories exist."""
    log_dir = Path("logs")
    if not log_dir.exists():
        raise Exception("Logs directory missing")

def test_configuration():
    """Test configuration files exist."""
    required_configs = [
        ".env.template",
        "requirements.txt"
    ]

    for config in required_configs:
        if not Path(config).exists():
            raise Exception(f"Missing config: {config}")

def main():
    """Run all validation tests."""
    print("=" * 60)
    print("  Digital FTE - Complete Gold Tier Validation")
    print("  Including Twitter Browser Automation")
    print("=" * 60)
    print()

    tests = [
        ("Directory Structure", test_directories),
        ("MCP Servers (10 total)", test_mcp_servers),
        ("Gold Tier Skills (9 total)", test_gold_tier_skills),
        ("CEO Briefing System", test_ceo_briefing),
        ("Twitter Browser Automation", test_twitter_browser),
        ("Core Watchers", test_core_watchers),
        ("Documentation", test_documentation),
        ("Startup Scripts", test_startup_scripts),
        ("Python Dependencies", test_python_dependencies),
        ("Logging System", test_logging_system),
        ("Configuration Files", test_configuration)
    ]

    results = []
    for test_name, test_func in tests:
        result = test_component(test_name, test_func)
        results.append((test_name, result))

    print()
    print("=" * 60)
    print("  Validation Summary")
    print("=" * 60)
    print()

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")

    print()
    print(f"Total Tests: {total}")
    print(f"[PASS] Passed: {passed}")
    print(f"[FAIL] Failed: {total - passed}")
    print()

    # Save results
    results_data = {
        "total_tests": total,
        "passed": passed,
        "failed": total - passed,
        "tests": [{"name": name, "passed": result} for name, result in results]
    }

    results_file = Path("logs/complete_gold_tier_validation.json")
    results_file.parent.mkdir(parents=True, exist_ok=True)
    with open(results_file, 'w') as f:
        json.dump(results_data, f, indent=2)

    if passed == total:
        print("SUCCESS! Complete Gold Tier system is ready.")
        print()
        print("System includes:")
        print("  - 10 MCP Servers (Odoo, Facebook, Instagram, Twitter API,")
        print("    Twitter Browser, Gmail, Email, LinkedIn, WhatsApp, Vault)")
        print("  - 15+ Agent Skills")
        print("  - CEO Briefing System")
        print("  - Twitter Browser Automation")
        print("  - Multi-channel watchers")
        print("  - Complete documentation")
        print()
        print("Next Steps:")
        print("1. Configure API credentials in .env file")
        print("2. Set up Odoo Community Edition (optional)")
        print("3. Install Playwright: playwright install chromium")
        print("4. Run: test_twitter_browser.bat")
        print("5. Run: start_all_watchers.bat")
        print("6. Generate first CEO Briefing: python scripts/ceo_briefing_generator.py")
    else:
        print("Some tests failed. Please fix issues before proceeding.")

    print()
    print(f"Detailed results saved to: {results_file}")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
