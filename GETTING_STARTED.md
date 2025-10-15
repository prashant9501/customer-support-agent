# 🚀 Getting Started with Customer Support Agent

Welcome! This guide will help you get the Customer Support Agent running in **under 10 minutes**.

---

## ⚡ Super Quick Start (5 minutes)

### Prerequisites
- Python 3.11+ installed
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Steps

```bash
# 1. Navigate to the project
cd "d:\OneDrive\2025\Training\K21 Academy\Customer Support Agent Deployment"

# 2. Run the startup script
python startup.py
```

The startup script will:
- ✅ Check all dependencies
- ✅ Verify environment configuration
- ✅ Initialize the vector database
- ✅ Test the agent workflow
- ✅ Start the development server

### Access the Application

Once the server starts, open your browser to:
- **Chat Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📋 Manual Setup (10 minutes)

If you prefer manual setup or the startup script doesn't work:

### Step 1: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy the example file
copy .env.example .env

# Edit .env and add your API key
notepad .env
```

Add this line to `.env`:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### Step 4: Initialize Vector Database

```bash
python -c "from app.database.vectordb import initialize_vectordb; initialize_vectordb()"
```

You should see:
```
Loading knowledge base from: ...
Loaded 20 documents from knowledge base
ChromaDB vector store initialized successfully
```

### Step 5: Start the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 6: Test It!

Open http://localhost:8000 and try these queries:

**Billing Query:**
```
What payment methods do you support?
```
Expected: Category = Billing, helpful response about payments

**Technical Query:**
```
Do you support on-premises deployment?
```
Expected: Category = Technical, information about deployment

**Negative Sentiment:**
```
I am extremely frustrated with your service!
```
Expected: Sentiment = Negative, escalation to human agent

---

## 🎮 Try the Interactive Demo

Want to test the agent without the UI?

```bash
python demo.py
```

Choose option:
- **1** - Automated demo with 6 test cases
- **2** - Interactive chat mode
- **3** - Both

---

## 🧪 Run Tests

Verify everything works correctly:

```bash
cd backend
pytest tests/ -v
```

All tests should pass:
```
tests/test_agents.py::TestClassifier::test_technical_query PASSED
tests/test_agents.py::TestSentiment::test_positive_sentiment PASSED
tests/test_api.py::TestHealthEndpoint::test_health_check PASSED
...
```

---

## 📁 Project Structure Overview

```
customer-support-agent/
│
├── 📚 Documentation (READ THESE)
│   ├── README.md              ← Main documentation
│   ├── QUICKSTART.md          ← This file
│   ├── DEPLOYMENT_GUIDE.md    ← Production deployment
│   └── ARCHITECTURE.md        ← System architecture
│
├── 🐍 Scripts (RUN THESE)
│   ├── startup.py             ← Start here!
│   ├── demo.py                ← Interactive demo
│   └── test_api.sh            ← Test API endpoints
│
├── ⚙️ Backend (THE CORE)
│   ├── app/
│   │   ├── main.py            ← FastAPI application
│   │   ├── agents/            ← AI agents
│   │   ├── workflows/         ← LangGraph workflow
│   │   └── database/          ← ChromaDB setup
│   ├── data/
│   │   └── router_agent_documents.json  ← Knowledge base
│   ├── requirements.txt       ← Dependencies
│   └── .env                   ← Configuration (CREATE THIS)
│
├── 🎨 Frontend (THE UI)
│   ├── index.html             ← Chat interface
│   └── static/                ← CSS & JavaScript
│
└── 🚀 Deployment (FOR PRODUCTION)
    ├── docker/                ← Docker deployment
    ├── ec2/                   ← AWS EC2 deployment
    └── lambda/                ← AWS Lambda (serverless)
```

---

## 🔧 Common Issues & Solutions

### Issue: "Module not found"

**Solution:**
```bash
# Make sure virtual environment is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Reinstall dependencies
cd backend
pip install -r requirements.txt
```

### Issue: "OpenAI API Key Invalid"

**Solution:**
1. Check your `.env` file exists in `backend/` folder
2. Verify the key starts with `sk-`
3. Test your key:
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Issue: "ChromaDB initialization fails"

**Solution:**
```bash
# Delete and recreate
cd backend
rmdir /s knowledge_base  # Windows
rm -rf knowledge_base    # Mac/Linux

# Reinitialize
python -c "from app.database.vectordb import initialize_vectordb; initialize_vectordb()"
```

### Issue: "Port 8000 already in use"

**Solution:**
```bash
# Windows - Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

### Issue: "Slow responses (>10 seconds)"

**Possible causes:**
1. Check OpenAI API status: https://status.openai.com
2. Try a faster model in `.env`:
   ```
   LLM_MODEL=gpt-4o-mini
   ```
3. Check your internet connection

---

## 🎯 What to Try First

### 1. Chat Interface (Recommended)

Open http://localhost:8000 and chat naturally!

**Sample Conversations:**

```
You: What payment methods do you support?
AI: We support credit cards (Visa, MasterCard, American Express)...
[Category: Billing | Sentiment: Neutral]

You: Do you support on-premises deployment?
AI: Yes, we fully support on-premises deployment...
[Category: Technical | Sentiment: Neutral]

You: I'm very frustrated with this!
AI: We sincerely apologize for any frustration...
[Category: General | Sentiment: Negative - Escalated to Human]
```

### 2. API Testing (For Developers)

Test the REST API directly:

```bash
# Using PowerShell
$body = @{
    query = "What is your refund policy?"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/chat" `
    -ContentType "application/json" -Body $body
```

### 3. Interactive Demo (For Testing)

```bash
python demo.py
```

Choose option 2 for interactive chat in terminal.

---

## 📚 Next Steps

### Learn More

1. **Read the Full Documentation**
   - [README.md](README.md) - Complete overview
   - [ARCHITECTURE.md](ARCHITECTURE.md) - How it works

2. **Customize the Agent**
   - Edit `backend/data/router_agent_documents.json` to add your own knowledge
   - Modify prompts in `backend/app/agents/`
   - Adjust settings in `backend/.env`

3. **Deploy to Production**
   - See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
   - Try Docker: `cd deployment/docker && docker-compose up`
   - Deploy to AWS EC2 for public access

### Experiment

**Try Different Queries:**
- "How much does it cost?" (Billing)
- "How do I integrate with AWS?" (Technical)
- "What is your company vision?" (General)
- "This product is terrible!" (Negative → Escalation)

**Modify the Knowledge Base:**
```bash
# Edit the JSON file
notepad backend\data\router_agent_documents.json

# Reinitialize database
cd backend
python -c "from app.database.vectordb import initialize_vectordb; initialize_vectordb()"

# Restart server
# Press Ctrl+C and run uvicorn again
```

**Change the Model:**
```bash
# Edit .env
LLM_MODEL=gpt-4o-mini  # Faster and cheaper

# Restart server
```

---

## 🎓 Understanding the Workflow

Every query goes through this process:

```
1. 📝 User types question
   ↓
2. 🏷️ AI categorizes it (Technical/Billing/General)
   ↓
3. 😊 AI analyzes sentiment (Positive/Neutral/Negative)
   ↓
4. 🔀 Router decides:
   - Negative? → Escalate to human
   - Technical? → Technical response
   - Billing? → Billing response
   - General? → General response
   ↓
5. 📚 Retrieves relevant documents from knowledge base
   ↓
6. 🤖 AI generates contextual response using retrieved docs
   ↓
7. ✅ Returns answer to user
```

---

## 💡 Tips for Best Results

### For Accurate Responses
- Keep your knowledge base updated
- Use clear, descriptive documents
- Tag documents with correct categories

### For Better Performance
- Use `gpt-4o-mini` for faster responses
- Reduce `RAG_TOP_K` in `.env` (default: 3)
- Add more Uvicorn workers for production

### For Cost Optimization
- Use `gpt-4o-mini` (10x cheaper than gpt-4o)
- Cache frequent queries (future enhancement)
- Monitor usage on OpenAI dashboard

---

## 🆘 Getting Help

### Documentation
- [README.md](README.md) - Full documentation
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Deployment help
- [API Docs](http://localhost:8000/docs) - Interactive API docs (when running)

### Support
- **GitHub Issues** - Report bugs
- **GitHub Discussions** - Ask questions
- **Email** - support@k21academy.com

### External Resources
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [OpenAI API Docs](https://platform.openai.com/docs)

---

## ✅ Checklist

Before you start coding/customizing:

- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with valid OpenAI API key
- [ ] Vector database initialized successfully
- [ ] Server starts without errors
- [ ] Chat interface loads in browser
- [ ] Test query returns a response
- [ ] All tests pass (`pytest tests/`)

If all checkboxes are ticked, you're ready to go! 🎉

---

## 🎉 You're Ready!

You now have a fully functional AI-powered customer support agent running locally!

**What you can do:**
- ✅ Chat with the AI
- ✅ Test different queries
- ✅ Modify the knowledge base
- ✅ Customize the UI
- ✅ Deploy to production

**Happy Coding! 🚀**

---

For detailed deployment instructions, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

For architecture details, see [ARCHITECTURE.md](ARCHITECTURE.md)

For contributing, see [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Last Updated**: October 15, 2025  
**Questions?** Open an issue or email support@k21academy.com
