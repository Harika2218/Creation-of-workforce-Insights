/**
 * PWA Service: Service Worker Registration, Install Prompts, and Push Permissions
 */

export interface PWAInstallEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed'; platform: string }>;
}

class PWAService {
  private deferredPrompt: PWAInstallEvent | null = null;
  private updateAvailableCallback: (() => void) | null = null;
  private installStateChangeCallbacks: Array<(canInstall: boolean) => void> = [];

  constructor() {
    this.init();
  }

  private init() {
    if (typeof window === 'undefined') return;

    // Capture beforeinstallprompt for custom install UX
    window.addEventListener('beforeinstallprompt', (e: Event) => {
      e.preventDefault();
      this.deferredPrompt = e as PWAInstallEvent;
      this.notifyInstallStateChange(true);
    });

    window.addEventListener('appinstalled', () => {
      this.deferredPrompt = null;
      this.notifyInstallStateChange(false);
    });
  }

  public registerServiceWorker(): void {
    if (typeof window === 'undefined' || !('serviceWorker' in navigator)) return;

    window.addEventListener('load', () => {
      navigator.serviceWorker
        .register('/sw.js')
        .then((reg) => {
          // Check for service worker updates
          reg.addEventListener('updatefound', () => {
            const newWorker = reg.installing;
            if (!newWorker) return;

            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                // New update available
                if (this.updateAvailableCallback) {
                  this.updateAvailableCallback();
                }
              }
            });
          });
        })
        .catch((err) => {
          console.warn('Service Worker registration skipped or failed:', err);
        });
    });
  }

  public onUpdateAvailable(callback: () => void): () => void {
    this.updateAvailableCallback = callback;
    return () => {
      if (this.updateAvailableCallback === callback) {
        this.updateAvailableCallback = null;
      }
    };
  }

  public onInstallStateChange(callback: (canInstall: boolean) => void): () => void {
    this.installStateChangeCallbacks.push(callback);
    callback(!!this.deferredPrompt);
    return () => {
      this.installStateChangeCallbacks = this.installStateChangeCallbacks.filter((cb) => cb !== callback);
    };
  }

  private notifyInstallStateChange(canInstall: boolean) {
    this.installStateChangeCallbacks.forEach((cb) => cb(canInstall));
  }

  public canInstall(): boolean {
    return !!this.deferredPrompt;
  }

  public isInstalled(): boolean {
    if (typeof window === 'undefined') return false;
    const hasMatchMedia = typeof window.matchMedia === 'function';
    return Boolean(
      (hasMatchMedia && window.matchMedia('(display-mode: standalone)').matches) ||
      (window.navigator as any).standalone === true ||
      (typeof document !== 'undefined' && document.referrer && document.referrer.includes('android-app://'))
    );
  }

  public async promptInstall(): Promise<boolean> {
    if (!this.deferredPrompt) return false;

    try {
      await this.deferredPrompt.prompt();
      const choice = await this.deferredPrompt.userChoice;
      this.deferredPrompt = null;
      this.notifyInstallStateChange(false);
      return choice.outcome === 'accepted';
    } catch (err) {
      console.error('Error triggering PWA install prompt:', err);
      return false;
    }
  }

  public updateApp(): void {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.getRegistration().then((reg) => {
        if (reg?.waiting) {
          reg.waiting.postMessage({ type: 'SKIP_WAITING' });
        }
        window.location.reload();
      });
    } else {
      window.location.reload();
    }
  }

  // Push Notifications API abstraction
  public isPushSupported(): boolean {
    return typeof window !== 'undefined' && 'Notification' in window;
  }

  public getNotificationPermission(): NotificationPermission {
    if (!this.isPushSupported()) return 'denied';
    return Notification.permission;
  }

  public async requestNotificationPermission(): Promise<NotificationPermission> {
    if (!this.isPushSupported()) return 'denied';
    try {
      const permission = await Notification.requestPermission();
      return permission;
    } catch {
      return 'denied';
    }
  }

  public showLocalNotification(title: string, options?: NotificationOptions): boolean {
    if (!this.isPushSupported() || Notification.permission !== 'granted') return false;
    try {
      new Notification(title, {
        icon: '/icon-192.svg',
        badge: '/favicon.svg',
        ...options,
      });
      return true;
    } catch {
      return false;
    }
  }
}

export const pwaService = new PWAService();
export default pwaService;
