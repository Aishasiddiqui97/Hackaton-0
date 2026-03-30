# Platinum Tier - Phase 5: Odoo 19 Community Setup

This document provides the exact commands and configuration to deploy Odoo 19 Community Edition via Docker on your Oracle Cloud VM.

## 1. Prepare Directory Structure

Run these commands as the `ai-employee` user on the Cloud VM:

```bash
mkdir -p /opt/ai-employee/odoo/config
mkdir -p /opt/ai-employee/odoo/addons
mkdir -p /opt/ai-employee/odoo/backups
cd /opt/ai-employee/odoo
```

## 2. Create the Docker Compose File

Create `docker-compose.yml` in `/opt/ai-employee/odoo/`:

```yaml
version: '3.1'

services:
  web:
    image: odoo:19.0
    depends_on:
      - db
    ports:
      - "8069:8069"
    volumes:
      - odoo-web-data:/var/lib/odoo
      - ./config:/etc/odoo
      - ./addons:/mnt/extra-addons
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=my_strong_db_password

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_PASSWORD=my_strong_db_password
      - POSTGRES_USER=odoo
      - PGDATA=/var/lib/postgresql/data/pgdata
    volumes:
      - odoo-db-data:/var/lib/postgresql/data/pgdata

volumes:
  odoo-web-data:
  odoo-db-data:
```

*Replace `my_strong_db_password` with a secure password.*

## 3. Create Odoo Config File

Create `/opt/ai-employee/odoo/config/odoo.conf`:

```ini
[options]
admin_passwd = secure_admin_master_password
```

## 4. Start Odoo

Make sure Docker is installed first (if it wasn't installed in Phase 1):
```bash
sudo apt-get install docker.io docker-compose -y
sudo usermod -aG docker ai-employee
# Disconnect and reconnect to apply the docker group
```

Then start the container:
```bash
cd /opt/ai-employee/odoo
docker-compose up -d
```

Check the logs to ensure it's running:
```bash
docker-compose logs -f web
```

## 5. Setup Automated Backups

Create a backup script `/opt/ai-employee/odoo/backup_odoo.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/opt/ai-employee/odoo/backups"
TIMESTAMP=$(date +"%F")
DOCKER_CONTAINER="odoo-db-1" # Check container name with 'docker compose ps'
DB_USER="odoo"

mkdir -p $BACKUP_DIR
docker exec -t $DOCKER_CONTAINER pg_dumpall -c -U $DB_USER > $BACKUP_DIR/db_backup_$TIMESTAMP.sql
chmod 600 $BACKUP_DIR/db_backup_$TIMESTAMP.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -type f -name "*.sql" -mtime +7 -exec rm {} \;
```

Make it executable and add to crontab:
```bash
chmod +x /opt/ai-employee/odoo/backup_odoo.sh
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/ai-employee/odoo/backup_odoo.sh") | crontab -
```

## 6. Accessing Odoo
Odoo will be available at `http://<YOUR_VM_PUBLIC_IP>:8069`.
Set up your master database using the `secure_admin_master_password` defined in the config.

The health endpoint `http://<YOUR_VM_PUBLIC_IP>:8069/web/webclient/version_info` can be monitored by the watchdog.
