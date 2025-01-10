# GTA Benchmark (Guess The Algorithm)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Required-blue.svg)](https://www.docker.com/)
[![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Demo](https://img.shields.io/badge/Demo-Live-success.svg)](http://138.197.66.242:5000/)
AI reasoning benchmark through reverse-engineering of byte transformations. Test your model's algorithmic thinking capabilities!

## Overview
GTA-Benchmark challenges participants to reverse-engineer hidden transformation algorithms by examining input-output pairs. Each puzzle provides 20 visible test cases for analysis and 20 hidden test cases for validation.

![GTA Benchmark Interface](/docs/images/interface.png)

## Live Demo
A running instance of GTA-Benchmark is available at http://138.197.66.242:5000/

⚠️ Note: This is a development instance for demonstration purposes.

![GTA Benchmark Interface](/docs/images/example.png)

## Prerequisites
- Python 3.9 or higher
- Docker
- pip (Python package installer)

## Structure
- Example puzzles are included in `puzzles/examples/`
- Actual benchmark puzzles are kept private
- All test buffers are 64 bytes

## Architecture
```mermaid
graph TD
    subgraph User Interaction
        User[User] -->|Interacts with| WebUI[Web Interface]
    end
    
    subgraph Backend
        WebUI -->|Sends code to| Flask[Flask App]
        Flask -->|Processes request via| API[API Endpoint]
        API -->|Invokes| Docker[Docker Sandbox]
        Docker -->|Runs| Runner[Code Runner]
        Runner -->|Generates| Results[Results]
        Results -->|Stores results in| Database[SQLite Database]
        Database -->|Updates| Leaderboard[Leaderboard]
        Results -->|Returns to| Flask
        Flask -->|Displays to| WebUI
        WebUI -->|Fetches leaderboard from| Leaderboard
    end
    
    subgraph Source Control
        GitHub[GitHub Repository] -->|Hosts code for| Flask & Docker & Runner
    end
    
    classDef interaction fill:#f9f,stroke:#333,stroke-width:2px;
    classDef backend fill:#bbf,stroke:#333,stroke-width:2px;
    classDef source fill:#bfb,stroke:#333,stroke-width:2px;
    
    class User,WebUI interaction;
    class Flask,API,Docker,Runner,Results,Database,Leaderboard backend;
    class GitHub source;
```

## Local Development
1. Clone the repository
2. Install requirements: `pip install -r requirements.txt`
3. Make sure Docker is running
4. Run the server: `python app.py`
5. Access the web interface at `http://localhost:5000`

## Docker Setup
The system uses Docker for secure sandbox execution of submitted solutions. Make sure:
- Docker is installed and running
- Current user has permissions to run Docker commands
- Python image `python:3.9-slim` can be pulled from Docker Hub

## Security Note
All user-submitted code runs in an isolated Docker container with:
- Memory limit: 64MB
- Execution timeout: 3 seconds
- Network access: Disabled
- Read-only filesystem
- Process limit: 100