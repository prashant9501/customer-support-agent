# Complete Deployment Guide

This guide covers all deployment options for the Customer Support Agent.

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [AWS EC2 Production Deployment](#aws-ec2-production-deployment)
4. [AWS Lambda Serverless](#aws-lambda-serverless)
5. [SSL Configuration](#ssl-configuration)
6. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Local Development

### Initial Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# 2. Install dependencies
cd backend
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env

# 4. Edit .env and add your OpenAI API key
OPENAI_API_KEY=sk-your-key-here
```

### Initialize Vector Database

```bash
# From backend directory
python -c "from app.database.vectordb import initialize_vectordb; initialize_vectordb()"
```

### Run Development Server

```bash
# From backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Access at: http://localhost:8000

---

## Docker Deployment

### Prerequisites
- Docker 24+
- Docker Compose 2.0+

### Quick Start

```bash
# 1. Navigate to docker directory
cd deployment/docker

# 2. Create .env file
cat > .env << EOF
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4o
LOG_LEVEL=INFO
EOF

# 3. Build and start services
docker-compose up -d

# 4. View logs
docker-compose logs -f backend

# 5. Check status
docker-compose ps
```

Access at: http://localhost

### Docker Commands

```bash
# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# View backend logs
docker-compose logs -f backend

# View nginx logs
docker-compose logs -f nginx

# Shell into backend container
docker-compose exec backend bash

# Remove all containers and volumes
docker-compose down -v
```

### Troubleshooting Docker

**Issue: Container fails to start**
```bash
# Check logs
docker-compose logs backend

# Rebuild
docker-compose up -d --build --force-recreate
```

**Issue: ChromaDB initialization fails**
```bash
# Remove volume and restart
docker-compose down -v
docker-compose up -d
```

---

## AWS EC2 Production Deployment

### Step 1: Launch EC2 Instance

**Instance Configuration:**
- **AMI**: Ubuntu 22.04 LTS (ami-0c7217cdde317cfec)
- **Instance Type**: t3.medium (2 vCPU, 4GB RAM)
- **Storage**: 20GB gp3 SSD
- **Key Pair**: Create or select existing

**Security Group Rules:**
| Type | Protocol | Port | Source |
|------|----------|------|--------|
| SSH | TCP | 22 | Your IP |
| HTTP | TCP | 80 | 0.0.0.0/0 |
| HTTPS | TCP | 443 | 0.0.0.0/0 |

**Advanced Details:**
- Enable detailed CloudWatch monitoring
- Add IAM role if using AWS services (S3, CloudWatch, etc.)

### Step 2: Connect to Instance

```bash
# Download your key pair file and set permissions
chmod 400 your-key.pem

# Connect via SSH
# ssh -i your-key.pem ubuntu@your-ec2-public-ip
ssh -i support-agent-key.pem ubuntu@13.232.49.8
```

### Step 3: Clone Repository

```bash
# Install git if not present
sudo apt update
sudo apt install git -y

# Clone repository
cd /home/ubuntu
git clone https://github.com/your-username/customer-support-agent.git
cd customer-support-agent
```

### Step 4: Run Automated Setup

```bash
cd deployment/ec2
chmod +x setup.sh
sudo ./setup.sh
```

The setup script will:
- Update system packages
- Install Python 3.11, NGINX, and dependencies
- Create virtual environment
- Install Python packages
- Setup systemd service
- Configure NGINX
- Configure firewall (UFW)

### Step 5: Configure API Key

```bash
# Edit .env file
sudo nano /home/ubuntu/customer-support-agent/backend/.env
```

Add your OpenAI API key:
```env
OPENAI_API_KEY=sk-your-actual-key-here
```

Save and exit (Ctrl+X, Y, Enter)

### Step 6: Start the Service

```bash
# Restart the service
sudo systemctl restart support-agent

# Check status
sudo systemctl status support-agent

# Enable auto-start on boot (should already be enabled)
sudo systemctl enable support-agent
```

### Step 7: Verify Deployment

```bash
# Check if service is running
curl http://localhost:8000/health

# Check NGINX
curl http://localhost/health

# View logs
sudo journalctl -u support-agent -f
```

### Step 8: Access Your Application

Open in browser: `http://YOUR_EC2_PUBLIC_IP`

To find your public IP:
```bash
curl http://169.254.169.254/latest/meta-data/public-ipv4
```

---

## SSL Configuration

### Option 1: Let's Encrypt (Free SSL)

**Prerequisites:**
- Domain name pointing to your EC2 instance
- DNS A record configured

**Steps:**

```bash
# 1. Install Certbot (should already be installed by setup script)
sudo apt install certbot python3-certbot-nginx -y

# 2. Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 3. Follow the prompts:
#    - Enter email address
#    - Agree to terms of service
#    - Choose whether to redirect HTTP to HTTPS (recommended: Yes)

# 4. Test auto-renewal
sudo certbot renew --dry-run
```

Certificate will auto-renew every 90 days via cron job.

### Option 2: Custom SSL Certificate

If you have your own SSL certificates:

```bash
# 1. Copy certificates to server
scp -i your-key.pem cert.pem ubuntu@your-ec2-ip:/home/ubuntu/
scp -i your-key.pem key.pem ubuntu@your-ec2-ip:/home/ubuntu/

# 2. Move to secure location
sudo mkdir -p /etc/nginx/ssl
sudo mv /home/ubuntu/cert.pem /etc/nginx/ssl/
sudo mv /home/ubuntu/key.pem /etc/nginx/ssl/
sudo chmod 600 /etc/nginx/ssl/key.pem

# 3. Update NGINX configuration
sudo nano /etc/nginx/sites-available/support-agent
```

Uncomment and modify the SSL server block:
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # ... rest of configuration
}
```

```bash
# 4. Test and reload NGINX
sudo nginx -t
sudo systemctl reload nginx
```

---

## AWS Lambda Serverless

### Prerequisites
- AWS Account
- AWS CLI configured
- Python 3.11+

### Step 1: Package Dependencies

```bash
cd deployment/lambda

# Create deployment package directory
mkdir -p package

# Install dependencies
pip install -r requirements.txt -t package/

# Add application code
cp -r ../../backend/app package/
cp -r ../../backend/data package/
cp lambda_handler.py package/

# Create ZIP file
cd package
zip -r ../lambda-deployment.zip .
cd ..
```

**Note**: The package size may exceed Lambda's 50MB limit. Consider using Lambda Layers.

### Step 2: Create Lambda Layer (for large dependencies)

```bash
# Create layer for langchain and dependencies
mkdir -p layer/python
pip install langchain langchain-openai langchain-chroma -t layer/python/
cd layer
zip -r ../langchain-layer.zip .
cd ..
```

### Step 3: Create Lambda Function

**Via AWS Console:**

1. Go to AWS Lambda Console
2. Click "Create function"
3. Choose "Author from scratch"
4. Configuration:
   - Function name: `customer-support-agent`
   - Runtime: Python 3.11
   - Architecture: x86_64
5. Click "Create function"

### Step 4: Upload Code

**Option A: Upload ZIP (< 50MB)**
- In Lambda console, go to "Code" tab
- Click "Upload from" → ".zip file"
- Select `lambda-deployment.zip`

**Option B: Use S3 (> 50MB)**
```bash
# Upload to S3
aws s3 cp lambda-deployment.zip s3://your-bucket/lambda-deployment.zip

# Update Lambda from S3
aws lambda update-function-code \
  --function-name customer-support-agent \
  --s3-bucket your-bucket \
  --s3-key lambda-deployment.zip
```

### Step 5: Configure Lambda

**Environment Variables:**
```
OPENAI_API_KEY=sk-your-key
```

**Settings:**
- Memory: 1024 MB (minimum)
- Timeout: 30 seconds
- Handler: `lambda_handler.lambda_handler`

**Add Layer** (if using layers):
- Click "Add a layer"
- Choose "Custom layers"
- Select your langchain layer

### Step 6: Create API Gateway

1. Go to API Gateway Console
2. Create "REST API"
3. Create resource: `/api`
4. Create method: `POST` → Lambda Integration
5. Select your Lambda function
6. Deploy API to stage (e.g., "prod")

### Step 7: Test

```bash
# Get your API endpoint from API Gateway console
API_URL="https://your-api-id.execute-api.region.amazonaws.com/prod"

# Test
curl -X POST $API_URL/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What payment methods do you support?"}'
```

---

## Monitoring & Maintenance

### Logs

**EC2 - Systemd Logs:**
```bash
# View real-time logs
sudo journalctl -u support-agent -f

# View last 100 lines
sudo journalctl -u support-agent -n 100

# View logs from today
sudo journalctl -u support-agent --since today
```

**EC2 - Application Logs:**
```bash
# View application log file
tail -f /home/ubuntu/customer-support-agent/backend/agent.log
```

**Docker Logs:**
```bash
docker-compose logs -f backend
docker-compose logs --tail=100 backend
```

### Health Checks

```bash
# Check application health
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","vectordb":"connected","timestamp":"..."}
```

### Service Management

**EC2:**
```bash
# Start service
sudo systemctl start support-agent

# Stop service
sudo systemctl stop support-agent

# Restart service
sudo systemctl restart support-agent

# Check status
sudo systemctl status support-agent

# Enable auto-start
sudo systemctl enable support-agent
```

**Docker:**
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart backend
```

### Performance Monitoring

**Monitor System Resources:**
```bash
# CPU and Memory usage
htop

# Disk usage
df -h

# Network connections
netstat -tunlp | grep 8000
```

**Monitor Application:**
```bash
# Request count and response times (from logs)
sudo journalctl -u support-agent | grep "INFO" | tail -50

# Check for errors
sudo journalctl -u support-agent | grep "ERROR"
```

### Backup

**Backup ChromaDB:**
```bash
# Create backup
tar -czf chromadb-backup-$(date +%Y%m%d).tar.gz \
  /home/ubuntu/customer-support-agent/backend/knowledge_base

# Restore from backup
tar -xzf chromadb-backup-20250115.tar.gz -C /home/ubuntu/customer-support-agent/backend/
```

**Backup Configuration:**
```bash
# Backup .env and configs
tar -czf config-backup-$(date +%Y%m%d).tar.gz \
  /home/ubuntu/customer-support-agent/backend/.env \
  /etc/nginx/sites-available/support-agent \
  /etc/systemd/system/support-agent.service
```

### Updates

**Update Application Code:**
```bash
cd /home/ubuntu/customer-support-agent
git pull origin main

# Restart service
sudo systemctl restart support-agent
```

**Update Python Dependencies:**
```bash
cd /home/ubuntu/customer-support-agent
source venv/bin/activate
cd backend
pip install --upgrade -r requirements.txt

# Restart service
sudo systemctl restart support-agent
```

**Update Knowledge Base:**
```bash
# Edit knowledge base
nano /home/ubuntu/customer-support-agent/backend/data/router_agent_documents.json

# Reinitialize vector database
cd /home/ubuntu/customer-support-agent/backend
source ../venv/bin/activate
python -c "from app.database.vectordb import initialize_vectordb; initialize_vectordb()"

# Restart service
sudo systemctl restart support-agent
```

---

## Scaling Strategies

### Vertical Scaling (Single Server)

**Increase EC2 Instance Size:**
1. Stop instance
2. Change instance type (e.g., t3.medium → t3.large)
3. Start instance

**Increase Workers:**
Edit `/etc/systemd/system/support-agent.service`:
```
ExecStart=/home/ubuntu/customer-support-agent/venv/bin/uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 8  # Increase workers
```

Restart: `sudo systemctl restart support-agent`

### Horizontal Scaling (Multiple Servers)

**Option 1: Application Load Balancer (ALB)**

1. Create multiple EC2 instances with the same setup
2. Create ALB in AWS Console
3. Add EC2 instances to target group
4. Configure health checks: `/health`
5. Point domain to ALB DNS

**Option 2: Docker Swarm**

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml support-agent

# Scale service
docker service scale support-agent_backend=3
```

---

## Cost Optimization

### Tips to Reduce Costs

1. **Use GPT-4o-mini** instead of GPT-4o (10x cheaper)
   ```env
   LLM_MODEL=gpt-4o-mini
   ```

2. **Use Reserved Instances** for EC2 (40% savings)

3. **Enable EC2 Auto Scaling** - scale down during low traffic

4. **Cache Frequent Queries** - implement Redis caching

5. **Set OpenAI Rate Limits** - prevent unexpected bills
   ```python
   # In settings.py
   max_tokens: int = 500  # Limit response length
   ```

6. **Monitor Usage** - Set up billing alerts in AWS

---

## Security Best Practices

1. **Never commit .env files** to git
2. **Rotate API keys** regularly
3. **Use IAM roles** for AWS services (not access keys)
4. **Enable CloudWatch logs** for auditing
5. **Keep dependencies updated**: `pip install --upgrade`
6. **Use HTTPS** in production (Let's Encrypt)
7. **Implement rate limiting** to prevent abuse
8. **Regular security audits** of dependencies

---

## Troubleshooting Common Issues

### Service Won't Start

```bash
# Check service status
sudo systemctl status support-agent

# Check logs for errors
sudo journalctl -u support-agent -n 50

# Common fixes:
# 1. Check .env file exists and has valid API key
# 2. Check Python path in service file
# 3. Check file permissions: sudo chown -R ubuntu:ubuntu /home/ubuntu/customer-support-agent
```

### High Memory Usage

```bash
# Check memory
free -h

# Reduce workers in service file
# Restart: sudo systemctl restart support-agent
```

### Slow Response Times

1. Check OpenAI API status: https://status.openai.com
2. Use faster model: `LLM_MODEL=gpt-4o-mini`
3. Reduce RAG_TOP_K: `RAG_TOP_K=2`
4. Add more workers (if CPU available)

---

## Support

- **Documentation**: See README.md
- **Issues**: GitHub Issues
- **Email**: support@k21academy.com

---

**Last Updated**: October 15, 2025
