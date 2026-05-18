# Setup & Deployment Guide - Agora Portfolio Rebalancer

## Prerequisites

- **Python**: 3.11+
- **Node.js**: 18+
- **Docker**: 20.10+
- **Git**: 2.30+
- **Arc Account**: Testnet setup at https://arc.network
- **Wallet**: MetaMask or WalletConnect enabled

---

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/coisasgreen/agora-portfolio-rebalancer.git
cd agora-portfolio-rebalancer
```

### 2. Backend Setup

#### Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Environment Configuration

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
# Arc Network
ARC_RPC_URL=https://testnet.arc.network
ARC_CHAIN_ID=2025
ARC_EXPLORER=https://explorer.arc.network

# Circle Integration
CIRCLE_API_KEY=<your-circle-api-key>
CIRCLE_USDC_ADDRESS=0x...

# LLM Provider
CLAUDE_API_KEY=<your-claude-api-key>

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/agora
REDIS_URL=redis://localhost:6379

# Wallet
PRIVATE_KEY=<your-private-key>  # ⚠️ Never commit to repo
PUBLIC_ADDRESS=0x...

# Server
FLASK_ENV=development
DEBUG=True
SECRET_KEY=<generate-random-string>

# API Keys
_1INCH_API_KEY=<optional>
CHAINLINK_RPC=https://...
```

#### Initialize Database

```bash
# Create database
createpdb agora

# Run migrations
alembic upgrade head

# Seed test data (optional)
python scripts/seed_testnet_data.py
```

#### Start Backend Server

```bash
cd backend
uvicorn app:app --reload --port 5000
```

API available at: http://localhost:5000
API docs at: http://localhost:5000/docs

---

### 3. Frontend Setup

#### Install Dependencies

```bash
cd frontend
npm install
```

#### Environment Configuration

```bash
cp .env.example .env.local
```

Edit `.env.local`:

```env
REACT_APP_API_URL=http://localhost:5000/api/v1
REACT_APP_WS_URL=ws://localhost:5000/ws
REACT_APP_CHAIN_ID=2025
REACT_APP_ARC_RPC=https://testnet.arc.network
```

#### Start Development Server

```bash
npm start
```

UI available at: http://localhost:3000

---

## Docker Compose Setup (Recommended)

### Start All Services

```bash
docker-compose up --build
```

This starts:
- **Backend**: http://localhost:5000
- **Frontend**: http://localhost:3000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### Stop Services

```bash
docker-compose down
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

---

## Arc Testnet Configuration

### 1. Connect Wallet to Arc Testnet

**MetaMask Setup:**
1. Open MetaMask
2. Click network dropdown → "Add Network"
3. Enter:
   - **Network Name**: Arc Testnet
   - **RPC URL**: https://testnet.arc.network
   - **Chain ID**: 2025
   - **Currency**: USDC
   - **Explorer**: https://explorer.arc.network
4. Click "Save"

### 2. Get Testnet USDC

```bash
# Using Circle testnet faucet
curl -X POST https://testnet-api.circle.com/v1/faucet \
  -H "Content-Type: application/json" \
  -d '{"address": "0x...", "amount": "1000"}'
```

Or visit: https://testnet.circle.com/faucet

### 3. Verify Connection

```bash
python scripts/verify_arc_connection.py
```

Expected output:
```
✓ Connected to Arc testnet
✓ Chain ID: 2025
✓ Balance: 1000 USDC
✓ Gas price: 0.01 USDC per tx
```

---

## Testing

### Run Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_risk_calculator.py

# With coverage
pytest --cov=agent --cov=blockchain
```

### Testnet Integration Tests

```bash
# Run Arc testnet tests
pytest tests/integration/test_arc_integration.py

# Run DEX swap tests
pytest tests/integration/test_dex_swaps.py
```

### Load Testing

```bash
# Install locust
pip install locust

# Run load tests
locust -f tests/load_tests.py --headless -u 100 -r 10 -t 5m
```

---

## Deployment to Production

### 1. Build Docker Images

```bash
# Build backend image
docker build -t agora-backend:latest -f docker/backend.Dockerfile .

# Build frontend image
docker build -t agora-frontend:latest -f docker/frontend.Dockerfile .

# Push to registry (AWS ECR / Docker Hub)
docker push agora-backend:latest
docker push agora-frontend:latest
```

### 2. Deploy to AWS ECS

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name agora-prod

# Register task definition
aws ecs register-task-definition --cli-input-json file://docker/ecs-task-def.json

# Create service
aws ecs create-service --cluster agora-prod \
  --service-name agora-backend \
  --task-definition agora-backend:1 \
  --desired-count 3 \
  --launch-type FARGATE
```

### 3. Setup Database

```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier agora-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --allocated-storage 20

# Run migrations
alembic upgrade head
```

### 4. Configure Environment

```bash
# Create Secrets Manager entry
aws secretsmanager create-secret \
  --name agora/production \
  --secret-string file://secrets.json
```

### 5. Deploy Frontend

```bash
# Build static files
cd frontend
npm run build

# Upload to S3
aws s3 sync build/ s3://agora-frontend/

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id E123EXAMPLE \
  --paths "/*"
```

### 6. Setup Monitoring

```bash
# Create CloudWatch dashboard
aws cloudwatch put-dashboard \
  --dashboard-name agora-monitoring \
  --dashboard-body file://docker/dashboard.json

# Create alarms
aws cloudwatch put-metric-alarm \
  --alarm-name agora-high-error-rate \
  --alarm-description "Alert on high error rate" \
  --metric-name ErrorCount \
  --threshold 100 \
  --comparison-operator GreaterThanThreshold
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>
```

### Database Connection Error

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql

# Check connection
psql -U postgres -d agora -c "SELECT 1"
```

### Arc Network Connection Issues

```bash
# Test RPC endpoint
curl https://testnet.arc.network -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_chainId","id":1}'

# Expected response: {"result":"0x7e5"}  # 2025 in hex
```

### Low Testnet USDC Balance

```bash
# Request more USDC from faucet
PUBLIC_ADDRESS=0x...

curl -X POST https://testnet-api.circle.com/v1/faucet \
  -H "Content-Type: application/json" \
  -d "{\"address\": \"$PUBLIC_ADDRESS\", \"amount\": \"1000\"}"
```

### API Returns 401 Unauthorized

```bash
# Check JWT token
echo $JWT_TOKEN

# Regenerate token
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

---

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Changes

```bash
# Edit files
# Run tests
pytest
# Format code
black .
pylint agent/
```

### 3. Commit & Push

```bash
git add .
git commit -m "feat: add new rebalancing strategy"
git push origin feature/my-feature
```

### 4. Create Pull Request

Go to GitHub and create PR with:
- Clear title
- Description of changes
- Link to issue (if applicable)
- Screenshots (if UI changes)

### 5. CI/CD Pipeline

GitHub Actions automatically:
- Runs tests
- Checks code style
- Builds Docker images
- Deploys to staging

---

## Production Checklist

Before going live:

- [ ] All tests passing (unit + integration)
- [ ] Code coverage > 80%
- [ ] Security audit completed
- [ ] Database backups configured
- [ ] Monitoring & alerting setup
- [ ] Disaster recovery plan ready
- [ ] Documentation up-to-date
- [ ] Performance benchmarks met
- [ ] Load testing completed
- [ ] User acceptance testing done
- [ ] Stakeholder approval received
- [ ] Communication plan ready

---

## Support & Resources

- **Discord**: https://discord.gg/TGnyfKh23V
- **Arc Docs**: https://docs.arc.network
- **Circle Docs**: https://developers.circle.com
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **React Docs**: https://react.dev

---

**You're ready to build! 🚀**
