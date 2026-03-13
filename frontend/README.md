# Pipeline Health Monitor - Frontend

A modern React SPA for real-time revenue operations monitoring, built with React 19, Vite 7, and TypeScript.

## Overview

The frontend provides three main pages:
- **Dashboard (Pipeline Health)**: Real-time pipeline metrics and opportunity tracking
- **Operations (CRM Integrity)**: BANT validation and CRM data quality checks
- **Connectivity (DCL Demo)**: Data Connectivity Layer with drill-to-details connector information

## Tech Stack

- **React 19**: Modern React with hooks and latest features
- **TypeScript**: Full type safety across the application
- **Vite 7**: Fast build tool with HMR
- **Tailwind CSS v4**: Utility-first CSS with custom dark theme
- **React Router v7**: Client-side routing
- **Recharts**: Data visualization and charts
- **Axios**: HTTP client for API requests
- **Lucide React**: Icon library

## Key Features

### Drill-to-Details Connectivity
Click any connector card on the Connectivity page to view:
- **Overview Tab**: Connection status, configuration, capabilities
- **Health Tab**: Real-time health checks with diagnostics
- **Live Data Tab**: Up to 20 actual records from the data source

### Responsive Design
- Mobile-first approach
- Dark theme with teal accents (autonomOS Platform Theme)
- Smooth transitions and hover effects
- Accessible UI components

### State Management
- React hooks (useState, useEffect, useMemo)
- Custom `useFetch` hook for data fetching
- Component-level state management

## Development

### Prerequisites
- Node.js (latest LTS)
- npm or yarn

### Running Locally
```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5000`

### Building for Production
```bash
npm run build
```

### Running Tests
```bash
npm test
```

## Environment Variables

Create a `.env` file in the frontend directory:

```bash
# LIVE mode: Use platform views with real backend
# DEMO mode: Use mock data
VITE_USE_PLATFORM_VIEWS=false
```

## Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   │   ├── Card.tsx
│   │   ├── ConnectorDetailModal.tsx
│   │   └── ...
│   ├── pages/         # Page components
│   │   ├── Dashboard.tsx
│   │   ├── Operations.tsx
│   │   └── Connectivity.tsx
│   ├── hooks/         # Custom React hooks
│   │   └── useFetch.ts
│   ├── lib/           # Utilities and helpers
│   │   ├── aosClient.ts
│   │   └── dataFetchers.ts
│   └── App.tsx        # Main app component
├── public/            # Static assets
└── index.html         # Entry point
```

## API Integration

The frontend connects to the FastAPI backend at `/api/*`:
- `/api/dcl/connectors` - List all connectors
- `/api/dcl/connectors/{name}` - Get detailed connector info
- `/api/workflows/pipeline-health` - Pipeline health metrics
- `/api/workflows/crm-integrity` - CRM validation results

## Styling

Uses Tailwind CSS v4 with custom configuration:
- Dark background (`#0a0a0a`)
- Teal accent color (`#00d4aa`)
- Custom card and border styles
- Responsive breakpoints

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

Proprietary
