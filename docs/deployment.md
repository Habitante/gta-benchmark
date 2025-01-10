# Deployment Guide

## Repository Structure
GTA-Benchmark uses two repositories:
- Public repo (gta-benchmark): Contains the framework, web interface, and example puzzles
- Private repo (gta-benchmark-puzzles): Contains the actual benchmark puzzles

## Local Development
For local development, you can run the system with just the public repo. It will automatically fall back to example puzzles if benchmark puzzles are not present.

```bash
# Clone public repo
git clone https://github.com/[username]/gta-benchmark.git
cd gta-benchmark

# Setup Python environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run development server
python app.py
```

## Production Deployment

### 1. Requirements
- Ubuntu 22.04 LTS
- Python 3.9 or higher
- Docker
- Git access to both public and private repositories

### 2. Initial Server Setup
```bash
# Update system
apt update && apt upgrade -y

# Install required packages
apt install -y python3-pip python3-venv git docker.io

# Start and enable Docker
systemctl start docker
systemctl enable docker
```

### 3. Application Setup
```bash
# Create application directory
mkdir /opt/gta-benchmark
cd /opt/gta-benchmark

# Clone public repo
git clone https://github.com/[username]/gta-benchmark.git .

# Clone private puzzle repo and copy puzzles
git clone https://github.com/[username]/gta-benchmark-puzzles.git tmp
cp -r tmp/puzzles/benchmark puzzles/
rm -rf tmp

# Setup Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Environment Configuration
Create `.env` file in `/opt/gta-benchmark/`:
```
FLASK_ENV=production
FLASK_SECRET_KEY=[generate-a-secure-key]
DATABASE_URL=sqlite:///puzzle_bench.db
```

### 5. Production Server Setup

1. Install Gunicorn:
```bash
pip install gunicorn
pip freeze > requirements.txt
```

2. Create system service file `/etc/systemd/system/gta-benchmark.service`:
```ini
[Unit]
Description=GTA Benchmark
After=network.target

[Service]
User=root
WorkingDirectory=/opt/gta-benchmark
Environment="PATH=/opt/gta-benchmark/venv/bin"
ExecStart=/opt/gta-benchmark/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 wsgi:app

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:
```bash
systemctl daemon-reload
systemctl enable gta-benchmark
systemctl start gta-benchmark
```

4. Configure firewall:
```bash
ufw allow 5000
```

## Maintenance and Updates

### Updating the Application

1. SSH into the server:
```bash
ssh root@[server-ip]
```

2. Navigate to project directory and pull changes:
```bash
cd /opt/gta-benchmark
git pull
```

3. Restart the service:
```bash
systemctl restart gta-benchmark
```

4. Verify the service is running:
```bash
systemctl status gta-benchmark
```

### Useful Commands

#### Service Management
- Start service: `systemctl start gta-benchmark`
- Stop service: `systemctl stop gta-benchmark`
- Restart service: `systemctl restart gta-benchmark`
- Check status: `systemctl status gta-benchmark`

#### Logs
- View service logs: `journalctl -u gta-benchmark`
- Follow logs live: `journalctl -u gta-benchmark -f`
- View last 100 lines: `journalctl -u gta-benchmark -n 100`

## Security Notes
- Keep the private repository credentials secure
- Regular database backups recommended
- Monitor server resources and Docker container usage
- Keep system and packages updated regularly
- Consider setting up HTTPS with Let's Encrypt (coming soon)

# Updating Levels

1. Clean current benchmark folder
rm -rf puzzles/benchmark/*

2. Clone private repo using SSH URL and copy new levels
git clone git@github.com:habitante/gta-benchmark-puzzles.git tmp
cp -r tmp/puzzles/benchmark/* puzzles/benchmark/
rm -rf tmp

3. Restart the service:
systemctl restart gta-benchmark