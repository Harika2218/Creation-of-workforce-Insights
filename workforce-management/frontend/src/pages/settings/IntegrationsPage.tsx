import React, { useState, useEffect } from 'react';
import {
  Plug,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Clock,
  ShieldCheck,
  Server,
  Zap,
  Mail,
  MessageSquare,
  Calendar,
  KeyRound,
  FileSpreadsheet,
  Building2,
  Fingerprint,
  Info,
  ExternalLink,
  Search,
  Activity,
} from 'lucide-react';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Modal } from '../../components/common/Modal';
import { LoadingSkeleton } from '../../components/common/LoadingSkeleton';
import { useToast } from '../../context/ToastContext';
import {
  integrationService,
  IntegrationHealth,
  ConnectionTestResult,
  SyncResult,
  IntegrationStatus,
} from '../../services/integrationService';

export const IntegrationsPage: React.FC = () => {
  const { showToast } = useToast();
  const [integrations, setIntegrations] = useState<IntegrationHealth[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');

  // Testing & Sync states
  const [testingName, setTestingName] = useState<string | null>(null);
  const [syncingName, setSyncingName] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<{ name: string; result: ConnectionTestResult } | null>(null);

  // Sync History Modal
  const [historyModalOpen, setHistoryModalOpen] = useState<boolean>(false);
  const [historyIntegration, setHistoryIntegration] = useState<string | null>(null);
  const [syncHistory, setSyncHistory] = useState<SyncResult[]>([]);
  const [historyLoading, setHistoryLoading] = useState<boolean>(false);

  // Webhook Info Modal
  const [webhookModalOpen, setWebhookModalOpen] = useState<boolean>(false);
  const [selectedWebhook, setSelectedWebhook] = useState<IntegrationHealth | null>(null);

  const fetchIntegrations = async () => {
    try {
      setIsLoading(true);
      const res = await integrationService.getIntegrations();
      setIntegrations(res.integrations || []);
    } catch (err: any) {
      console.error('Failed to load integrations:', err);
      showToast('Failed to load integrations', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchIntegrations();
  }, []);

  const handleTestConnection = async (integration: IntegrationHealth) => {
    try {
      setTestingName(integration.name);
      const res = await integrationService.testConnection(integration.name);
      setTestResult({ name: integration.display_name, result: res });
      if (res.success) {
        showToast(`${integration.display_name} connection test passed (${res.latency_ms}ms)`, 'success');
      } else {
        showToast(`${integration.display_name} test: ${res.message}`, 'warning');
      }
      // Refresh list to update health status
      const updated = await integrationService.getIntegrations();
      setIntegrations(updated.integrations || []);
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Connection test failed';
      showToast(`${integration.display_name} test failed: ${msg}`, 'error');
    } finally {
      setTestingName(null);
    }
  };

  const handleTriggerSync = async (integration: IntegrationHealth) => {
    try {
      setSyncingName(integration.name);
      const res = await integrationService.triggerSync(integration.name);
      showToast(
        `Sync completed for ${integration.display_name}: Read ${res.records_read}, Updated ${res.records_updated}`,
        res.status === 'SUCCESS' ? 'success' : 'warning'
      );
      // Refresh list
      const updated = await integrationService.getIntegrations();
      setIntegrations(updated.integrations || []);
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Synchronization failed';
      showToast(`Sync failed: ${msg}`, 'error');
    } finally {
      setSyncingName(null);
    }
  };

  const handleOpenSyncHistory = async (integration: IntegrationHealth) => {
    setHistoryIntegration(integration.display_name);
    setHistoryModalOpen(true);
    setHistoryLoading(true);
    try {
      const res = await integrationService.getSyncHistory(integration.name);
      setSyncHistory(res.history || []);
    } catch (err: any) {
      showToast('Failed to load sync history', 'error');
    } finally {
      setHistoryLoading(false);
    }
  };

  const getStatusBadge = (status: IntegrationStatus) => {
    switch (status) {
      case 'CONNECTED':
        return <Badge variant="success">Connected</Badge>;
      case 'CONFIGURED':
        return <Badge variant="info">Configured</Badge>;
      case 'NOT_CONFIGURED':
        return <Badge variant="neutral">Not Configured</Badge>;
      case 'DISABLED':
        return <Badge variant="neutral">Disabled</Badge>;
      case 'BLOCKED_EXTERNAL_DEPENDENCY':
        return <Badge variant="warning">Blocked Dependency</Badge>;
      case 'ERROR':
        return <Badge variant="danger">Error</Badge>;
      default:
        return <Badge variant="neutral">{status}</Badge>;
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'email':
        return <Mail size={22} className="text-blue-400" />;
      case 'messaging':
        return <MessageSquare size={22} className="text-purple-400" />;
      case 'calendar':
        return <Calendar size={22} className="text-green-400" />;
      case 'identity':
        return <KeyRound size={22} className="text-amber-400" />;
      case 'payroll':
        return <FileSpreadsheet size={22} className="text-emerald-400" />;
      case 'erp':
      case 'hrms':
        return <Building2 size={22} className="text-indigo-400" />;
      case 'biometric':
        return <Fingerprint size={22} className="text-cyan-400" />;
      default:
        return <Plug size={22} className="text-sky-400" />;
    }
  };

  const filteredIntegrations = integrations.filter((item) => {
    const matchesSearch =
      item.display_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = categoryFilter === 'all' || item.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  const totalCount = integrations.length;
  const configuredCount = integrations.filter((i) => i.configured).length;
  const connectedCount = integrations.filter((i) => i.status === 'CONNECTED').length;
  const blockedCount = integrations.filter((i) => i.status === 'BLOCKED_EXTERNAL_DEPENDENCY').length;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <div
              style={{
                width: '42px',
                height: '42px',
                borderRadius: '12px',
                background: 'linear-gradient(135deg, rgba(56, 189, 248, 0.2), rgba(129, 140, 248, 0.2))',
                border: '1px solid rgba(56, 189, 248, 0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Plug size={24} className="text-sky-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white">Enterprise Integrations</h1>
              <p className="text-sm text-gray-400">
                Connect external enterprise services, configure identity providers, sync ERP data, and monitor connector health.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            onClick={fetchIntegrations}
            disabled={isLoading}
            className="flex items-center gap-2"
          >
            <RefreshCw size={16} className={isLoading ? 'animate-spin' : ''} />
            Refresh Status
          </Button>
        </div>
      </div>

      {/* Overview Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-4 bg-slate-900/60 border-slate-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase font-semibold text-gray-400 tracking-wider">Total Connectors</p>
              <p className="text-2xl font-bold text-white mt-1">{totalCount}</p>
            </div>
            <div className="p-2.5 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400">
              <Server size={20} />
            </div>
          </div>
          <p className="text-xs text-gray-400 mt-2">Modular integration adapters</p>
        </Card>

        <Card className="p-4 bg-slate-900/60 border-slate-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase font-semibold text-gray-400 tracking-wider">Configured</p>
              <p className="text-2xl font-bold text-emerald-400 mt-1">{configuredCount}</p>
            </div>
            <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <ShieldCheck size={20} />
            </div>
          </div>
          <p className="text-xs text-gray-400 mt-2">Services with valid env credentials</p>
        </Card>

        <Card className="p-4 bg-slate-900/60 border-slate-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase font-semibold text-gray-400 tracking-wider">Connected</p>
              <p className="text-2xl font-bold text-sky-400 mt-1">{connectedCount}</p>
            </div>
            <div className="p-2.5 rounded-xl bg-sky-500/10 border border-sky-500/20 text-sky-400">
              <Activity size={20} />
            </div>
          </div>
          <p className="text-xs text-gray-400 mt-2">Live ping verified</p>
        </Card>

        <Card className="p-4 bg-slate-900/60 border-slate-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase font-semibold text-gray-400 tracking-wider">External Dependencies</p>
              <p className="text-2xl font-bold text-amber-400 mt-1">{blockedCount}</p>
            </div>
            <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
              <AlertTriangle size={20} />
            </div>
          </div>
          <p className="text-xs text-gray-400 mt-2">Awaiting external tenant credentials</p>
        </Card>
      </div>

      {/* Controls & Filters Bar */}
      <div className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center justify-between bg-slate-900/40 p-3 rounded-xl border border-slate-800/80">
        <div className="relative flex-1 max-w-md">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search integrations, categories, or protocols..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-800/50 border border-slate-700/60 rounded-lg text-sm text-white placeholder-gray-400 focus:outline-none focus:border-sky-500 transition-colors"
          />
        </div>

        <div className="flex items-center gap-2 overflow-x-auto">
          {['all', 'email', 'messaging', 'calendar', 'identity', 'payroll', 'erp', 'hrms', 'biometric'].map((cat) => (
            <button
              key={cat}
              onClick={() => setCategoryFilter(cat)}
              className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all capitalize whitespace-nowrap ${
                categoryFilter === cat
                  ? 'bg-sky-500/20 text-sky-400 border border-sky-500/40'
                  : 'bg-slate-800/40 text-gray-400 hover:text-white border border-transparent'
              }`}
            >
              {cat === 'all' ? 'All Categories' : cat}
            </button>
          ))}
        </div>
      </div>

      {/* Integration Cards Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {[...Array(6)].map((_, i) => (
            <LoadingSkeleton key={i} height="220px" lines={1} />
          ))}
        </div>
      ) : filteredIntegrations.length === 0 ? (
        <Card className="p-8 text-center bg-slate-900/40 border-slate-800">
          <Info size={36} className="mx-auto text-gray-400 mb-3" />
          <p className="text-base font-semibold text-white">No integrations found</p>
          <p className="text-sm text-gray-400 mt-1">Try clearing your search query or category filter.</p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredIntegrations.map((item) => (
            <Card
              key={item.name}
              className="flex flex-col justify-between p-5 bg-slate-900/60 border-slate-800 hover:border-slate-700 transition-all shadow-lg"
            >
              <div>
                {/* Header: Icon, Name & Status */}
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-xl bg-slate-800/80 border border-slate-700/60">
                      {getCategoryIcon(item.category)}
                    </div>
                    <div>
                      <h3 className="font-semibold text-base text-white leading-snug">{item.display_name}</h3>
                      <p className="text-xs text-gray-400 capitalize">{item.category} Connector</p>
                    </div>
                  </div>
                  <div>{getStatusBadge(item.status)}</div>
                </div>

                {/* Configuration & Circuit State */}
                <div className="mt-4 pt-3 border-t border-slate-800/80 space-y-2 text-xs">
                  <div className="flex justify-between items-center text-gray-400">
                    <span>Feature Flag:</span>
                    <span className={item.enabled ? 'text-emerald-400 font-mono' : 'text-gray-500 font-mono'}>
                      {item.enabled ? 'ENABLED' : 'DISABLED'}
                    </span>
                  </div>

                  <div className="flex justify-between items-center text-gray-400">
                    <span>Credentials:</span>
                    <span className={item.configured ? 'text-emerald-400' : 'text-amber-400'}>
                      {item.configured ? 'Configured (.env)' : 'Missing / Incomplete'}
                    </span>
                  </div>

                  <div className="flex justify-between items-center text-gray-400">
                    <span>Circuit Breaker:</span>
                    <span
                      className={`font-mono px-1.5 py-0.5 rounded text-[11px] ${
                        item.circuit_breaker_state === 'CLOSED'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'bg-red-500/10 text-red-400 border border-red-500/20'
                      }`}
                    >
                      {item.circuit_breaker_state}
                    </span>
                  </div>

                  <div className="flex justify-between items-center text-gray-400">
                    <span>Last Success:</span>
                    <span className="text-gray-300 font-mono text-[11px]">
                      {item.last_success ? item.last_success.split('T')[0] : 'Never'}
                    </span>
                  </div>

                  {item.error_message && (
                    <div className="p-2 rounded bg-amber-500/10 border border-amber-500/20 text-amber-300 text-[11px] break-words">
                      {item.error_message}
                    </div>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="mt-5 pt-3 border-t border-slate-800/80 flex items-center justify-between gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleTestConnection(item)}
                  disabled={testingName === item.name}
                  className="flex-1 text-xs"
                >
                  {testingName === item.name ? (
                    <RefreshCw size={13} className="animate-spin mr-1.5" />
                  ) : (
                    <Zap size={13} className="mr-1.5 text-amber-400" />
                  )}
                  Test Connection
                </Button>

                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleTriggerSync(item)}
                  disabled={syncingName === item.name || !item.configured}
                  title="Trigger Manual Synchronization"
                  className="text-xs px-2.5"
                >
                  <RefreshCw size={13} className={syncingName === item.name ? 'animate-spin' : ''} />
                </Button>

                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleOpenSyncHistory(item)}
                  title="View Sync History Logs"
                  className="text-xs px-2.5 text-gray-400 hover:text-white"
                >
                  <Clock size={13} />
                </Button>

                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setSelectedWebhook(item);
                    setWebhookModalOpen(true);
                  }}
                  title="Webhook & Protocol Info"
                  className="text-xs px-2.5 text-gray-400 hover:text-white"
                >
                  <Info size={13} />
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Safe Connection Test Result Modal */}
      <Modal
        isOpen={!!testResult}
        onClose={() => setTestResult(null)}
        title={
          <div className="flex items-center gap-2">
            <Zap size={18} className="text-amber-400" />
            <span>Connection Test: {testResult?.name}</span>
          </div>
        }
      >
        {testResult && (
          <div className="space-y-4 text-sm">
            <div
              className={`p-4 rounded-xl border flex items-start gap-3 ${
                testResult.result.success
                  ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-200'
                  : 'bg-amber-500/10 border-amber-500/20 text-amber-200'
              }`}
            >
              {testResult.result.success ? (
                <CheckCircle2 size={20} className="text-emerald-400 mt-0.5" />
              ) : (
                <AlertTriangle size={20} className="text-amber-400 mt-0.5" />
              )}
              <div className="space-y-1">
                <p className="font-semibold">{testResult.result.message}</p>
                <div className="flex items-center gap-3 text-xs opacity-80">
                  <span>Latency: {testResult.result.latency_ms.toFixed(1)} ms</span>
                  <span>Timestamp: {testResult.result.timestamp}</span>
                </div>
              </div>
            </div>

            {testResult.result.details && (
              <div className="space-y-2">
                <p className="text-xs font-semibold uppercase tracking-wider text-gray-400">Diagnostics Detail</p>
                <pre className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-gray-300 overflow-x-auto">
                  {JSON.stringify(testResult.result.details, null, 2)}
                </pre>
              </div>
            )}

            <div className="flex justify-end pt-2">
              <Button variant="outline" size="sm" onClick={() => setTestResult(null)}>
                Close
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Sync History Modal */}
      <Modal
        isOpen={historyModalOpen}
        onClose={() => setHistoryModalOpen(false)}
        title={
          <div className="flex items-center gap-2">
            <Clock size={18} className="text-sky-400" />
            <span>Sync History: {historyIntegration}</span>
          </div>
        }
        maxWidth="720px"
      >
        <div className="space-y-4">
          {historyLoading ? (
            <LoadingSkeleton height="180px" />
          ) : syncHistory.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              <Info size={32} className="mx-auto mb-2 opacity-60" />
              <p className="text-sm">No synchronization runs recorded yet.</p>
              <p className="text-xs text-gray-500 mt-1">Manual or scheduled syncs will appear here.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 text-gray-400">
                    <th className="py-2 px-3">Sync ID</th>
                    <th className="py-2 px-3">Status</th>
                    <th className="py-2 px-3">Read</th>
                    <th className="py-2 px-3">Created</th>
                    <th className="py-2 px-3">Updated</th>
                    <th className="py-2 px-3">Failed</th>
                    <th className="py-2 px-3">Started</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono text-gray-300">
                  {syncHistory.map((s) => (
                    <tr key={s.sync_id} className="hover:bg-slate-800/30">
                      <td className="py-2.5 px-3 text-sky-400">{s.sync_id}</td>
                      <td className="py-2.5 px-3">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-sans font-semibold ${
                            s.status === 'SUCCESS'
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                              : s.status === 'PARTIAL'
                              ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                              : 'bg-red-500/10 text-red-400 border border-red-500/20'
                          }`}
                        >
                          {s.status}
                        </span>
                      </td>
                      <td className="py-2.5 px-3">{s.records_read}</td>
                      <td className="py-2.5 px-3 text-emerald-400">{s.records_created}</td>
                      <td className="py-2.5 px-3 text-sky-400">{s.records_updated}</td>
                      <td className="py-2.5 px-3 text-red-400">{s.records_failed}</td>
                      <td className="py-2.5 px-3 text-gray-400">{s.started_at ? s.started_at.split('T')[0] : '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="flex justify-end pt-2">
            <Button variant="outline" size="sm" onClick={() => setHistoryModalOpen(false)}>
              Done
            </Button>
          </div>
        </div>
      </Modal>

      {/* Webhook & Security Spec Modal */}
      <Modal
        isOpen={webhookModalOpen}
        onClose={() => setWebhookModalOpen(false)}
        title={
          <div className="flex items-center gap-2">
            <ShieldCheck size={18} className="text-emerald-400" />
            <span>Webhook Specification: {selectedWebhook?.display_name}</span>
          </div>
        }
        maxWidth="640px"
      >
        {selectedWebhook && (
          <div className="space-y-4 text-xs text-gray-300">
            <div>
              <p className="font-semibold text-white text-sm mb-1">Inbound Webhook Endpoint</p>
              <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg font-mono text-sky-300 select-all">
                POST /api/v1/integrations/webhooks/{selectedWebhook.name}
              </div>
            </div>

            <div className="space-y-2">
              <p className="font-semibold text-white">Security & Signature Verification</p>
              <ul className="list-disc pl-5 space-y-1 text-gray-400">
                <li>
                  <strong className="text-gray-200">HMAC-SHA256 Header:</strong> Include{' '}
                  <code className="text-sky-300 font-mono">X-Webhook-Signature: sha256=&lt;hash&gt;</code>
                </li>
                <li>
                  <strong className="text-gray-200">Secret:</strong> Configured via{' '}
                  <code className="text-sky-300 font-mono">WEBHOOK_SECRET</code> in <code className="font-mono">.env</code>
                </li>
                <li>
                  <strong className="text-gray-200">Replay Protection:</strong> Events within a 5-minute window are verified; duplicates rejected via idempotency key.
                </li>
                <li>
                  <strong className="text-gray-200">Fault Isolation:</strong> Webhook processing executes with circuit-breaker protection and audit-logging.
                </li>
              </ul>
            </div>

            <div className="flex justify-end pt-2">
              <Button variant="outline" size="sm" onClick={() => setWebhookModalOpen(false)}>
                Close
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default IntegrationsPage;
