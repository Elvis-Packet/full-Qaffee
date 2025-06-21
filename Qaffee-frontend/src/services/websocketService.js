import { toast } from 'react-toastify';

class WebSocketService {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000; // Start with 1 second delay
    this.subscribers = new Map();
    this.isConnecting = false;
    this.baseUrl = import.meta.env.VITE_WS_URL || 'ws://143.198.224.163/ws';
  }

  connect(userId) {
    if (this.isConnecting || this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    this.isConnecting = true;
    const token = localStorage.getItem('token');
    const wsUrl = `${this.baseUrl}?token=${token}&user_id=${userId}`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onclose = () => {
        this.isConnecting = false;
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          setTimeout(() => {
            this.reconnectAttempts++;
            this.reconnectDelay *= 2; // Exponential backoff
            this.connect(userId);
          }, this.reconnectDelay);
        } else {
          toast.error('Connection lost. Please refresh the page.');
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.isConnecting = false;
      };
    } catch (error) {
      console.error('WebSocket connection error:', error);
      this.isConnecting = false;
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.subscribers.clear();
  }

  subscribe(eventType, callback) {
    if (!this.subscribers.has(eventType)) {
      this.subscribers.set(eventType, new Set());
    }
    this.subscribers.get(eventType).add(callback);

    // Return unsubscribe function
    return () => {
      const callbacks = this.subscribers.get(eventType);
      if (callbacks) {
        callbacks.delete(callback);
        if (callbacks.size === 0) {
          this.subscribers.delete(eventType);
        }
      }
    };
  }

  handleMessage(data) {
    const { type, payload } = data;

    if (this.subscribers.has(type)) {
      this.subscribers.get(type).forEach(callback => {
        try {
          callback(payload);
        } catch (error) {
          console.error(`Error in subscriber callback for ${type}:`, error);
        }
      });
    }
  }

  // Send message to server
  send(type, payload) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, payload }));
    } else {
      console.error('WebSocket is not connected');
      toast.error('Connection error. Please refresh the page.');
    }
  }

  // Helper method to check connection status
  isConnected() {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// Create singleton instance
const websocketService = new WebSocketService();

export default websocketService; 