import { useState, useEffect } from 'react';
import './index.css';
import { PokerTable } from './components/PokerTable';
import { useWebSocket } from './hooks/useWebSocket';
import { telegramService } from './services/telegram';

function App() {
  const [gameStarted, setGameStarted] = useState(false);
  const { connected, gameState, joinGame, fold, call, raise } = useWebSocket();

  useEffect(() => {
    // Initialize Telegram WebApp
    telegramService.init();
  }, []);

  const handleStartGame = () => {
    const userId = telegramService.getUserId();
    const userName = telegramService.getUserName();
    const gameId = 'default'; // In production, this could be from a room code

    joinGame(gameId, userId, userName);
    setGameStarted(true);
    telegramService.hapticFeedback('impact', 'medium');
  };

  const handleFold = () => {
    fold();
    telegramService.hapticFeedback('impact', 'light');
  };

  const handleCall = () => {
    call();
    telegramService.hapticFeedback('impact', 'medium');
  };

  const handleRaise = () => {
    raise(100); // Default raise amount
    telegramService.hapticFeedback('impact', 'heavy');
  };

  // Use real game state if connected, otherwise show mock data
  const players = gameState?.players || [
    { name: 'Вы', chips: 1000, cards: ['A♠', 'K♠'], bet: 50 },
    { name: 'Игрок 2', chips: 850, cards: ['?', '?'], bet: 50 },
    { name: 'Игрок 3', chips: 1200, cards: ['?', '?'], bet: 0 },
    { name: 'Игрок 4', chips: 600, cards: ['?', '?'], bet: 50 },
  ];

  const communityCards = gameState?.communityCards || ['A♥', 'K♦', 'Q♣', '?', '?'];
  const pot = gameState?.pot || 200;
  const currentPlayerIndex = gameState?.currentPlayerIndex || 0;

  return (
    <div className="min-h-screen">
      {!gameStarted ? (
        <div className="h-screen flex flex-col items-center justify-center">
          <div className="text-center mb-12 animate-fade-in">
            <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-yellow-400 via-orange-500 to-red-500 bg-clip-text text-transparent">
              🎰 Poker Club
            </h1>
            <p className="text-gray-400 text-xl">Texas Hold'em • Telegram Mini App</p>
          </div>

          <button
            onClick={handleStartGame}
            className="px-12 py-6 bg-gradient-to-r from-green-500 to-emerald-600 rounded-2xl font-bold text-2xl shadow-2xl hover:scale-110 transition-all duration-300 animate-bounce-in border-4 border-green-400"
          >
            🃏 Начать игру
          </button>

          {connected && (
            <div className="mt-4 flex items-center gap-2 text-green-400 animate-fade-in">
              <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
              <span>Подключено к серверу</span>
            </div>
          )}

          <div className="mt-12 text-center text-gray-500 animate-fade-in">
            <p className="text-lg">Powered by Telegram Mini Apps</p>
          </div>
        </div>
      ) : (
        <PokerTable
          players={players}
          communityCards={communityCards}
          pot={pot}
          currentPlayerIndex={currentPlayerIndex}
          onFold={handleFold}
          onCall={handleCall}
          onRaise={handleRaise}
        />
      )}
    </div>
  );
}

export default App;
