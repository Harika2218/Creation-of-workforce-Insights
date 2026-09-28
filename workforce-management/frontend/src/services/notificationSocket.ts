/**
 * Real-Time Notification WebSocket Client
 * ---------------------------------------
 * Connects to FastAPI WebSocket /api/v1/notifications/ws with JWT token,
 * manages reconnects with exponential backoff, and emits push events to subscribers.
 */

import { NotificationItem } from '../types';

type NotificationListener = (notification: NotificationItem) => void;
type StatusListener = (connected: boolean) => void;

class NotificationSocketService {
  private socket: WebSocket | null = null;
  private token: string | null = null;
  private notificationListeners: Set<NotificationListener> = new Set();
  private statusListeners: Set<StatusListener> = new Set();
  private reconnectTimer: any = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private isConnected = false;

  public connect(token: string) {
    if (!token) return;
    this.token = token;

    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return;
    }

    try {
      // Determine ws protocol based on window location
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.hostname || 'localhost';
      const port = '8000'; // FastAPI backend default port
      const url = `${protocol}//${host}:${port}/api/v1/notifications/ws?token=${token}`;

      this.socket = new WebSocket(url);

      this.socket.onopen = () => {
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.notifyStatus(true);
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data && data.notification_id) {
            this.notifyListeners(data as NotificationItem);
          }
        } catch {
          // Ignore non-json ping/pong
        }
      };

      this.socket.onclose = () => {
        this.isConnected = false;
        this.notifyStatus(false);
        this.scheduleReconnect();
      };

      this.socket.onerror = () => {
        this.isConnected = false;
        this.notifyStatus(false);
      };
    } catch {
      this.isConnected = false;
      this.notifyStatus(false);
      this.scheduleReconnect();
    }
  }

  public disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    this.isConnected = false;
    this.notifyStatus(false);
  }

  private scheduleReconnect() {
    if (!this.token || this.reconnectAttempts >= this.maxReconnectAttempts) return;
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 15000);
    this.reconnectAttempts++;
    this.reconnectTimer = setTimeout(() => {
      if (this.token) {
        this.connect(this.token);
      }
    }, delay);
  }

  public subscribe(listener: NotificationListener): () => void {
    this.notificationListeners.add(listener);
    return () => {
      this.notificationListeners.delete(listener);
    };
  }

  public subscribeStatus(listener: StatusListener): () => void {
    this.statusListeners.add(listener);
    listener(this.isConnected);
    return () => {
      this.statusListeners.delete(listener);
    };
  }

  private notifyListeners(notification: NotificationItem) {
    this.notificationListeners.forEach((listener) => {
      try {
        listener(notification);
      } catch (err) {
        console.error('Error in notification socket listener:', err);
      }
    });
  }

  private notifyStatus(connected: boolean) {
    this.statusListeners.forEach((listener) => {
      try {
        listener(connected);
      } catch (err) {
        console.error('Error in status listener:', err);
      }
    });
  }

  public getIsConnected(): boolean {
    return this.isConnected;
  }
}

export const notificationSocket = new NotificationSocketService();
