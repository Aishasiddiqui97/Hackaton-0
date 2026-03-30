#!/usr/bin/env python3
"""
Platinum Tier - Cloud VM Watchdog Script
Path: /opt/ai-employee/watchdog.py
Runs as a systemd service to monitor PM2 and critical agent processes.
"""

import os
import sys
import time
import subprocess
import json
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables (expecting /opt/ai-employee/.env)
load_dotenv()

# Setup paths
VAULT_SYNC_DIR = os.getenv("VAULT_SYNC_DIR", "/opt/ai-employee/AI_Employee_Vault_Sync")
LOG_DIR = os.path.join(VAULT_SYNC_DIR, "Logs")
HEALTH_MD_PATH = os.path.join(LOG_DIR, "health.md")

# Ensure directories exist
Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

# Setup basic logging locally to the VM
logging.basicConfig(
    filename='/var/log/ai-employee-watchdog.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("watchdog")

class AIWatchdog:
    def __init__(self):
        self.check_interval = 60 # Check every 60 seconds
        self.critical_processes = [
            "gmail_cloud_watcher",
            "social_cloud_watcher",
            "cloud_orchestrator",
            "vault_sync",
            "odoo_health_check"
        ]

    def _run_cmd(self, cmd):
        """Run a shell command and return output"""
        try:
            result = subprocess.run(
                cmd, shell=True, check=True, 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr

    def get_pm2_status(self):
        """Get PM2 JSON status output"""
        success, output = self._run_cmd("pm2 jlist")
        if not success:
            logger.error(f"Failed to run pm2 jlist: {output}")
            return None

        try:
            data = json.loads(output)
            processes = {}
            for item in data:
                name = item.get("name")
                status = item.get("pm2_env", {}).get("status")
                restarts = item.get("pm2_env", {}).get("restart_time", 0)
                processes[name] = {"status": status, "restarts": restarts}
            return processes
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse PM2 output: {e}")
            return None

    def write_health_alert(self, message):
        """Write an alert to Vault/Logs/health.md"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"## 🚨 Health Alert: {timestamp}\n{message}\n\n"
        
        try:
            # Append to file
            with open(HEALTH_MD_PATH, "a", encoding="utf-8") as f:
                f.write(entry)
            logger.error(f"ALERT WRITTEN: {message}")
        except Exception as e:
            logger.error(f"Failed to write health alert to vault: {e}")

    def restart_process(self, process_name):
        """Restart a specific process via PM2"""
        logger.warning(f"Attempting to auto-restart critical process: {process_name}")
        success, output = self._run_cmd(f"pm2 restart {process_name}")
        if success:
            logger.info(f"Successfully restarted {process_name}")
            return True
        else:
            logger.error(f"Failed to restart {process_name}: {output}")
            return False

    def check_health(self):
        """Main health check loop"""
        processes = self.get_pm2_status()
        if not processes:
            self.write_health_alert("Error: Unable to fetch PM2 status. PM2 daemon might be dead.")
            return

        failed_processes = []
        for p_name in self.critical_processes:
            p_data = processes.get(p_name)
            
            if not p_data:
                logger.warning(f"Process {p_name} is not registered in PM2.")
                # We don't alert here immediately unless it was supposed to be running
                continue
                
            status = p_data.get("status")
            if status != "online":
                failed_processes.append(p_name)
                alert_msg = f"Critical process '{p_name}' went offline. Status: {status}."
                self.write_health_alert(alert_msg)
                
                # Attempt Auto-Restart
                if self.restart_process(p_name):
                    self.write_health_alert(f"Auto-recovery: process '{p_name}' restarted successfully via Watchdog.")
                else:
                    self.write_health_alert(f"Auto-recovery FAILED: process '{p_name}' could not be restarted.")

    def run(self):
        """Start the watchdog daemon"""
        logger.info("Watchdog started.")
        while True:
            try:
                self.check_health()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.critical(f"Watchdog hit a critical failure: {e}")
                self.write_health_alert(f"Watchdog daemon encountered critical exception: {e}")
                time.sleep(10)

if __name__ == "__main__":
    if os.geteuid() == 0:
        print("Warning: Watchdog running as root. It should run as ai-employee user.")
    
    dog = AIWatchdog()
    dog.run()
