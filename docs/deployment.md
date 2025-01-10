# Deployment Guide

## Repository Structure
GTA-Benchmark uses two repositories:
- Public repo (gta-benchmark): Contains the framework, web interface, and example puzzles
- Private repo (gta-benchmark-puzzles): Contains the actual benchmark puzzles

## Local Development
For local development, you can run the system with just the public repo. It will automatically fall back to example puzzles if benchmark puzzles are not present.

## Full Deployment
To deploy the complete benchmark:

1. Requirements:
   - Python 3.9 or higher
   - Docker
   - Git access to both public and private repositories

2. Basic deployment steps:
   ```bash
   # Clone public repo
   git clone https://github.com/[username]/gta-benchmark.git
   cd gta-benchmark
   
   # Clone private puzzle repo into puzzles/benchmark
   git clone https://github.com/[username]/gta-benchmark-puzzles.git tmp
   cp -r tmp/puzzles/benchmark puzzles/
   rm -rf tmp
   
   # Setup Python environment
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   
   # Start server
   python app.py

3. Environment Variables:
   - FLASK_ENV: Set to 'production' for deployment
   - FLASK_SECRET_KEY: Set a secure secret key
   - Additional configuration coming soon

Security Notes
   - Keep the private repository credentials secure
   - Regular database backups recommended
   - Monitor server resources and Docker container usage