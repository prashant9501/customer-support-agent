# Deployment Guide

Complete guide for deploying the Customer Support Agent on AWS EC2.

## Prerequisites

### 1. AWS EC2 Instance
- **OS**: Ubuntu 24.04 LTS
- **Instance Type**: t2.medium or larger (2 vCPU, 4GB RAM minimum)
- **Storage**: 20GB EBS volume
- **Security Group**: Open ports 22 (SSH), 80 (HTTP), 443 (HTTPS)

### 2. OpenAI API Key
- Sign up at [OpenAI Platform](https://platform.openai.com/)
- Create an API key from API keys section
- Ensure you have credits available

### 3. Domain Name (Optional)
- For HTTPS/SSL certificates
- Configure DNS A record pointing to EC2 public IP

## Step-by-Step Deployment

### Step 1: Launch EC2 Instance

1. Go to AWS Console → EC2 → Launch Instance
2. Choose **Ubuntu Server 24.04 LTS**
3. Select **t2.medium** instance type
4. Configure Security Group:
   - SSH (22): Your IP
   - HTTP (80): 0.0.0.0/0
   - HTTPS (443): 0.0.0.0/0
5. Create/select a key pair
6. Launch instance

### Step 2: Connect to EC2

```bash
# From your local machine
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@YOUR-EC2-PUBLIC-IP
```

### Step 3: Clone Repository

```bash
# Clone your repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git ~/customer-support-agent
```

#### Change File Ownership
You need to change the owner of the entire application directory from root to the ubuntu user. This will allow your application to write to the database.
Run this single command from your home directory (~):
```bash
# Navigate to the directory
cd ~/customer-support-agent

sudo chown -R ubuntu:ubuntu /home/ubuntu/customer-support-agent
```

### Step 4: Run Setup Script

```bash
# Make the script executable
sudo chmod +x deployment/ec2/setup.sh

# Run the automated setup
sudo deployment/ec2/setup.sh
```

The script will:
- ✅ Update system packages
- ✅ Install Python 3.12, pip, nginx, git, ufw, certbot
- ✅ Create Python virtual environment
- ✅ Install all Python dependencies
- ✅ Create `.env` file from template
- ✅ Configure systemd service
- ✅ Configure NGINX reverse proxy
- ✅ Configure firewall (UFW)
- ✅ Start the application

### Step 5: Configure OpenAI API Key

```bash
# Edit the .env file
sudo nano ~/customer-support-agent/backend/.env

# Add your OpenAI API key:
OPENAI_API_KEY=sk-your-actual-key-here

# Save: Ctrl+O, Enter
# Exit: Ctrl+X
```

### Step 6: Restart Service

```bash
# Restart the support agent service
sudo systemctl restart support-agent

# Wait 10 seconds for initialization
sleep 10

# Check status (should show "active (running)")
sudo systemctl status support-agent

# View logs
sudo journalctl -u support-agent -n 50 --no-pager
```

### Step 7: Verify Deployment

```bash
# Get your EC2 public IP
curl -s http://169.254.169.254/latest/meta-data/public-ipv4

# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","vectordb":"connected","timestamp":"..."}
```

### Step 8: Access Application

Open in your browser:
- **Frontend**: `http://YOUR-EC2-IP/`
- **API Docs**: `http://YOUR-EC2-IP/docs`
- **Health Check**: `http://YOUR-EC2-IP/health`

## Configuration Options

### Environment Variables (`backend/.env`)

```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# LLM Configuration
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.0
EMBEDDING_MODEL=text-embedding-3-small

# ChromaDB Configuration
CHROMADB_PATH=./knowledge_base
CHROMADB_COLLECTION=knowledge_base

# RAG Configuration
RAG_TOP_K=3
RAG_SCORE_THRESHOLD=0.2

# Application Settings
MAX_QUERY_LENGTH=500
RATE_LIMIT_PER_MINUTE=10
SESSION_TIMEOUT_HOURS=24

# Logging
LOG_LEVEL=INFO
LOG_FILE=agent.log

# CORS (comma-separated)
ALLOWED_ORIGINS=http://localhost:8000,http://localhost:3000
```

## Service Management

### Check Service Status
```bash
sudo systemctl status support-agent
```

### View Logs
```bash
# View last 50 lines
sudo journalctl -u support-agent -n 50

# Follow logs in real-time
sudo journalctl -u support-agent -f

# View logs since specific time
sudo journalctl -u support-agent --since "10 minutes ago"
```

### Restart Service
```bash
sudo systemctl restart support-agent
```

### Stop Service
```bash
sudo systemctl stop support-agent
```

### Start Service
```bash
sudo systemctl start support-agent
```

### Disable Auto-start
```bash
sudo systemctl disable support-agent
```

### Enable Auto-start
```bash
sudo systemctl enable support-agent
```

## NGINX Configuration

### Check NGINX Status
```bash
sudo systemctl status nginx
```

### Test NGINX Configuration
```bash
sudo nginx -t
```

### Reload NGINX
```bash
sudo systemctl reload nginx
```

### View NGINX Logs
```bash
# Access logs
sudo tail -f /var/log/nginx/support-agent-access.log

# Error logs
sudo tail -f /var/log/nginx/support-agent-error.log
```

## SSL/HTTPS Setup (Optional)

### Using Let's Encrypt Certbot

```bash
# Install certbot (already installed by setup script)
sudo apt install certbot python3-certbot-nginx -y

# Edit NGINX config to add your domain
sudo nano /etc/nginx/sites-available/support-agent
# Change: server_name _; 
# To: server_name yourdomain.com www.yourdomain.com;

# Test configuration
sudo nginx -t

# Reload NGINX
sudo systemctl reload nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow the prompts
# Certbot will automatically configure NGINX for HTTPS
```

### Auto-renewal
Certbot automatically sets up auto-renewal. To test:
```bash
sudo certbot renew --dry-run
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs for errors
sudo journalctl -u support-agent -n 100 --no-pager

# Common issues:
# 1. Missing OpenAI API key
# 2. Port 8000 already in use
# 3. Missing dependencies
# 4. File permissions
```

### Check Port Availability
```bash
# Check if port 8000 is in use
sudo netstat -tlnp | grep 8000

# Kill process if needed
sudo kill -9 <PID>
```

### Fix File Permissions
```bash
sudo chown -R ubuntu:ubuntu ~/customer-support-agent
```

### Reinstall Dependencies
```bash
cd ~/customer-support-agent
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
```

### Reset Vector Database
```bash
cd ~/customer-support-agent/backend
rm -rf knowledge_base/
sudo systemctl restart support-agent
```

### Frontend 404 Error

```bash
# Check if frontend files exist
ls -la ~/customer-support-agent/frontend/

# Fix NGINX configuration
sudo nano /etc/nginx/sites-available/support-agent

# Ensure this section exists:
# location = / {
#     alias /home/ubuntu/customer-support-agent/frontend/index.html;
# }

sudo nginx -t
sudo systemctl reload nginx
```

## Updating the Application

```bash
# Stop service
sudo systemctl stop support-agent

# Pull latest changes
cd ~/customer-support-agent
git pull origin main

# Reinstall dependencies if requirements changed
source venv/bin/activate
pip install -r backend/requirements.txt

# Restart service
sudo systemctl start support-agent
```

## Monitoring

### Check System Resources
```bash
# CPU and Memory
htop

# Disk usage
df -h

# Process info
ps aux | grep uvicorn
```

### Application Metrics
```bash
# Request count from NGINX logs
sudo cat /var/log/nginx/support-agent-access.log | wc -l

# Recent errors
sudo tail -n 50 /var/log/nginx/support-agent-error.log
```

## Backup

### Backup Knowledge Base
```bash
# Backup ChromaDB
tar -czf chromadb-backup-$(date +%Y%m%d).tar.gz ~/customer-support-agent/backend/knowledge_base/

# Backup .env file
cp ~/customer-support-agent/backend/.env ~/env-backup-$(date +%Y%m%d).env
```

## Clean Deployment (Starting Fresh)

```bash
# Stop and remove everything
sudo systemctl stop support-agent
sudo systemctl disable support-agent
sudo rm -f /etc/systemd/system/support-agent.service
sudo rm -f /etc/nginx/sites-enabled/support-agent
sudo rm -f /etc/nginx/sites-available/support-agent
sudo systemctl daemon-reload
sudo rm -rf ~/customer-support-agent

# Now follow deployment steps from Step 3
```

## Security Best Practices

1. **Keep API Key Secure**: Never commit `.env` to git
2. **Limit SSH Access**: Restrict Security Group to your IP
3. **Regular Updates**: Keep system and packages updated
4. **Enable HTTPS**: Use SSL/TLS for production
5. **Firewall**: Use UFW to limit access
6. **Monitoring**: Set up CloudWatch or similar
7. **Backups**: Regular backups of data and configuration

## Cost Optimization

- Use **t2.medium** for development/testing
- Scale to **t3.medium** or **t3.large** for production
- Consider **Spot Instances** for cost savings
- Use **Elastic IP** to keep same IP address
- Monitor OpenAI API usage to control costs

## Support

For issues or questions:
- Check logs: `sudo journalctl -u support-agent -f`
- Open GitHub issue
- Review error messages in logs

---

**Last Updated**: October 2025
