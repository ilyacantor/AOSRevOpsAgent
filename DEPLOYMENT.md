# Deployment Guide

This Pipeline Health Monitor (RevOps DCL Agent) can be deployed to either **Replit** or **Render**. Both platforms are fully supported.

The application consists of:
- **Frontend**: React 19 + Vite 7 + TypeScript SPA
- **Backend**: FastAPI server with Data Connectivity Layer (DCL)

---

## Option 1: Deploy to Replit (Recommended for Quick Setup)

### Prerequisites
- Replit account
- Environment secrets already configured in this Repl
- Salesforce OAuth 2.0 credentials (instance URL, client ID, client secret, refresh token)
- Supabase project with `salesforce_health_scores` table
- MongoDB connection (optional)

### Steps

1. **Click the Publish button** in the Replit interface
2. **Configure deployment settings:**
   - Choose your deployment tier
   - Select a custom domain (optional)
   - Review deployment settings
3. **Publish!** 
   - Replit will automatically handle SSL, health checks, and environment variables
   - Your app will be live at `https://your-app.replit.app`

### Benefits
- ✅ One-click deployment
- ✅ Automatic HTTPS/SSL
- ✅ Environment secrets already configured
- ✅ Built-in health monitoring
- ✅ Easy rollback capabilities
- ✅ Auto-scaling included

### Environment Variables
All secrets are automatically carried over from your Repl secrets.

---

## Option 2: Deploy to Render

### Prerequisites
- Render account ([render.com](https://render.com))
- GitHub account and repository for this project

### Steps

#### 1. Push Code to GitHub

Push your code to a GitHub repository using standard version control commands.

#### 2. Create Render Service

1. **Log in to Render Dashboard** at [dashboard.render.com](https://dashboard.render.com)
2. **Click "New +"** → **"Web Service"**
3. **Connect your GitHub repository**
4. **Configure the service:**
   - **Name:** `revops-dcl-agent`
   - **Environment:** Python
   - **Build Command:** See requirements.txt
   - **Start Command:** `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`
   - **Plan:** Starter (or higher)

#### 3. Configure Environment Variables

In the Render dashboard, add these environment variables:

**Salesforce OAuth 2.0 (Required):**
| Variable Name | Description |
|---------------|-------------|
| `SALESFORCE_INSTANCE_URL` | Your Salesforce instance URL (e.g., `https://yourorg.my.salesforce.com`) |
| `SALESFORCE_CLIENT_ID` | OAuth app consumer key |
| `SALESFORCE_CLIENT_SECRET` | OAuth app consumer secret |
| `SALESFORCE_REFRESH_TOKEN` | OAuth refresh token |

**Supabase (Required):**
| Variable Name | Description |
|---------------|-------------|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_KEY` | Supabase API key |

**MongoDB (Optional):**
| Variable Name | Description |
|---------------|-------------|
| `MONGODB_URI` | MongoDB connection string |
| `MONGODB_DATABASE` | MongoDB database name |

**Other (Optional):**
| Variable Name | Description |
|---------------|-------------|
| `SLACK_WEBHOOK_URL` | Slack webhook for alerts |
| `SESSION_SECRET` | Random secret for sessions |
| `VITE_USE_PLATFORM_VIEWS` | `true` for LIVE mode, `false` for DEMO mode |

#### 4. Deploy

- Click **"Create Web Service"**
- Render will automatically build and deploy your app
- Your app will be live at `https://revops-dcl-agent.onrender.com`

### Using render.yaml (Alternative Method)

The `render.yaml` file in this repository contains the full deployment configuration:

1. Push code to GitHub
2. In Render Dashboard: Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will detect `render.yaml` automatically
5. Configure environment variables
6. Deploy!

---

## Verification

After deployment to either platform, verify your app is working:

1. **Visit the app URL** 
2. **Check the Dashboard** - should show pipeline health metrics
3. **Test the Connectivity page:**
   - Click on any connector card to view detailed information
   - Verify "Live Data" tab shows up to 20 actual records from your data sources
4. **Verify connectors are healthy:**
   - Salesforce: Healthy (green) - OAuth 2.0 authenticated
   - Supabase: Healthy (green) - Connected to PostgreSQL
   - MongoDB: Healthy (green) or Mock (yellow) depending on configuration

---

## Troubleshooting

### Common Issues

**"Salesforce not connected"**
- Verify OAuth 2.0 credentials are correct
- Ensure `SALESFORCE_INSTANCE_URL` matches your Salesforce org (no trailing slash)
- Check refresh token is still valid
- Verify OAuth app has required permissions (API access, refresh token)

**"Supabase not connected"**
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Ensure the `salesforce_health_scores` table exists in your Supabase database
- Check API key has proper permissions (read/write access to the table)

**"App won't start"**
- Check build logs for dependency errors
- Verify Python version is 3.11+ 
- Ensure all required packages are in `requirements.txt`

**"Port binding error"**
- For Render: The app automatically uses `$PORT` environment variable
- For Replit: Port 5000 is configured in `.streamlit/config.toml`

---

## Architecture Notes

This app uses a Data Connectivity Layer (DCL) architecture that:
- Abstracts data source connections (Salesforce, Supabase, MongoDB)
- Provides graceful degradation (mock data when services unavailable)
- Enables multi-source data joins through unified workflows

For full architecture details, see `replit.md`.

---

## Maintenance

### Updating the App

**On Replit:**
- Make changes in the Repl
- Click "Publish" again to redeploy

**On Render:**
- Push changes to GitHub
- Render will automatically redeploy on push to main branch

### Monitoring

**Replit:**
- Built-in monitoring in the deployment dashboard
- View logs directly in the Repl

**Render:**
- Check logs in the Render dashboard
- Set up alerts for service health
- Monitor via `/_stcore/health` endpoint

---

## Support

For issues specific to:
- **Replit deployment:** Check Replit docs or support
- **Render deployment:** Check Render docs or support  
- **App functionality:** Review `replit.md` for architecture details
