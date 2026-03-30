# Platinum Tier - Phase 1: Cloud VM Setup (Always-On)

This guide provides the exact commands to provision and secure your Oracle Cloud Free Tier VM, install dependencies, and set up the health monitoring script according to the Platinum Tier requirements.

## 1. Provision Oracle Cloud Free Tier VM

Go to your Oracle Cloud account and create an instance with these exact specs:
- **Image**: Ubuntu 22.04 LTS
- **Shape**: `VM.Standard.A1.Flex` (ARM-based, Ampere)
- **CPU Config**: 4 OCPUs 
- **Memory**: 24 GB RAM
- **Networking**: Assign a public IPv4 address
- **SSH Keys**: Generate a new key pair or paste your public key (do NOT skip this)

*Note: The Ampere A1 shape with 4 OCPU and 24GB RAM is always-free eligible.*

## 2. Initial VM Hardening

SSH into your new VM using the default `ubuntu` user:
```bash
ssh -i /path/to/your/private_key ubuntu@<YOUR_VM_PUBLIC_IP>
```

Run the following commands to harden the VM:

```bash
# 1. Update the system
sudo apt update && sudo apt upgrade -y

# 2. Create the ai-employee user and add to sudoers
sudo adduser --disabled-password --gecos "" ai-employee
echo "ai-employee ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/ai-employee

# 3. Setup SSH directory for the new user
sudo mkdir -p /home/ai-employee/.ssh
sudo cp /home/ubuntu/.ssh/authorized_keys /home/ai-employee/.ssh/
sudo chown -R ai-employee:ai-employee /home/ai-employee/.ssh
sudo chmod 700 /home/ai-employee/.ssh
sudo chmod 600 /home/ai-employee/.ssh/authorized_keys

# 4. Disable Password Authentication & Root Login
sudo sed -i 's/^#*PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/^#*PermitRootLogin yes/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# 5. Configure UFW Firewall rules
sudo apt install ufw -y
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP (Odoo/Web)
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8069/tcp  # Odoo Default Port
sudo ufw --force enable
```

**Disconnect and reconnect as the new user:**
```bash
exit
ssh -i /path/to/your/private_key ai-employee@<YOUR_VM_PUBLIC_IP>
```

> **Oracle Cloud Specific Note:** You must ALSO open ports 80, 443, and 8069 in the **Oracle Cloud Console Security List (Ingress Rules)** for your virtual cloud network, otherwise the OS firewall rules won't matter.

## 3. Install Dependencies

Run these commands as `ai-employee`:

```bash
# 1. Install prerequisites
sudo apt install -y curl wget git software-properties-common apt-transport-https ca-certificates build-essential

# 2. Add Deadsnakes PPA and Install Python 3.13
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.13 python3.13-venv python3.13-dev python3.13-distutils

# 3. Install pip for Python 3.13
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.13

# 4. Install Node.js v24 LTS (Note: v24 might not be fully LTS yet, using v22 as fallback if needed, but targeting latest)
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -  # As of now v22 is current LTS standard, replace with v24.x when ready
sudo apt install -y nodejs

# 5. Install PM2
sudo npm install pm2@latest -g

# 6. Verify versions
python3.13 --version
node --version
pm2 --version

# 7. Setup project directory
sudo mkdir -p /opt/ai-employee
sudo chown -R ai-employee:ai-employee /opt/ai-employee
cd /opt/ai-employee

# 8. Create Python virtual environment and install pip packages
python3.13 -m venv venv
source venv/bin/activate
pip install playwright watchdog google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv requests schedule
playwright install chromium
playwright install-deps
```

## 4. Setup Health Monitoring Script

The `/opt/ai-employee/watchdog.py` script is provided in the repository.

To deploy it as a systemd service:

```bash
# Create the service file
sudo tee /etc/systemd/system/ai-watchdog.service > /dev/null << 'EOF'
[Unit]
Description=AI Employee Health Watchdog
After=network.target

[Service]
Type=simple
User=ai-employee
WorkingDirectory=/opt/ai-employee
Environment="PATH=/opt/ai-employee/venv/bin:/usr/bin:/bin"
ExecStart=/opt/ai-employee/venv/bin/python /opt/ai-employee/watchdog.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable ai-watchdog.service
sudo systemctl start ai-watchdog.service
sudo systemctl status ai-watchdog.service
```
