import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { WifiOff, Wifi, Download, RefreshCw, AlertCircle, CheckCircle2, X } from 'lucide-react';
import { pwaService } from '../services/pwaService';
import { offlineAttendanceManager, SyncOutcome } from '../services/offlineAttendance';
import { useToast } from './ToastContext';

interface PWAContextType {
  isOnline: boolean;
  isReconnecting: boolean;
  canInstall: boolean;
  isInstalled: boolean;
  hasUpdate: boolean;
  pendingPunchCount: number;
  promptInstall: () => Promise<boolean>;
  applyUpdate: () => void;
  syncOfflineAttendance: () => Promise<SyncOutcome[]>;
}

const PWAContext = createContext<PWAContextType | undefined>(undefined);

export const PWAProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { showToast } = useToast();
  const [isOnline, setIsOnline] = useState<boolean>(
    typeof navigator !== 'undefined' ? navigator.onLine : true
  );
  const [isReconnecting, setIsReconnecting] = useState<boolean>(false);
  const [canInstall, setCanInstall] = useState<boolean>(pwaService.canInstall());
  const [isInstalled, setIsInstalled] = useState<boolean>(pwaService.isInstalled());
  const [hasUpdate, setHasUpdate] = useState<boolean>(false);
  const [showInstallBanner, setShowInstallBanner] = useState<boolean>(true);
  const [pendingPunchCount, setPendingPunchCount] = useState<number>(
    offlineAttendanceManager.getPendingPunches().length
  );

  // Sync offline attendance helper
  const syncOfflineAttendance = useCallback(async (): Promise<SyncOutcome[]> => {
    if (!navigator.onLine) {
      showToast('Cannot synchronize while offline.', 'warning');
      return [];
    }

    const outcomes = await offlineAttendanceManager.syncPendingQueue();
    const updatedCount = offlineAttendanceManager.getPendingPunches().length;
    setPendingPunchCount(updatedCount);

    if (outcomes.length > 0) {
      const successes = outcomes.filter((o) => o.success).length;
      const failures = outcomes.filter((o) => !o.success).length;

      if (successes > 0 && failures === 0) {
        showToast(`Synchronized ${successes} pending attendance event(s) successfully!`, 'success');
      } else if (failures > 0) {
        showToast(
          `Sync: ${successes} approved, ${failures} rejected by server policy.`,
          'warning'
        );
      }
    }

    return outcomes;
  }, [showToast]);

  useEffect(() => {
    // 1. Register Service Worker
    pwaService.registerServiceWorker();

    // 2. Install state listener
    const unsubInstall = pwaService.onInstallStateChange((available) => {
      setCanInstall(available);
      setIsInstalled(pwaService.isInstalled());
    });

    // 3. Update listener
    const unsubUpdate = pwaService.onUpdateAvailable(() => {
      setHasUpdate(true);
      showToast('New version available. Refresh to update.', 'info');
    });

    // 4. Online/Offline network listeners
    const handleOnline = () => {
      setIsReconnecting(true);
      setIsOnline(true);
      showToast('Connection restored. Reconnecting to enterprise server...', 'info');

      // Auto-sync pending attendance queue on reconnect
      setTimeout(() => {
        syncOfflineAttendance().finally(() => {
          setIsReconnecting(false);
        });
      }, 1500);
    };

    const handleOffline = () => {
      setIsOnline(false);
      setIsReconnecting(false);
      showToast('You are currently offline. Safe cached shell active.', 'warning');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Initial pending punch count
    setPendingPunchCount(offlineAttendanceManager.getPendingPunches().length);

    return () => {
      unsubInstall();
      unsubUpdate();
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [showToast, syncOfflineAttendance]);

  const promptInstall = async (): Promise<boolean> => {
    const outcome = await pwaService.promptInstall();
    if (outcome) {
      setCanInstall(false);
      setShowInstallBanner(false);
      showToast('HRvantage installed successfully!', 'success');
    }
    return outcome;
  };

  const applyUpdate = () => {
    pwaService.updateApp();
  };

  return (
    <PWAContext.Provider
      value={{
        isOnline,
        isReconnecting,
        canInstall,
        isInstalled,
        hasUpdate,
        pendingPunchCount,
        promptInstall,
        applyUpdate,
        syncOfflineAttendance,
      }}
    >
      {/* Network & Offline Status Banner */}
      {!isOnline && (
        <div
          role="status"
          aria-live="polite"
          style={{
            position: 'sticky',
            top: 0,
            zIndex: 9999,
            backgroundColor: '#DC2626',
            color: '#FFFFFF',
            padding: '0.5rem 1rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.75rem',
            fontSize: '0.85rem',
            fontWeight: 500,
            boxShadow: '0 2px 10px rgba(0,0,0,0.3)',
          }}
        >
          <WifiOff size={16} />
          <span>
            You are offline. Shell is cached; real-time HR actions and attendance require server verification.
          </span>
          {pendingPunchCount > 0 && (
            <span
              style={{
                backgroundColor: 'rgba(0,0,0,0.3)',
                padding: '0.15rem 0.5rem',
                borderRadius: '999px',
                fontSize: '0.75rem',
              }}
            >
              {pendingPunchCount} pending punch(es)
            </span>
          )}
        </div>
      )}

      {isReconnecting && (
        <div
          role="status"
          aria-live="polite"
          style={{
            position: 'sticky',
            top: 0,
            zIndex: 9999,
            backgroundColor: '#0284C7',
            color: '#FFFFFF',
            padding: '0.5rem 1rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.75rem',
            fontSize: '0.85rem',
            fontWeight: 500,
          }}
        >
          <RefreshCw size={16} className="animate-spin" />
          <span>Reconnecting to enterprise servers and synchronizing pending events...</span>
        </div>
      )}

      {/* PWA Update Notification Banner */}
      {hasUpdate && (
        <div
          role="alert"
          style={{
            position: 'fixed',
            bottom: '1rem',
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 9998,
            backgroundColor: 'var(--bg-card-solid)',
            border: '1px solid var(--primary)',
            color: '#FFFFFF',
            padding: '0.75rem 1.25rem',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            gap: '1rem',
            boxShadow: 'var(--shadow-lg)',
            maxWidth: '90vw',
          }}
        >
          <RefreshCw size={18} className="text-indigo-400" />
          <span style={{ fontSize: '0.85rem' }}>A new version of HRvantage is available.</span>
          <button
            onClick={applyUpdate}
            style={{
              padding: '0.35rem 0.85rem',
              borderRadius: '6px',
              backgroundColor: 'var(--primary)',
              color: '#FFFFFF',
              border: 'none',
              cursor: 'pointer',
              fontSize: '0.8rem',
              fontWeight: 600,
            }}
          >
            Update Now
          </button>
        </div>
      )}

      {/* Subtle PWA Install Banner */}
      {canInstall && !isInstalled && showInstallBanner && (
        <aside
          aria-label="Install Application"
          style={{
            position: 'fixed',
            bottom: '4.5rem',
            right: '1.25rem',
            zIndex: 1500,
            backgroundColor: 'rgba(22, 30, 49, 0.95)',
            backdropFilter: 'blur(12px)',
            border: '1px solid rgba(99, 102, 241, 0.4)',
            borderRadius: '14px',
            padding: '0.75rem 1rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.85rem',
            boxShadow: '0 10px 25px rgba(0,0,0,0.5)',
            maxWidth: '380px',
          }}
        >
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '10px',
              backgroundColor: 'rgba(99, 102, 241, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}
          >
            <Download size={18} className="text-indigo-400" />
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <p style={{ margin: 0, fontSize: '0.82rem', fontWeight: 600, color: '#FFFFFF' }}>
              Install HRvantage App
            </p>
            <p style={{ margin: 0, fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              Add to Home Screen for fast mobile access
            </p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <button
              onClick={promptInstall}
              style={{
                padding: '0.35rem 0.75rem',
                borderRadius: '6px',
                background: 'linear-gradient(135deg, #6366F1, #8B5CF6)',
                color: '#FFFFFF',
                border: 'none',
                cursor: 'pointer',
                fontSize: '0.75rem',
                fontWeight: 600,
              }}
            >
              Install
            </button>
            <button
              onClick={() => setShowInstallBanner(false)}
              aria-label="Dismiss install banner"
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--text-dim)',
                cursor: 'pointer',
                padding: '0.2rem',
              }}
            >
              <X size={16} />
            </button>
          </div>
        </aside>
      )}

      {children}
    </PWAContext.Provider>
  );
};

export const usePWA = (): PWAContextType => {
  const context = useContext(PWAContext);
  if (!context) {
    throw new Error('usePWA must be used within a PWAProvider');
  }
  return context;
};
