module.exports = {
  apps: [
    {
      name: "vault_sync",
      script: "vault_sync.py",
      interpreter: "python3",
      cwd: "/opt/ai-employee",
      env: {
        VAULT_SYNC_DIR: "/opt/ai-employee/AI_Employee_Vault_Sync",
        IS_CLOUD_VM: "true"
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_restarts: 10,
      log_date_format: "YYYY-MM-DD HH:mm:ss Z",
      error_file: "AI_Employee_Vault_Sync/Logs/pm2_vault_sync_error.log",
      out_file: "AI_Employee_Vault_Sync/Logs/pm2_vault_sync_out.log",
      merge_logs: true,
      exec_mode: "fork"
    },
    {
      name: "gmail_cloud_watcher",
      script: "gmail_cloud_watcher.py",
      interpreter: "python3",
      cwd: "/opt/ai-employee",
      env: {
        VAULT_SYNC_DIR: "/opt/ai-employee/AI_Employee_Vault_Sync"
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_restarts: 10,
      log_date_format: "YYYY-MM-DD HH:mm:ss Z",
      error_file: "AI_Employee_Vault_Sync/Logs/pm2_gmail_error.log",
      out_file: "AI_Employee_Vault_Sync/Logs/pm2_gmail_out.log"
    },
    {
      name: "social_cloud_watcher",
      script: "social_cloud_watcher.py",
      interpreter: "python3",
      cwd: "/opt/ai-employee",
      env: {
        VAULT_SYNC_DIR: "/opt/ai-employee/AI_Employee_Vault_Sync"
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_restarts: 10,
      log_date_format: "YYYY-MM-DD HH:mm:ss Z"
    },
    {
      name: "cloud_orchestrator",
      script: "cloud_orchestrator.py",
      interpreter: "python3",
      cwd: "/opt/ai-employee",
      env: {
        VAULT_SYNC_DIR: "/opt/ai-employee/AI_Employee_Vault_Sync"
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_restarts: 10,
      log_date_format: "YYYY-MM-DD HH:mm:ss Z"
    },
    {
      name: "odoo_mcp",
      script: "odoo_mcp_server.py",
      interpreter: "python3",
      cwd: "/opt/ai-employee",
      env: {
        VAULT_SYNC_DIR: "/opt/ai-employee/AI_Employee_Vault_Sync"
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "150M"
    }
  ]
};
