# Customer Support Agent

AI-powered customer support system with LangGraph workflow orchestration, RAG (Retrieval-Augmented Generation), and intelligent routing.

## Features

- 🤖 **AI-Powered Responses**: Uses OpenAI GPT-4o-mini for intelligent customer support
- 🔍 **RAG with ChromaDB**: Vector database for knowledge base retrieval
- 🎯 **Smart Routing**: Automatic categorization (Technical, Billing, General)
- 😊 **Sentiment Analysis**: Detects customer sentiment (Positive, Neutral, Negative)
- 🔄 **LangGraph Workflows**: State-based conversation management
- 🚀 **Production Ready**: FastAPI backend with NGINX reverse proxy
- 📊 **Real-time & REST APIs**: WebSocket and HTTP endpoints

## Quick Start

### Prerequisites

- AWS EC2 instance (Ubuntu 24.04 LTS, t2.medium or larger)
- OpenAI API key
- Domain name (optional, for HTTPS)

### Deployment on EC2

1. **Clone the repository:**
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git ~/customer-support-agent
cd ~/customer-support-agent
```

2. **Run the setup script:**
```bash
sudo chmod +x deployment/ec2/setup.sh
sudo deployment/ec2/setup.sh
```

3. **Configure your OpenAI API key:**
```bash
sudo nano ~/customer-support-agent/backend/.env
# Add: OPENAI_API_KEY=sk-your-actual-key-here
```

4. **Restart the service:**
```bash
sudo systemctl restart support-agent
```

5. **Access your application:**
- Frontend: `http://YOUR-EC2-IP/`
- API Docs: `http://YOUR-EC2-IP/docs`
- Health Check: `http://YOUR-EC2-IP/health`

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── agents/          # AI agent modules
│   │   ├── config/          # Configuration
│   │   ├── database/        # ChromaDB integration
│   │   ├── models/          # Pydantic schemas
│   │   ├── workflows/       # LangGraph workflows
│   │   └── main.py          # FastAPI application
│   ├── data/                # Knowledge base JSON
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment variables template
├── frontend/
│   ├── index.html           # Web UI
│   └── static/              # CSS, JS, images
└── deployment/
    ├── ec2/                 # EC2 deployment files
    │   ├── setup.sh         # Automated setup script
    │   ├── nginx/           # NGINX configuration
    │   └── systemd/         # Systemd service
    └── docker/              # Docker deployment (optional)
```

## Configuration

Edit `backend/.env`:

```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional (defaults provided)
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
API_PORT=8000
```

## API Endpoints

- `POST /api/chat` - Send a customer query
- `GET /health` - Health check
- `GET /api/status` - API status
- `WS /ws/chat` - WebSocket chat endpoint

## Managing the Service

```bash
# Check status
sudo systemctl status support-agent

# View logs
sudo journalctl -u support-agent -f

# Restart
sudo systemctl restart support-agent

# Stop
sudo systemctl stop support-agent
```

## Tech Stack

- **Backend**: FastAPI, Python 3.12
- **AI**: OpenAI GPT-4o-mini, LangChain, LangGraph
- **Database**: ChromaDB (vector database)
- **Web Server**: NGINX
- **Process Manager**: Systemd
- **Frontend**: Vanilla HTML/CSS/JavaScript

## License

MIT License

## Support

For issues and questions, please open a GitHub issue.
