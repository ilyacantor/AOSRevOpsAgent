import React, { useState, useEffect } from 'react';
import { X, CheckCircle, AlertCircle, Database, Activity, Settings, Code } from 'lucide-react';
import { Card } from './Card';

interface ConnectorDetails {
  name: string;
  type: string;
  status: string;
  description: string;
  error?: string | null;
  health?: {
    healthy: boolean;
    error?: string | null;
  } | null;
  last_checked?: string | null;
  config_info: Record<string, any>;
  capabilities: string[];
  sample_data?: Array<Record<string, any>> | null;
}

interface ConnectorDetailModalProps {
  connectorName: string;
  onClose: () => void;
}

export const ConnectorDetailModal: React.FC<ConnectorDetailModalProps> = ({ connectorName, onClose }) => {
  const [details, setDetails] = useState<ConnectorDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'health' | 'data'>('overview');

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/dcl/connectors/${connectorName}`);
        if (!response.ok) {
          throw new Error(`Failed to fetch connector details: ${response.statusText}`);
        }
        const data = await response.json();
        setDetails(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load connector details');
      } finally {
        setLoading(false);
      }
    };

    fetchDetails();
  }, [connectorName]);

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50" onClick={onClose}>
        <div className="bg-card-bg border border-border-primary rounded-xl p-8 max-w-4xl w-full mx-4" onClick={(e) => e.stopPropagation()}>
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-accent"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !details) {
    return (
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50" onClick={onClose}>
        <div className="bg-card-bg border border-border-primary rounded-xl p-8 max-w-4xl w-full mx-4" onClick={(e) => e.stopPropagation()}>
          <div className="text-center py-12">
            <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <p className="text-red-500">{error || 'Failed to load connector details'}</p>
            <button
              onClick={onClose}
              className="mt-4 px-4 py-2 bg-teal-accent text-white rounded hover:bg-teal-hover transition"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    const lowerStatus = status.toLowerCase();
    if (lowerStatus === 'healthy') return 'bg-green-500/20 text-green-500';
    if (lowerStatus === 'mock') return 'bg-yellow-500/20 text-yellow-500';
    return 'bg-red-500/20 text-red-500';
  };

  const getDisplayName = (name: string) => {
    if (name.toLowerCase() === 'mongodb') {
      return 'MongoDB';
    }
    return name.charAt(0).toUpperCase() + name.slice(1);
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-card-bg border border-border-primary rounded-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="p-6 border-b border-border-primary flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-teal-accent/10 rounded-lg">
              <Database className="w-8 h-8 text-teal-accent" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">{getDisplayName(details.name)}</h2>
              <p className="text-text-secondary">{details.type}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/5 rounded-lg transition"
          >
            <X className="w-6 h-6 text-text-secondary" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 px-6 pt-4 border-b border-border-primary">
          <button
            onClick={() => setActiveTab('overview')}
            className={`pb-3 px-2 font-medium transition-colors ${
              activeTab === 'overview'
                ? 'text-teal-accent border-b-2 border-teal-accent'
                : 'text-text-secondary hover:text-white'
            }`}
          >
            <div className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              Overview
            </div>
          </button>
          <button
            onClick={() => setActiveTab('health')}
            className={`pb-3 px-2 font-medium transition-colors ${
              activeTab === 'health'
                ? 'text-teal-accent border-b-2 border-teal-accent'
                : 'text-text-secondary hover:text-white'
            }`}
          >
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Health
            </div>
          </button>
          <button
            onClick={() => setActiveTab('data')}
            className={`pb-3 px-2 font-medium transition-colors ${
              activeTab === 'data'
                ? 'text-teal-accent border-b-2 border-teal-accent'
                : 'text-text-secondary hover:text-white'
            }`}
          >
            <div className="flex items-center gap-2">
              <Code className="w-4 h-4" />
              Live Data
            </div>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Status */}
              <Card>
                <h3 className="text-lg font-semibold text-white mb-4">Connection Status</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-text-secondary text-sm">Status</span>
                    <div className="mt-1">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(details.status)}`}>
                        {details.status}
                      </span>
                    </div>
                  </div>
                  <div>
                    <span className="text-text-secondary text-sm">Last Checked</span>
                    <p className="text-white mt-1">{details.last_checked ? new Date(details.last_checked).toLocaleString() : 'Never'}</p>
                  </div>
                </div>
                {details.error && (
                  <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                    <p className="text-red-400 text-sm">{details.error}</p>
                  </div>
                )}
              </Card>

              {/* Configuration */}
              <Card>
                <h3 className="text-lg font-semibold text-white mb-4">Configuration</h3>
                <div className="space-y-3">
                  {Object.entries(details.config_info).map(([key, value]) => (
                    <div key={key} className="flex justify-between items-center">
                      <span className="text-text-secondary text-sm capitalize">{key.replace(/_/g, ' ')}</span>
                      <span className="text-white text-sm font-medium">
                        {typeof value === 'boolean' ? (value ? '✓ Yes' : '✗ No') : String(value)}
                      </span>
                    </div>
                  ))}
                </div>
              </Card>

              {/* Capabilities */}
              <Card>
                <h3 className="text-lg font-semibold text-white mb-4">Capabilities</h3>
                <div className="flex flex-wrap gap-2">
                  {details.capabilities.map((capability) => (
                    <span
                      key={capability}
                      className="px-3 py-1 bg-teal-accent/10 text-teal-accent rounded-full text-sm"
                    >
                      {capability}
                    </span>
                  ))}
                </div>
              </Card>

              {/* Description */}
              <Card>
                <h3 className="text-lg font-semibold text-white mb-2">Description</h3>
                <p className="text-text-secondary">{details.description}</p>
              </Card>
            </div>
          )}

          {activeTab === 'health' && (
            <div className="space-y-6">
              <Card>
                <div className="flex items-center gap-3 mb-4">
                  {details.health?.healthy ? (
                    <CheckCircle className="w-8 h-8 text-green-500" />
                  ) : (
                    <AlertCircle className="w-8 h-8 text-red-500" />
                  )}
                  <h3 className="text-lg font-semibold text-white">
                    {details.health?.healthy ? 'Connection Healthy' : 'Connection Issues Detected'}
                  </h3>
                </div>

                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="text-text-secondary text-sm">Health Status</span>
                      <p className={`text-lg font-semibold mt-1 ${details.health?.healthy ? 'text-green-500' : 'text-red-500'}`}>
                        {details.health?.healthy ? 'Healthy' : 'Unhealthy'}
                      </p>
                    </div>
                    <div>
                      <span className="text-text-secondary text-sm">Last Check</span>
                      <p className="text-white mt-1">{details.last_checked ? new Date(details.last_checked).toLocaleString() : 'Never'}</p>
                    </div>
                  </div>

                  {details.health?.error && (
                    <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
                      <h4 className="text-red-400 font-semibold mb-2">Error Details</h4>
                      <p className="text-red-300 text-sm font-mono">{details.health.error}</p>
                    </div>
                  )}

                  {details.health?.healthy && (
                    <div className="p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
                      <p className="text-green-400 text-sm">
                        ✓ Connection is operational and ready to serve requests
                      </p>
                    </div>
                  )}
                </div>
              </Card>
            </div>
          )}

          {activeTab === 'data' && (
            <div className="space-y-6">
              {details.sample_data && details.sample_data.length > 0 ? (
                <Card>
                  <h3 className="text-lg font-semibold text-white mb-4">Live Records from Instance</h3>
                  <div className="space-y-3">
                    {details.sample_data.map((record, index) => (
                      <div key={index} className="p-4 bg-bg-primary/50 rounded-lg border border-border-primary">
                        <pre className="text-sm text-text-secondary overflow-x-auto">
                          {JSON.stringify(record, null, 2)}
                        </pre>
                      </div>
                    ))}
                  </div>
                  <p className="text-text-secondary text-sm mt-4">
                    Showing {details.sample_data.length} live record{details.sample_data.length !== 1 ? 's' : ''} from your instance (up to 20 max)
                  </p>
                </Card>
              ) : (
                <Card>
                  <div className="text-center py-12">
                    <Code className="w-16 h-16 text-text-secondary mx-auto mb-4 opacity-50" />
                    <p className="text-text-secondary">
                      {details.health?.healthy
                        ? 'No live data available'
                        : 'Live data unavailable - connector not healthy'}
                    </p>
                  </div>
                </Card>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-border-primary flex justify-end">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-teal-accent text-white rounded-lg hover:bg-teal-hover transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
