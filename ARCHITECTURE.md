# System Architecture - Agora Portfolio Rebalancer

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface (React)                  │
│  Dashboard | Portfolio | Rebalancing | Settings | Analytics │
└──────────────────────────┬──────────────────────────────────┘
                           │ WebSocket/REST API
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              API Routes (CRUD Operations)            │  │
│  │  /portfolio | /rebalance | /strategies | /analytics  │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Background Jobs (APScheduler)                │  │
│  │  • Balance Refresh (30s)     • Price Updates (1m)    │  │
│  │  • Rebalancing Check (5m)    • Analytics (daily)     │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────┬──────────────────────────┬──────────────────┘
               │                          │
      ┌────────▼────────┐        ┌────────▼─────────┐
      │                 │        │                  │
      ▼                 ▼        ▼                  ▼
┌─────────────────┐ ┌──────────────────┐  ┌───────────────┐
│  Agent Layer    │ │ Blockchain Layer │  │ Data Layer    │
├─────────────────┤ ├──────────────────┤  ├───────────────┤
│ • Rebalancer    │ │ • Arc Client     │  │ • PostgreSQL  │
│ • Risk Calc     │ │ • DEX Handler    │  │ • Redis Cache │
│ • LLM Provider  │ │ • Protocols      │  │ • S3 Backup   │
│ • Strategies    │ │ • Transactions   │  │               │
└────────┬────────┘ └────────┬─────────┘  └───────────────┘
         │                   │
         └───────┬───────────┘
                 │
         ┌───────▼────────┐
         │  Arc Network   │
         ├────────────────┤
         │ • Sub-1s final.│
         │ • USDC fees    │
         │ • DEX Protocols│
         │ • Yield Protos │
         └────────────────┘
```

## Detailed Component Architecture

### 1. Frontend Layer (React)

**Purpose:** User-facing dashboard for portfolio management and strategy configuration

**Components:**
- **Dashboard Page** - Portfolio overview, real-time updates
- **Portfolio Page** - Detailed holdings, asset breakdown
- **Rebalancing Page** - Strategy setup, preview, execution
- **Analytics Page** - Historical performance, reports
- **Settings Page** - Risk parameters, notifications, wallet

**Technologies:**
- React 18+ for UI components
- TailwindCSS for styling
- ECharts for data visualization
- Web3.js for wallet connection
- Axios for API calls
- WebSocket client for real-time updates

**State Management:**
- Redux or Zustand for global state
- React Query for server-state caching
- Local storage for user preferences

---

### 2. Backend API Layer (FastAPI)

**Purpose:** RESTful API handling business logic orchestration

**Endpoints:**

```
POST   /api/v1/portfolio/refresh        → Fetch latest portfolio state
GET    /api/v1/portfolio                → Get portfolio data
GET    /api/v1/portfolio/risk           → Calculate risk metrics
GET    /api/v1/portfolio/history        → Transaction history

GET    /api/v1/strategies               → List available strategies
POST   /api/v1/strategies/create        → Create custom strategy
GET    /api/v1/strategies/{id}          → Get strategy details
PUT    /api/v1/strategies/{id}          → Update strategy

POST   /api/v1/rebalance/simulate       → Dry-run rebalancing
POST   /api/v1/rebalance/execute        → Execute rebalancing
GET    /api/v1/rebalance/status         → Get last rebalance status

GET    /api/v1/analytics/performance    → Performance metrics
GET    /api/v1/analytics/reports        → Generate reports

POST   /api/v1/auth/login               → User authentication
POST   /api/v1/auth/wallet              → Connect wallet
```

**Core Modules:**
- `routes/` - API endpoint definitions
- `services/` - Business logic layer
- `models/` - Pydantic data models
- `middleware/` - Auth, logging, error handling
- `config.py` - Configuration management

---

### 3. Agent Intelligence Layer (Python)

**Purpose:** AI-driven decision making for rebalancing

**Modules:**

```python
agent/
├── rebalancer.py          # Main orchestration
├── risk_calculator.py     # Risk metrics (VaR, Sharpe)
├── market_analyzer.py     # Market sentiment & data
├── strategies.py          # Rebalancing strategies
├── llm_provider.py        # LLM integration (Claude)
└── explanations.py        # Decision reasoning
```

**Rebalancing Flow:**
1. **Portfolio Assessment** → Get current allocation
2. **Risk Analysis** → Calculate Sharpe, VaR, Volatility
3. **Strategy Evaluation** → Check drift vs. target
4. **Market Analysis** → Check sentiment, volatility
5. **Decision Making** → LLM reasons about rebalancing
6. **Trade Generation** → Create swap transactions
7. **Execution** → Send to blockchain layer
8. **Reporting** → Log outcome & explanation

---

### 4. Blockchain Integration Layer (Web3)

**Purpose:** Secure interaction with Arc network and DeFi protocols

**Modules:**

```python
blockchain/
├── arc_client.py          # Arc network connection
├── dex_handler.py         # DEX swap execution
├── protocols/
│   ├── aave.py           # Aave lending
│   ├── uniswap.py        # Uniswap swaps
│   └── curve.py          # Curve liquidity
├── contracts/
│   ├── abis/             # Contract ABIs
│   └── addresses.py      # Deployed contracts
└── transaction.py        # Tx building & signing
```

**Key Features:**
- Web3.py for on-chain interaction
- Private key management (secure enclave)
- Nonce tracking for concurrent transactions
- Gas estimation & optimization for Arc (~$0.01 per tx)
- Sub-second finality monitoring
- Retry logic with exponential backoff

**Transaction Flow:**
1. Build swap transaction (0x API)
2. Estimate gas costs
3. Sign with private key
4. Broadcast to Arc network
5. Monitor for confirmation (sub-1s finality)
6. Parse receipt and update portfolio

---

### 5. Data Layer

**Purpose:** Persistent storage and caching

**PostgreSQL Schema:**
```sql
users
  - id (PK)
  - email, wallet_address
  - created_at, updated_at

portfolios
  - id (PK)
  - user_id (FK)
  - name, risk_profile
  - created_at, updated_at

holdings
  - id (PK)
  - portfolio_id (FK)
  - token_address, amount
  - value_usdc, weight (%)
  - updated_at

strategies
  - id (PK)
  - portfolio_id (FK)
  - name, description
  - target_allocations (JSON)
  - drift_threshold, rebalance_frequency

transactions
  - id (PK)
  - portfolio_id (FK)
  - tx_hash, from_token, to_token
  - amount_in, amount_out, fee_usdc
  - status, timestamp

rebalancing_history
  - id (PK)
  - portfolio_id (FK)
  - reason, trades_executed (count)
  - slippage (%), timestamp
```

**Redis Cache:**
- `price:{token_address}` → Latest price (TTL: 1m)
- `balance:{portfolio_id}` → Cached balances (TTL: 30s)
- `portfolio_risk:{portfolio_id}` → Risk metrics (TTL: 5m)
- `session:{user_id}` → Auth session (TTL: 24h)

---

### 6. Job Scheduler (APScheduler)

**Purpose:** Async tasks for monitoring and rebalancing checks

**Jobs:**

| Job | Frequency | Purpose |
|-----|-----------|----------|
| `refresh_balances` | 30s | Fetch latest holdings from Arc |
| `update_prices` | 1m | Get latest token prices |
| `check_rebalance_trigger` | 5m | Check if rebalancing needed |
| `compute_analytics` | Daily | Calculate daily metrics |
| `cleanup_cache` | Hourly | Clear expired cache entries |
| `sync_transactions` | 2m | Confirm pending transactions |

---

## Data Flow Diagrams

### Rebalancing Execution Flow

```
User Clicks "Execute"
    ↓
Backend: POST /api/v1/rebalance/execute
    ↓
Agent: Verify portfolio & strategy
    ↓
Agent: Calculate target allocation
    ↓
Agent: Generate swap trades
    ↓
DEX: Query swap quotes (1inch/0x)
    ↓
Blockchain: Build transactions
    ↓
Blockchain: Sign with private key
    ↓
Arc Network: Broadcast transaction
    ↓
Arc Network: Confirm (sub-1s finality)
    ↓
Backend: Update portfolio state
    ↓
Database: Log transaction
    ↓
Frontend: WebSocket update to dashboard
    ↓
User: See new allocation
```

---

## Deployment Architecture

### Local Development
```
Docker Compose:
  - backend:5000 (FastAPI)
  - frontend:3000 (React dev server)
  - postgres:5432
  - redis:6379
```

### Testnet Deployment
```
AWS/GCP/DigitalOcean:
  - Backend: Docker container (ECS/GKE/App Platform)
  - Frontend: S3 + CloudFront (static hosting)
  - Database: Managed PostgreSQL
  - Cache: Managed Redis
  - Monitoring: CloudWatch/Datadog
```

### Production Deployment
```
Multi-region setup:
  - Primary region: Backend + Database
  - Secondary region: Failover backend
  - CDN: Frontend distribution
  - Load balancer: Request distribution
  - Monitoring: 24/7 alerts
```

---

## Security Architecture

**Private Key Management:**
- Never stored in code or logs
- Encrypted in database (AES-256)
- Decrypted in-memory only during signing
- Alternative: Hardware wallet integration

**API Security:**
- JWT authentication for all endpoints
- Rate limiting (1000 req/min per user)
- CORS whitelist configuration
- HTTPS enforced
- Request signing for sensitive ops

**Blockchain Security:**
- Contract ABIs validated before interaction
- Transaction simulation before broadcast
- Slippage limits enforced
- Circuit breaker for unusual activity

---

## Scalability Considerations

**Horizontal Scaling:**
- Stateless backend (multiple replicas)
- Load balancer distribution
- Database connection pooling

**Caching Strategy:**
- Redis for hot data (prices, balances)
- CDN for static assets
- Database query optimization

**Performance Targets:**
- API latency: < 200ms (p95)
- Dashboard load: < 2s
- Portfolio calculation: < 500ms
- Concurrent users: 1000+

---

## Testing Strategy

### Unit Tests (Agent Layer)
```python
test_risk_calculator.py
test_rebalancer.py
test_strategy_logic.py
```

### Integration Tests (E2E)
```python
test_blockchain_integration.py
test_dex_swaps.py
test_api_endpoints.py
```

### Load Testing
```bash
locust -f tests/load_tests.py --headless -u 100 -r 10
```

---

**Ready to build! 🚀**
