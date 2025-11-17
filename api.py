"""
FastAPI Backend for Pipeline Health Monitor
Exposes REST endpoints for workflows and DCL connectors

ARCHITECTURE NOTE:
- Frontend data fetching now uses: Platform Views → Mock (no backend API)
- Workflow endpoints (/api/workflows/*) are NO LONGER USED by the frontend
- Frontend uses dataFetchers.ts which calls Platform Views directly via AosClient
- Workflow endpoints kept for backward compatibility and direct API access/testing
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime
import os
from pathlib import Path

from dcl_core import DCL
from connectors.salesforce_connector import create_salesforce_connector
from connectors.supabase_connector import create_supabase_connector
from connectors.mongo_connector import create_mongo_connector
from connectors.exceptions import ConnectorConfigurationError
from workflows.crm_integrity import CRMIntegrityWorkflow
from workflows.pipeline_health import PipelineHealthWorkflow

app = FastAPI(title="Pipeline Health Monitor API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global DCL instance
dcl = None

def get_dcl():
    """Get or initialize DCL instance with graceful error handling"""
    global dcl
    if dcl is None:
        dcl = DCL()
        
        # Track connector initialization results
        connector_results = {
            'healthy': [],
            'mock': [],
            'failed': []
        }
        
        # Register Salesforce with mock fallback
        try:
            sf_connector, sf_meta, sf_instance = create_salesforce_connector(allow_mock=True)
            dcl.register_connector('salesforce', sf_connector, sf_meta, sf_instance)
            status = sf_meta.get('status', 'unknown')
            if status == 'healthy':
                connector_results['healthy'].append('salesforce')
            elif status == 'mock':
                connector_results['mock'].append('salesforce')
                print(f"⚠️  Salesforce: {sf_meta.get('error', 'Using mock data')}")
        except ConnectorConfigurationError as e:
            print(f"❌ Salesforce initialization failed: {e}")
            connector_results['failed'].append('salesforce')
            dcl.register_connector('salesforce', lambda *args, **kwargs: [], {
                "type": "Salesforce CRM",
                "status": "failed",
                "description": "Salesforce Sandbox - Opportunities, Accounts, Leads",
                "error": str(e)
            })
        except Exception as e:
            print(f"❌ Salesforce unexpected error: {e}")
            connector_results['failed'].append('salesforce')
        
        # Register Supabase with mock fallback
        try:
            sb_connector, sb_meta, sb_instance = create_supabase_connector(allow_mock=True)
            dcl.register_connector('supabase', sb_connector, sb_meta, sb_instance)
            status = sb_meta.get('status', 'unknown')
            if status == 'healthy':
                connector_results['healthy'].append('supabase')
            elif status == 'mock':
                connector_results['mock'].append('supabase')
                print(f"⚠️  Supabase: {sb_meta.get('error', 'Using mock data')}")
        except ConnectorConfigurationError as e:
            print(f"❌ Supabase initialization failed: {e}")
            connector_results['failed'].append('supabase')
            dcl.register_connector('supabase', lambda *args, **kwargs: [], {
                "type": "Supabase PostgreSQL",
                "status": "failed",
                "description": "Customer health scores and engagement metrics",
                "error": str(e)
            })
        except Exception as e:
            print(f"❌ Supabase unexpected error: {e}")
            connector_results['failed'].append('supabase')
        
        # Register MongoDB with mock fallback
        try:
            mongo_connector, mongo_meta, mongo_instance = create_mongo_connector(allow_mock=True)
            dcl.register_connector('mongodb', mongo_connector, mongo_meta, mongo_instance)
            status = mongo_meta.get('status', 'unknown')
            if status == 'healthy':
                connector_results['healthy'].append('mongodb')
            elif status == 'mock':
                connector_results['mock'].append('mongodb')
                print(f"⚠️  MongoDB: {mongo_meta.get('error', 'Using mock data')}")
        except ConnectorConfigurationError as e:
            print(f"❌ MongoDB initialization failed: {e}")
            connector_results['failed'].append('mongodb')
            dcl.register_connector('mongodb', lambda *args, **kwargs: {}, {
                "type": "MongoDB",
                "status": "failed",
                "description": "Usage and engagement data",
                "error": str(e)
            })
        except Exception as e:
            print(f"❌ MongoDB unexpected error: {e}")
            connector_results['failed'].append('mongodb')
        
        # Log summary
        if connector_results['healthy']:
            print(f"✅ Healthy connectors: {', '.join(connector_results['healthy'])}")
        if connector_results['mock']:
            print(f"⚠️  Mock connectors: {', '.join(connector_results['mock'])}")
        if connector_results['failed']:
            print(f"❌ Failed connectors: {', '.join(connector_results['failed'])}")
        
        if not connector_results['failed'] and not connector_results['mock']:
            print("✅ All connectors initialized successfully with real credentials")
        elif connector_results['healthy']:
            print("⚠️  DCL initialized with degraded state (some connectors using mock data or failed)")
        else:
            print("⚠️  DCL initialized in demo mode (all connectors using mock data)")
    
    return dcl

# Response models
class MetricResponse(BaseModel):
    label: str
    value: str
    change: Optional[str] = None
    trend: Optional[str] = None

class ConnectorInfo(BaseModel):
    name: str
    type: str
    status: str
    description: str
    error: Optional[str] = None
    health: Optional[Dict[str, Any]] = None
    last_checked: Optional[str] = None

class ConnectorDetails(BaseModel):
    name: str
    type: str
    status: str
    description: str
    error: Optional[str] = None
    health: Optional[Dict[str, Any]] = None
    last_checked: Optional[str] = None
    config_info: Dict[str, Any]
    capabilities: List[str]
    sample_data: Optional[List[Dict[str, Any]]] = None

class OpportunityRecord(BaseModel):
    id: str
    name: str
    account_name: str
    stage: str
    amount: float
    health_score: int
    risk_score: int
    is_stalled: bool

class ValidationRecord(BaseModel):
    opportunity_id: str
    opportunity_name: str
    account_name: str
    stage: str
    amount: float
    is_valid: bool
    missing_fields: List[str]
    validation_issues: str
    risk_level: str

class PlatformConfigResponse(BaseModel):
    baseUrl: str
    tenantId: str
    agentId: str
    jwt: Optional[str] = None

class PaginationMetadata(BaseModel):
    page: int
    page_size: int
    total: int
    has_more: bool
    next_cursor: Optional[str] = None

# Removed startup event - using lazy initialization instead

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Pipeline Health Monitor API"}

@app.get("/api/platform/config", response_model=PlatformConfigResponse)
async def get_platform_config():
    """
    Get platform configuration for AosClient
    Returns platform credentials from backend environment variables
    """
    base_url = os.getenv('AOS_BASE_URL', '')
    tenant_id = os.getenv('AOS_TENANT_ID', '')
    agent_id = os.getenv('AOS_AGENT_ID', '')
    jwt = os.getenv('AOS_JWT', '')
    
    if not all([base_url, tenant_id, agent_id]):
        raise HTTPException(
            status_code=503,
            detail="Platform configuration not available - credentials not configured in backend"
        )
    
    return PlatformConfigResponse(
        baseUrl=base_url,
        tenantId=tenant_id,
        agentId=agent_id,
        jwt=jwt if jwt else None
    )

@app.get("/api/dcl/connectors", response_model=List[ConnectorInfo])
async def get_connectors(force_check: bool = Query(default=False, description="Force fresh health check, bypass cache")):
    """
    Get list of registered DCL connectors with health status.
    Health checks are cached for 60s per connector to avoid blocking I/O.
    Use ?force_check=true to bypass cache.
    """
    dcl_instance = get_dcl()
    connectors = []
    
    for name, meta in dcl_instance.list_connectors().items():
        # Get connector status from metadata
        status = meta.get('status', 'Unknown')
        error = meta.get('error', None)
        
        # Get cached or fresh health check
        health = None
        last_checked = None
        connector_instance = dcl_instance.connector_instances.get(name)
        
        if connector_instance and hasattr(connector_instance, 'check_health'):
            # Check if cache is fresh - avoid expensive check if possible
            if hasattr(connector_instance, 'is_health_cache_fresh') and not force_check:
                if connector_instance.is_health_cache_fresh():
                    # Use cached health without calling check_health()
                    health = connector_instance.get_cached_health()
                    last_checked = datetime.fromtimestamp(connector_instance._health_cache_time).isoformat()
                else:
                    # Cache is stale or missing - perform check
                    health = connector_instance.check_health(force=force_check)
                    last_checked = datetime.fromtimestamp(connector_instance._health_cache_time).isoformat()
            else:
                # Forced check or no cache support - call check_health
                health = connector_instance.check_health(force=force_check)
                if hasattr(connector_instance, '_health_cache_time'):
                    last_checked = datetime.fromtimestamp(connector_instance._health_cache_time).isoformat()
        
        connectors.append(ConnectorInfo(
            name=name,
            type=meta.get('type', 'Unknown'),
            status=status,
            description=meta.get('description', 'No description'),
            error=error,
            health=health,
            last_checked=last_checked
        ))
    
    return connectors

@app.get("/api/dcl/connectors/{connector_name}", response_model=ConnectorDetails)
async def get_connector_details(
    connector_name: str,
    force_check: bool = Query(default=False, description="Force fresh health check"),
    include_sample: bool = Query(default=True, description="Include sample data")
):
    """
    Get detailed information about a specific connector including configuration,
    health status, and optional sample data.
    """
    dcl_instance = get_dcl()
    
    # Check if connector exists
    connectors = dcl_instance.list_connectors()
    if connector_name not in connectors:
        raise HTTPException(status_code=404, detail=f"Connector '{connector_name}' not found")
    
    meta = connectors[connector_name]
    connector_instance = dcl_instance.connector_instances.get(connector_name)
    
    # Get health check
    health = None
    last_checked = None
    if connector_instance and hasattr(connector_instance, 'check_health'):
        if hasattr(connector_instance, 'is_health_cache_fresh') and not force_check:
            if connector_instance.is_health_cache_fresh():
                health = connector_instance.get_cached_health()
                last_checked = datetime.fromtimestamp(connector_instance._health_cache_time).isoformat()
            else:
                health = connector_instance.check_health(force=force_check)
                last_checked = datetime.fromtimestamp(connector_instance._health_cache_time).isoformat()
        else:
            health = connector_instance.check_health(force=force_check)
            if hasattr(connector_instance, '_health_cache_time'):
                last_checked = datetime.fromtimestamp(connector_instance._health_cache_time).isoformat()
    
    # Build configuration info (sanitized - no secrets)
    config_info = {}
    if connector_instance:
        if connector_name == 'salesforce':
            config_info = {
                "authentication": "OAuth 2.0" if connector_instance.instance_url else "Username/Password",
                "instance_configured": bool(connector_instance.instance_url),
                "domain": connector_instance.domain if hasattr(connector_instance, 'domain') else None,
            }
        elif connector_name == 'supabase':
            config_info = {
                "url_configured": bool(connector_instance.url),
                "table": "salesforce_health_scores"
            }
        elif connector_name == 'mongodb':
            config_info = {
                "database": connector_instance.database if hasattr(connector_instance, 'database') else None,
                "connection_configured": connector_instance.uri is not None if hasattr(connector_instance, 'uri') else False
            }
    
    # Define capabilities
    capabilities = []
    if connector_name == 'salesforce':
        capabilities = ["SOQL Queries", "Opportunity Management", "Account Data", "CRM Analytics"]
    elif connector_name == 'supabase':
        capabilities = ["PostgreSQL Queries", "Health Scores", "Customer Metrics", "Real-time Data"]
    elif connector_name == 'mongodb':
        capabilities = ["NoSQL Queries", "Usage Analytics", "Engagement Metrics", "Document Store"]
    
    # Get live data if requested and connector is healthy (up to 20 records)
    sample_data = None
    if include_sample and health and health.get('healthy'):
        try:
            if connector_name == 'salesforce':
                result = dcl_instance.query('salesforce', query_str="SELECT Id, Name, StageName, Amount FROM Opportunity LIMIT 20")
                sample_data = result[:20] if isinstance(result, list) else []
            elif connector_name == 'supabase':
                result = dcl_instance.query('supabase')
                sample_data = result[:20] if isinstance(result, list) else []
            elif connector_name == 'mongodb':
                result = dcl_instance.query('mongodb')
                if isinstance(result, dict):
                    sample_data = [result]
                elif isinstance(result, list):
                    sample_data = result[:20]
        except Exception as e:
            # If data fetch fails, just don't include it
            print(f"Failed to fetch live data for {connector_name}: {e}")
            sample_data = None
    
    return ConnectorDetails(
        name=connector_name,
        type=meta.get('type', 'Unknown'),
        status=meta.get('status', 'Unknown'),
        description=meta.get('description', 'No description'),
        error=meta.get('error'),
        health=health,
        last_checked=last_checked,
        config_info=config_info,
        capabilities=capabilities,
        sample_data=sample_data
    )

@app.post("/api/workflows/pipeline-health")
async def run_pipeline_health(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=50, ge=1, le=100, description="Number of records per page"),
    cursor: Optional[str] = Query(default=None, description="Cursor for cursor-based pagination")
):
    """
    DEPRECATED: This endpoint is no longer used by the frontend application.
    Frontend now fetches data via Platform Views (dataFetchers.ts → AosClient).
    Kept for backward compatibility and direct API access/testing only.
    
    Execute pipeline health workflow and return metrics with pagination
    """
    dcl_instance = get_dcl()
    try:
        workflow = PipelineHealthWorkflow(dcl_instance)
        
        # First get total count for pagination metadata
        total_count = workflow.get_total_count()
        
        # Calculate offset from page number
        offset = (page - 1) * page_size
        
        # Run workflow with pagination
        df = workflow.run(offset=offset, limit=page_size)
        
        if df is None or df.empty:
            raise HTTPException(status_code=500, detail="No data returned from workflow")
        
        # Get data quality report
        data_quality = workflow.get_data_quality_report()
        
        # Calculate metrics
        total_opps = len(df)
        at_risk = len(df[df['Risk Score'] >= 70]) if 'Risk Score' in df.columns else 0
        stalled = len(df[df['Is Stalled'] == True]) if 'Is Stalled' in df.columns else 0
        healthy = total_opps - at_risk - stalled
        
        total_value = df['Amount'].sum() if 'Amount' in df.columns else 0
        avg_health = df['Health Score'].mean() if 'Health Score' in df.columns else 0
        
        # Prepare metrics
        metrics = [
            MetricResponse(label="Total Opportunities", value=str(total_opps), trend="up"),
            MetricResponse(label="At Risk", value=str(at_risk), change=f"{(at_risk/total_opps*100):.1f}%" if total_opps > 0 else "0%"),
            MetricResponse(label="Healthy", value=str(healthy), change=f"{(healthy/total_opps*100):.1f}%" if total_opps > 0 else "0%"),
            MetricResponse(label="Stalled Deals", value=str(stalled)),
            MetricResponse(label="Pipeline Value", value=f"${total_value:,.0f}"),
            MetricResponse(label="Avg Health Score", value=f"{avg_health:.0f}")
        ]
        
        # Prepare opportunities
        opportunities = []
        for _, row in df.iterrows():
            opportunities.append(OpportunityRecord(
                id=row.get('Opportunity ID', ''),
                name=row.get('Opportunity Name', 'Unknown'),
                account_name=row.get('Account Name', 'Unknown'),
                stage=row.get('Stage', 'Unknown'),
                amount=float(row.get('Amount', 0)),
                health_score=int(row.get('Health Score', 0)),
                risk_score=int(row.get('Risk Score', 0)),
                is_stalled=bool(row.get('Is Stalled', False))
            ))
        
        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size
        has_more = page < total_pages
        
        return {
            "metrics": metrics,
            "opportunities": opportunities,
            "data_quality": {
                "health_data_available": data_quality['health_data_loaded'],
                "usage_data_available": data_quality['usage_data_loaded'],
                "warnings": data_quality['warnings']
            },
            "timestamp": datetime.now().isoformat(),
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total_count,
                "has_more": has_more,
                "next_cursor": None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow error: {str(e)}")

@app.post("/api/workflows/crm-integrity")
async def run_crm_integrity(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=50, ge=1, le=100, description="Number of records per page"),
    cursor: Optional[str] = Query(default=None, description="Cursor for cursor-based pagination")
):
    """
    DEPRECATED: This endpoint is no longer used by the frontend application.
    Frontend now fetches data via Platform Views (dataFetchers.ts → AosClient).
    Kept for backward compatibility and direct API access/testing only.
    
    Execute CRM integrity validation workflow with pagination
    """
    dcl_instance = get_dcl()
    try:
        workflow = CRMIntegrityWorkflow(dcl_instance)
        
        # First get total count for pagination metadata
        total_count = workflow.get_total_count()
        
        # Calculate offset from page number
        offset = (page - 1) * page_size
        
        # Run workflow with pagination
        df = workflow.run_validation(offset=offset, limit=page_size)
        
        if df is None or df.empty:
            raise HTTPException(status_code=500, detail="No data returned from validation")
        
        # Calculate metrics
        total_opps = len(df)
        valid_opps = len(df[df['is_valid'] == True]) if 'is_valid' in df.columns else 0
        invalid_opps = total_opps - valid_opps
        validation_rate = (valid_opps / total_opps * 100) if total_opps > 0 else 0
        
        metrics = [
            MetricResponse(label="Total Records", value=str(total_opps)),
            MetricResponse(label="Valid", value=str(valid_opps), change=f"{validation_rate:.1f}%"),
            MetricResponse(label="Invalid", value=str(invalid_opps), change=f"{(100-validation_rate):.1f}%"),
        ]
        
        # Prepare validation records
        validations = []
        for _, row in df.iterrows():
            validations.append(ValidationRecord(
                opportunity_id=row.get('opportunity_id', ''),
                opportunity_name=row.get('opportunity_name', 'Unknown'),
                account_name=row.get('account_name', 'Unknown'),
                stage=row.get('stage', 'Unknown'),
                amount=float(row.get('amount', 0)),
                is_valid=bool(row.get('is_valid', False)),
                missing_fields=row.get('missing_fields', []),
                validation_issues=row.get('validation_issues', ''),
                risk_level=row.get('risk_level', 'MEDIUM')
            ))
        
        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size
        has_more = page < total_pages
        
        return {
            "metrics": metrics,
            "validations": validations,
            "timestamp": datetime.now().isoformat(),
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total_count,
                "has_more": has_more,
                "next_cursor": None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Detailed health check with connector status"""
    dcl_instance = get_dcl()
    connector_status = {}
    for name, meta in dcl_instance.list_connectors().items():
        connector_status[name] = meta.get('status', 'Unknown')
    
    return {
        "status": "healthy",
        "connectors": connector_status,
        "timestamp": datetime.now().isoformat()
    }

# Serve static files from frontend build (production only)
frontend_dist = Path(__file__).parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve React frontend for all non-API routes"""
        # Skip API routes
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        # Serve index.html for client-side routing
        index_path = frontend_dist / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        else:
            raise HTTPException(status_code=404, detail="Frontend not built. Run: cd frontend && npm run build")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    global dcl
    if dcl is not None:
        print("🛑 Shutting down - cleaning up connector resources...")
        for name, connector_instance in dcl.connector_instances.items():
            if hasattr(connector_instance, 'close'):
                try:
                    connector_instance.close()
                    print(f"✅ Closed {name} connector")
                except Exception as e:
                    print(f"⚠️  Error closing {name} connector: {e}")
        print("✅ All connector resources cleaned up")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
