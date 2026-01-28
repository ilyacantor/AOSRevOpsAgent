# Pipeline Health Monitor

## What This Application Does

This is a **Revenue Operations (RevOps) monitoring dashboard** that helps sales and operations teams track their sales pipeline health. It brings together data from three sources:

- **Salesforce** - Your CRM deals and opportunities
- **Supabase** - Customer health scores and engagement metrics
- **MongoDB** - User activity and usage analytics

The application displays key performance indicators, identifies at-risk deals, validates CRM data quality, and can alert your team via Slack when issues arise.

---

## How to Use the Application

### Dashboard (Pipeline Health)

**What you can do here:**
- View 8 key performance metrics at a glance (total pipeline value, win rate, average deal size, etc.)
- See pipeline breakdown by stage with visual charts
- Identify high-risk deals that need attention (risk score > 70)
- Send Slack alerts to notify your team about at-risk opportunities
- Filter by stalled deals and minimum risk score threshold
- Access the **Quick Start Guide** (collapsible FAQ) for help

**Key Metrics Explained:**
- **Health Score** (0-100): Higher is better - measures overall deal quality
- **Risk Score** (0-100): Lower is better - measures likelihood of deal problems
- **Pipeline Velocity**: How fast deals move through your pipeline
- **Stalled Deals**: Opportunities with no activity for 14+ days

### Operations (CRM Integrity)

**What you can do here:**
- Validate CRM data quality using the BANT framework
- Check if opportunities have complete information (Budget, Authority, Need, Timeline)
- Review data completeness scores for your pipeline
- Identify records with missing or incomplete fields
- Filter validation results by risk level (Low, Medium, High)
- Navigate through paginated results

**BANT Framework:**
- **Budget**: Does the opportunity have a defined budget?
- **Authority**: Is the decision-maker identified?
- **Need**: Is the customer's need clearly documented?
- **Timeline**: Is there a target close date?

### Connectivity (Data Sources)

**What you can do here:**
- See real-time status of all data source connections (healthy, degraded, or offline)
- View whether connectors are using live credentials or mock fallback data
- Click any connector card to view detailed information:
  - **Overview tab**: Configuration and capabilities
  - **Health tab**: Connection test results and error diagnostics
  - **Live Data tab**: Sample records from the data source (up to 20 records when credentials configured)

---

## LIVE Mode vs DEMO Mode

The application operates in two modes:

| Mode | How It Works | When to Use |
|------|--------------|-------------|
| **LIVE** | Displays real data from your connected services | Production use with configured credentials |
| **DEMO** | Displays realistic mock data | Demos, testing, or when credentials unavailable |

**How modes are determined:**
- **Dashboard & Operations**: Controlled by `VITE_USE_PLATFORM_VIEWS` environment variable (set to 'true' for platform data)
- **Connectivity page**: Each connector's status reflects whether valid credentials are configured; without credentials, connectors use mock data fallback

---

## User Preferences

- Preferred communication style: Simple, everyday language
- Dark theme with teal accents (autonomOS Platform Theme)

---

## Project Structure

```
/
├── api.py                 # FastAPI backend server
├── dcl_core.py           # Data Connectivity Layer core
├── connectors/           # Data source connectors
│   ├── salesforce_connector.py
│   ├── supabase_connector.py
│   └── mongodb_connector.py
├── workflows/            # Business logic workflows
├── frontend/             # React SPA
│   ├── src/
│   │   ├── pages/        # Dashboard, Operations, Connectivity
│   │   ├── components/   # Reusable UI components
│   │   └── lib/          # Data fetching utilities
│   └── dist/             # Production build output
├── roadmap_revops.md     # Feature roadmap and limitations
└── DEPLOYMENT.md         # Deployment instructions
```

---

## Technical Architecture

### Data Flow

1. **Dashboard & Operations pages** → Platform views (AosClient) or mock data services
2. **Connectivity page** → Backend DCL API (`/api/dcl/connectors`)

Note: The backend DCL connectors are fully implemented but currently only used by the Connectivity page for connector testing and monitoring.

### Backend (FastAPI + Python)

- **Data Connectivity Layer (DCL)**: Abstraction layer managing all data source connections
- **Connectors**: Salesforce (OAuth 2.0), Supabase, MongoDB - each with mock fallbacks
- **Health Checks**: Cached status with 60-second TTL
- **API Endpoints**:
  - `GET /api/dcl/connectors` - List all connectors with status
  - `GET /api/dcl/connectors/{name}` - Connector details with live data
  - `GET /api/health` - Application health check

### Frontend (React 19 + TypeScript)

- **Vite 7** for development and builds
- **React Router v7** for navigation
- **Tailwind CSS v4** for styling
- **Recharts** for data visualization
- **Axios** for API calls

---

## Configuration

### Required Secrets (Replit Secrets)

For **LIVE mode** with real data, configure these secrets:

**Salesforce (choose one authentication method):**

*Option A - OAuth 2.0 (Preferred):*
- `SALESFORCE_INSTANCE_URL`
- `SALESFORCE_CLIENT_ID`
- `SALESFORCE_CLIENT_SECRET`
- `SALESFORCE_REFRESH_TOKEN`

*Option B - Username/Password (Legacy):*
- `SALESFORCE_DOMAIN` (e.g., 'test' for sandbox)
- `SALESFORCE_USERNAME`
- `SALESFORCE_PASSWORD`
- `SALESFORCE_SECURITY_TOKEN`

**Supabase:**
- `SUPABASE_URL`
- `SUPABASE_KEY`

**MongoDB:**
- `MONGODB_URI`
- `MONGODB_DATABASE`

**Optional:**
- `SLACK_WEBHOOK_URL` - For Slack alerts
- `VITE_USE_PLATFORM_VIEWS` - Set to 'true' for LIVE mode on Dashboard/Operations

### Without Secrets

The application works without any secrets configured:
- **Dashboard & Operations**: Display mock data when `VITE_USE_PLATFORM_VIEWS` is not set to 'true'
- **Connectivity page**: Backend connectors fall back to realistic mock data when credentials are missing

---

## Running the Application

### Development

Two workflows run simultaneously:
- **Frontend**: `cd frontend && npm run dev` (port 5000)
- **Backend API**: `uvicorn api:app --host 0.0.0.0 --port 8000 --reload`

### Production Deployment

1. Build frontend: `cd frontend && npm run build`
2. Run unified server: `uvicorn api:app --host 0.0.0.0 --port 5000`

FastAPI serves both the API (`/api/*`) and the React frontend (`/*`) from a single process.

---

## Current Limitations

- **No user authentication** - This is a demo/internal tool
- **Dashboard/Operations** use platform views or mock data, not backend DCL
- **Live connector data** requires configured credentials and environment testing
- **No historical data tracking** - Shows current snapshot only
- **No data export** - View-only interface

See `roadmap_revops.md` for detailed limitations and future development plans.

---

## Useful Commands

```bash
# Start frontend dev server
cd frontend && npm run dev

# Start backend server
uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# Build for production
cd frontend && npm run build

# Test backend health
curl http://localhost:8000/api/health

# List connectors
curl http://localhost:8000/api/dcl/connectors
```

---

## Related Documentation

- `DEPLOYMENT.md` - Step-by-step deployment guide
- `roadmap_revops.md` - Features, limitations, and future roadmap
- `SUPABASE_SETUP.md` - Database schema setup
- `frontend/README.md` - Frontend-specific documentation
