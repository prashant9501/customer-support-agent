#!/bin/bash
#
# Customer Support Agent - EC2 Deployment Setup Script
# This script automates the deployment on AWS EC2 Ubuntu 22.04 LTS
#
# Usage: sudo ./setup.sh
#

set -e  # Exit on error

echo "=========================================="
echo "Customer Support Agent - EC2 Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root (use sudo)"
    exit 1
fi

print_info "Starting deployment setup..."

# Update system
print_info "Updating system packages..."
apt update && apt upgrade -y
print_success "System updated"

# Install dependencies
print_info "Installing system dependencies..."
apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    nginx \
    git \
    curl \
    ufw \
    certbot \
    python3-certbot-nginx
print_success "Dependencies installed"

# Create application directory
APP_DIR="/home/ubuntu/customer-support-agent"
print_info "Setting up application directory: $APP_DIR"

if [ ! -d "$APP_DIR" ]; then
    print_info "Application directory not found. Please clone the repository first."
    print_info "Run: git clone <your-repo-url> $APP_DIR"
    exit 1
fi

cd "$APP_DIR"

# Create virtual environment
print_info "Creating Python virtual environment..."
python3.11 -m venv venv
print_success "Virtual environment created"

# Activate virtual environment and install dependencies
print_info "Installing Python packages..."
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
print_success "Python packages installed"

# Create .env file if it doesn't exist
ENV_FILE="$APP_DIR/backend/.env"
if [ ! -f "$ENV_FILE" ]; then
    print_info "Creating .env file..."
    cp backend/.env.example "$ENV_FILE"
    print_info "Please edit $ENV_FILE and add your OPENAI_API_KEY"
    print_info "Run: sudo nano $ENV_FILE"
else
    print_success ".env file already exists"
fi

# Initialize ChromaDB
print_info "Initializing ChromaDB vector store..."
cd backend
python -c "from app.database.vectordb import initialize_vectordb; initialize_vectordb()" 2>/dev/null || print_info "Note: ChromaDB will initialize on first run"
cd ..
print_success "Vector store initialized"

# Setup systemd service
print_info "Setting up systemd service..."
cp deployment/ec2/systemd/support-agent.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable support-agent
print_success "Systemd service configured"

# Start the service
print_info "Starting support agent service..."
systemctl start support-agent
sleep 5

# Check service status
if systemctl is-active --quiet support-agent; then
    print_success "Support agent service is running"
else
    print_error "Support agent service failed to start"
    print_info "Check logs with: sudo journalctl -u support-agent -f"
    exit 1
fi

# Setup NGINX
print_info "Setting up NGINX..."

# Copy NGINX configuration
cp deployment/ec2/nginx/sites-available/support-agent /etc/nginx/sites-available/
ln -sf /etc/nginx/sites-available/support-agent /etc/nginx/sites-enabled/

# Remove default NGINX site
rm -f /etc/nginx/sites-enabled/default

# Test NGINX configuration
nginx -t
if [ $? -eq 0 ]; then
    print_success "NGINX configuration is valid"
else
    print_error "NGINX configuration test failed"
    exit 1
fi

# Restart NGINX
systemctl restart nginx
print_success "NGINX configured and restarted"

# Configure firewall
print_info "Configuring UFW firewall..."
ufw --force enable
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
print_success "Firewall configured"

# Get public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

# Print completion message
echo ""
echo "=========================================="
print_success "Deployment Complete!"
echo "=========================================="
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Configure your API key:"
echo "   sudo nano $ENV_FILE"
echo "   Add: OPENAI_API_KEY=sk-your-key-here"
echo ""
echo "2. Restart the service:"
echo "   sudo systemctl restart support-agent"
echo ""
echo "3. Access your application:"
echo "   http://$PUBLIC_IP"
echo ""
echo "4. (Optional) Setup SSL with Let's Encrypt:"
echo "   sudo certbot --nginx -d your-domain.com"
echo ""
echo "📊 Useful Commands:"
echo "   - View logs: sudo journalctl -u support-agent -f"
echo "   - Check status: sudo systemctl status support-agent"
echo "   - Restart: sudo systemctl restart support-agent"
echo "   - Stop: sudo systemctl stop support-agent"
echo ""
echo "=========================================="
