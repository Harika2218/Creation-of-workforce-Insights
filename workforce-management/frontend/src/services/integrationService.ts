import api from './api';

export type IntegrationStatus =
  | 'CONNECTED'
  | 'CONFIGURED'
  | 'NOT_CONFIGURED'
  | 'DISABLED'
  | 'ERROR'
  | 'BLOCKED_EXTERNAL_DEPENDENCY';

export interface IntegrationHealth {
  name: string;
  category: string;
  display_name: string;
  enabled: boolean;
  configured: boolean;
  status: IntegrationStatus;
  last_success: string | null;
  last_failure: string | null;
  error_message: string | null;
  total_calls: number;
  failed_calls: number;
  circuit_breaker_state: string;
}

export interface ConnectionTestResult {
  success: boolean;
  status: IntegrationStatus;
  message: string;
  latency_ms: number;
  timestamp: string;
  details?: Record<string, any>;
}

export interface SyncResult {
  sync_id: string;
  integration: string;
  status: 'SUCCESS' | 'PARTIAL' | 'FAILED' | 'RUNNING';
  records_read: number;
  records_created: number;
  records_updated: number;
  records_failed: number;
  started_at: string;
  completed_at: string | null;
  error_summary: string | null;
}

export const integrationService = {
  async getIntegrations(): Promise<{ integrations: IntegrationHealth[]; count: number; timestamp: string }> {
    const res = await api.get('/integrations');
    return res.data;
  },

  async getIntegrationDetail(name: string): Promise<Record<string, any>> {
    const res = await api.get(`/integrations/${name}`);
    return res.data;
  },

  async testConnection(name: string): Promise<ConnectionTestResult> {
    const res = await api.post(`/integrations/${name}/test`);
    return res.data;
  },

  async triggerSync(name: string): Promise<SyncResult> {
    const res = await api.post(`/integrations/${name}/sync`);
    return res.data;
  },

  async getSyncHistory(name: string, limit: number = 20): Promise<{ integration: string; history: SyncResult[]; count: number }> {
    const res = await api.get(`/integrations/${name}/sync-history`, {
      params: { limit },
    });
    return res.data;
  },
};

export default integrationService;
