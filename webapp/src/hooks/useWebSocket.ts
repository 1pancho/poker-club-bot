import { useEffect, useState } from 'react';
import { wsService, type GameState } from '../services/websocket';

export function useWebSocket() {
  const [connected, setConnected] = useState(false);
  const [gameState, setGameState] = useState<GameState | null>(null);

  useEffect(() => {
    // Connect to WebSocket server
    wsService.connect();

    // Listen for game state updates
    const unsubscribeState = wsService.on('game:state', (state) => {
      setGameState(state);
      setConnected(true);
    });

    const unsubscribeError = wsService.on('error', (error) => {
      console.error('Game error:', error);
    });

    // Cleanup
    return () => {
      unsubscribeState();
      unsubscribeError();
    };
  }, []);

  return {
    connected,
    gameState,
    joinGame: (gameId: string, playerId: string, playerName: string) => {
      wsService.joinGame(gameId, playerId, playerName);
    },
    fold: () => wsService.performAction('fold'),
    call: () => wsService.performAction('call'),
    raise: (amount: number) => wsService.performAction('raise', amount),
  };
}
