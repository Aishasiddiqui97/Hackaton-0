# WhatsApp Agent - Complete Production Guide

## 🚀 Quick Start (Local)

### 1. Test Input Box Fix
```bash
# Windows
test_input_box.bat

# Linux/Mac/Git Bash
bash test_input_box.sh
```

### 2. Launch Agent (Interactive Menu)
```bash
python launch_whatsapp_agent.py
```

### 3. Manual Launch Commands

**First Time (QR Scan Required):**
```bash
python whatsapp_agent.py --headful
```

**Autonomous Mode (Recommended):**
```bash
python autonomous_whatsapp_agent.py
```

**Loop Mode with Custom Interval:**
```bash
python whatsapp_agent.py --loop --interval 60 --headful
```

---

## 🐳 Docker Deployment

### Build & Run (Simple)
```bash
# Build image
docker build -f Dockerfile.whatsapp -t whatsapp-agent .

# Run container (first time - QR scan needed)
docker run -it --rm \
  --security-opt seccomp=unconfined \
  --cap-add=SYS_ADMIN \
  --shm-size=2g \
  -v $(pwd)/whatsapp_session:/app/whatsapp_session \
  -v $(pwd)/logs:/app/logs \
  whatsapp-agent
```

### Docker Compose (Production)
```bash
# Start agent
docker-compose -f docker-compose.whatsapp.yml up -d

# View logs
docker-compose -f docker-compose.whatsapp.yml logs -f

# Stop agent
docker-compose -f docker-compose.whatsapp.yml down
```

### Docker with VNC (Debug Mode)
```bash
# Start with VNC server
docker-compose -f docker-compose.whatsapp.yml --profile debug up -d whatsapp-agent-vnc

# Connect via VNC viewer to: localhost:5900
# Password: (none)
```

---

## 🔧 Troubleshooting

### Input Box Not Visible

**Solution 1: Clear Session**
```bash
# Windows
rmdir /s /q whatsapp_session
python whatsapp_agent.py --headful

# Linux/Mac
rm -rf whatsapp_session/
python whatsapp_agent.py --headful
```

**Solution 2: Force GPU Rendering**
```python
# Add to browser args:
"--use-gl=desktop",
"--enable-gpu-rasterization",
```

**Solution 3: Increase Wait Times**
```python
# In code, increase:
CHAT_OPEN_MS = 5000  # Default: 3000
MSG_LOAD_WAIT = 5    # Default: 3
```

### Security Warnings in Console

Normal behavior with `--no-sandbox`. These warnings don't affect functionality:
```
[WARNING] Running as root without --no-sandbox is not supported
```

To suppress (not recommended for production):
```python
args.append("--disable-logging")
```

### WhatsApp Web Not Loading

**Check 1: Internet Connection**
```bash
ping web.whatsapp.com
```

**Check 2: Phone Connection**
- Ensure phone has internet
- WhatsApp app is running
- Phone is not in airplane mode

**Check 3: Session Corruption**
```bash
# Clear and rescan
rm -rf whatsapp_session/
python whatsapp_agent.py --headful
```

### Container/Docker Issues

**Issue: Permission Denied**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

**Issue: Shared Memory Too Small**
```bash
# Increase shm-size
docker run --shm-size=2g ...
```

**Issue: Chrome Crashes in Container**
```bash
# Add more capabilities
docker run --cap-add=SYS_ADMIN --security-opt seccomp=unconfined ...
```

---

## 📊 Performance Optimization

### Memory Usage
```python
# Reduce memory footprint
browser = pw.chromium.launch_persistent_context(
    args=[
        "--disable-dev-shm-usage",
        "--disable-gpu",  # Only if input box works without it
        "--disable-software-rasterizer",
        "--single-process",  # Reduces memory but less stable
    ]
)
```

### CPU Usage
```python
# Reduce CPU usage
CHECK_INTERVAL = 30  # Increase scan interval (default: 15)
CHAT_LOAD_WAIT = 3   # Reduce wait times if network is fast
```

### Network Optimization
```python
# Block unnecessary resources
page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2}", lambda route: route.abort())
page.route("**/crashlogs.whatsapp.net/**", lambda route: route.abort())
```

---

## 🔒 Security Best Practices

### 1. Use Containers
Always run with `--no-sandbox` inside containers, never on host:
```bash
docker run --security-opt seccomp=unconfined ...
```

### 2. Network Isolation
```yaml
# docker-compose.yml
networks:
  whatsapp_net:
    driver: bridge
    internal: true  # No external access except WhatsApp
```

### 3. Read-Only Filesystem
```bash
docker run --read-only \
  -v $(pwd)/whatsapp_session:/app/whatsapp_session \
  -v $(pwd)/logs:/app/logs \
  whatsapp-agent
```

### 4. Resource Limits
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
```

---

## 📈 Monitoring & Logging

### Log Files
```bash
# View agent logs
tail -f logs/whatsapp_agent.log

# View Docker logs
docker logs -f whatsapp_autonomous_agent
```

### Health Checks
```bash
# Check if agent is running
docker ps | grep whatsapp

# Check session validity
ls -lah whatsapp_session/

# Check last activity
tail -n 20 logs/whatsapp_agent.log
```

### Metrics
```python
# Add to code for monitoring
import psutil
import time

def log_metrics():
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    print(f"CPU: {cpu}% | Memory: {mem}%")
```

---

## 🎯 Hackathon Tips

### Fast Iteration
```bash
# Use test script for quick validation
python test_input_box.py
```

### Debug Mode
```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Demo Mode
```python
# Slow down for presentation
SEND_DELAY_MS = 100  # Slower typing
CHAT_OPEN_MS = 2000  # Visible transitions
```

---

## 📝 Checklist for Production

- [ ] Input box renders correctly (test_input_box.py)
- [ ] QR code scanned and session saved
- [ ] Agent runs in loop mode without crashes
- [ ] Messages are read correctly
- [ ] Replies are sent successfully
- [ ] Logs are being written
- [ ] Obsidian vault integration works
- [ ] Docker container runs stable for 1+ hour
- [ ] Resource usage is acceptable (<2GB RAM, <50% CPU)
- [ ] Error handling works (network drops, WhatsApp updates)

---

**Last Updated:** 2026-03-16
**Tested Environments:** Windows 10/11, Ubuntu 22.04, Docker (Debian/Alpine)
**WhatsApp Web Version:** 2025-2026 selectors
