import { io, Socket } from 'socket.io-client';

// WebSocket event types
export interface GameState {
  players: Array<{
    name: string;
    chips: number;
    cards: string[];
    bet: number;
  }>;
  communityCards: string[];
  pot: number;
  currentPlayerIndex: number;
  phase: 'waiting' | 'preflop' | 'flop' | 'turn' | 'river' | 'showdown';
}

export interface WebSocketEvents {
  'game:state': (state: GameState) => void;
  'game:action': (action: { type: string; playerId: string; amount?: number }) => void;
  'player:joined': (player: { id: string; name: string }) => void;
  'player:left': (player: { id: string }) => void;
  'error': (error: { message: string }) => void;
}

class WebSocketService {
  private socket: Socket | null = null;
  private listeners: Map<keyof WebSocketEvents, Set<Function>> = new Map();

  connect(url: string = 'ws://localhost:3001'): void {
    if (this.socket?.connected) {
      return;
    }

    this.socket = io(url, {
      transports: ['websocket'],
      autoConnect: true,
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
    });

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
    });

    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error);
    });

    // Setup event forwarding
    this.setupEventForwarding();
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  on<K extends keyof WebSocketEvents>(event: K, callback: WebSocketEvents[K]): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);

    // Return unsubscribe function
    return () => {
      this.listeners.get(event)?.delete(callback);
    };
  }

  emit(event: string, data?: any): void {
    if (!this.socket?.connected) {
      console.warn('Cannot emit, socket not connected');
      return;
    }
    this.socket.emit(event, data);
  }

  // Game actions
  joinGame(gameId: string, playerId: string, playerName: string): void {
    this.emit('game:join', { gameId, playerId, playerName });
  }

  performAction(action: 'fold' | 'call' | 'raise', amount?: number): void {
    this.emit('game:action', { action, amount });
  }

  private setupEventForwarding(): void {
    if (!this.socket) return;

    // Forward all events to registered listeners
    const events: (keyof WebSocketEvents)[] = [
      'game:state',
      'game:action',
      'player:joined',
      'player:left',
      'error',
    ];

    events.forEach((event) => {
      this.socket!.on(event, (...args: any[]) => {
        const listeners = this.listeners.get(event);
        if (listeners) {
          listeners.forEach((callback) => callback(...args));
        }
      });
    });
  }
}

export const wsService = new WebSocketService();
