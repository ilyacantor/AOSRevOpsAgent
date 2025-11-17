# Pipeline Health Monitor

## Overview

This project is a real-time revenue operations monitoring application designed to unify CRM (Salesforce), customer health (Supabase/PostgreSQL), and user engagement (MongoDB) data. It provides workflow-based analytics for CRM integrity validation (BANT framework) and pipeline health monitoring, including Slack-based alerting. The system utilizes a Data Connectivity Layer (DCL) to abstract data access, enabling flexible integration and separation of concerns between business logic and data sources. The application aims to provide a comprehensive, unified view of pipeline health and CRM data integrity to drive informed business decisions.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Architecture Pattern

The core architecture is built around a **Data Connectivity Layer (DCL)**. This DCL acts as a universal router and abstraction layer, using a Registry Pattern to manage various data connectors (Salesforce, Supabase, MongoDB). Connectors register with the DCL, providing a standardized `query(params)` interface and metadata. Workflows then query the DCL, which routes requests to the appropriate connector, translating generic parameters into source-specific query languages. This design ensures clean separation between data access and business logic, allows for graceful degradation with mock data fallbacks, and simplifies the integration of new data sources.

### Frontend Architecture

The frontend is a modern **React Single Page Application (SPA)** built with React 19, Vite 7, and TypeScript. It features three main pages: Dashboard (Pipeline Health), Operations (CRM Integrity), and Connectivity (DCL Demo). The UI incorporates a custom component library, state management via React hooks, data fetching with a `useFetch` hook and Axios, and responsive design with Tailwind CSS v4. Charts are rendered using the Recharts library, and client-side routing is handled by React Router v7. The application adheres to the autonomOS Platform Theme, utilizing a dark aesthetic with teal accents for a professional, futuristic look.

**Key Features:**
- **Drill-to-Details Connectivity**: Clickable connector cards on the Connectivity page open detailed modals showing connection health, configuration, capabilities, and live data (up to 20 records) pulled directly from the actual data source instances. Accessible via `/api/dcl/connectors/{name}` endpoint. Modal features three tabs:
  - **Overview**: Connection status, sanitized configuration details, capabilities, and description
  - **Health**: Real-time health check results with error diagnostics
  - **Live Data**: Actual records from the connector's data source (up to 20 records max)
  - All tabs include comprehensive error handling, loading states, and click-outside-to-close functionality

### Backend Architecture

The backend implements **Connector and Workflow Patterns**. Each data source has a dedicated connector class that manages authentication, connection, and provides a standardized query interface with mock data fallbacks. Workflows encapsulate business logic, orchestrating multi-source data queries and joins through the DCL. Key workflows include `CRMIntegrityWorkflow` (BANT validation) and `PipelineHealthWorkflow` (multi-source pipeline analysis).

### Data Storage Solutions

The application integrates with multiple data sources:
- **Salesforce (CRM)**: Primary source for opportunity and account data via SOQL, accessed using `simple-salesforce` with OAuth 2.0 authentication.
- **Supabase/PostgreSQL**: Stores customer health scores in a `salesforce_health_scores` table, accessed via `supabase-py`.
- **MongoDB**: User engagement analytics and usage data, accessed via `pymongo`.

### Authentication & Authorization

Credentials for external services (Salesforce, Supabase, Slack) are managed via Replit Secrets. The application does not implement user authentication as it's a demo.

### Design Patterns

Key design patterns include:
- **Registry Pattern**: For the DCL core, managing connector mappings.
- **Factory Pattern**: For creating connector instances.
- **Strategy Pattern**: For schema mapping between data sources.
- **Graceful Degradation**: All connectors include mock data fallbacks to maintain application functionality even if external services are unavailable.

## External Dependencies

### Third-party Services

-   **Salesforce API**: Integrated via `simple-salesforce` for CRM data.
-   **Supabase PostgreSQL**: Integrated via `supabase-py` for customer health scores.
-   **Slack Webhooks**: Used for sending human-in-the-loop escalation alerts.

### Key Python Libraries

-   `pandas`: Data manipulation.
-   `simple-salesforce`: Salesforce API client.
-   `supabase`: Supabase client library.
-   `requests`: HTTP client.

### Configuration Requirements

**Replit Secrets (Backend):**
-   **Salesforce OAuth 2.0**: `SALESFORCE_INSTANCE_URL`, `SALESFORCE_CLIENT_ID`, `SALESFORCE_CLIENT_SECRET`, `SALESFORCE_REFRESH_TOKEN`
-   **Supabase**: `SUPABASE_URL`, `SUPABASE_KEY`
-   **MongoDB**: `MONGODB_URI`, `MONGODB_DATABASE`
-   **Slack** (optional): `SLACK_WEBHOOK_URL`
-   **Platform Integration** (optional): `AOS_BASE_URL`, `AOS_TENANT_ID`, `AOS_AGENT_ID`, `AOS_JWT`

**Replit Secrets (Frontend):**
-   `VITE_USE_PLATFORM_VIEWS`: 'true' for LIVE mode (platform integration), 'false' for DEMO mode.

## Deployment

The application uses a React + FastAPI architecture:

**Development (Replit):**
- Frontend: Vite dev server on port 5000 (workflow: "Frontend")
- Backend: FastAPI on port 8000 (workflow: "Backend API")
- Runs as two separate processes with hot module replacement

**Production (Deployment):**
- Frontend is built into static files: `cd frontend && npm run build`
- FastAPI serves both API (`/api/*`) and frontend (`/*`) on a single port
- Static files are served from `frontend/dist` directory
- Single unified deployment process

See `DEPLOYMENT.md` for detailed deployment instructions for Replit and Render platforms.