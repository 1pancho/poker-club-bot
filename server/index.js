const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST'],
  },
});

// Game state storage
const games = new Map();
const playerSockets = new Map();

class PokerGame {
  constructor(gameId) {
    this.gameId = gameId;
    this.players = [];
    this.communityCards = [];
    this.pot = 0;
    this.currentPlayerIndex = 0;
    this.phase = 'waiting';
    this.deck = this.createDeck();
  }

  createDeck() {
    const suits = ['♠', '♥', '♦', '♣'];
    const ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'];
    const deck = [];
    for (const suit of suits) {
      for (const rank of ranks) {
        deck.push(rank + suit);
      }
    }
    return this.shuffle(deck);
  }

  shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
  }

  addPlayer(playerId, playerName) {
    if (this.players.length >= 8) {
      return false;
    }
    if (this.players.find(p => p.id === playerId)) {
      return false;
    }
    this.players.push({
      id: playerId,
      name: playerName,
      chips: 1000,
      cards: [],
      bet: 0,
      folded: false,
    });
    return true;
  }

  removePlayer(playerId) {
    const index = this.players.findIndex(p => p.id === playerId);
    if (index !== -1) {
      this.players.splice(index, 1);
      if (this.players.length < 2) {
        this.phase = 'waiting';
      }
    }
  }

  startGame() {
    if (this.players.length < 2) {
      return false;
    }
    this.phase = 'preflop';
    this.deck = this.createDeck();
    this.communityCards = [];
    this.pot = 0;
    this.currentPlayerIndex = 0;

    // Deal cards to players
    this.players.forEach(player => {
      player.cards = [this.deck.pop(), this.deck.pop()];
      player.bet = 0;
      player.folded = false;
    });

    return true;
  }

  performAction(playerId, action, amount = 0) {
    const player = this.players.find(p => p.id === playerId);
    if (!player) return false;

    const currentPlayer = this.players[this.currentPlayerIndex];
    if (currentPlayer.id !== playerId) {
      return false;
    }

    switch (action) {
      case 'fold':
        player.folded = true;
        break;
      case 'call':
        const callAmount = this.getCurrentBet() - player.bet;
        player.chips -= callAmount;
        player.bet += callAmount;
        this.pot += callAmount;
        break;
      case 'raise':
        player.chips -= amount;
        player.bet += amount;
        this.pot += amount;
        break;
    }

    // Move to next player
    this.nextPlayer();

    // Check if round is over
    if (this.isRoundOver()) {
      this.nextPhase();
    }

    return true;
  }

  getCurrentBet() {
    return Math.max(...this.players.map(p => p.bet));
  }

  nextPlayer() {
    do {
      this.currentPlayerIndex = (this.currentPlayerIndex + 1) % this.players.length;
    } while (this.players[this.currentPlayerIndex].folded);
  }

  isRoundOver() {
    const activePlayers = this.players.filter(p => !p.folded);
    if (activePlayers.length === 1) return true;

    const currentBet = this.getCurrentBet();
    return activePlayers.every(p => p.bet === currentBet);
  }

  nextPhase() {
    const phases = ['preflop', 'flop', 'turn', 'river', 'showdown'];
    const currentIndex = phases.indexOf(this.phase);

    if (currentIndex < phases.length - 1) {
      this.phase = phases[currentIndex + 1];

      // Deal community cards
      switch (this.phase) {
        case 'flop':
          this.communityCards.push(this.deck.pop(), this.deck.pop(), this.deck.pop());
          break;
        case 'turn':
        case 'river':
          this.communityCards.push(this.deck.pop());
          break;
        case 'showdown':
          this.determineWinner();
          break;
      }

      // Reset bets
      this.players.forEach(p => p.bet = 0);
      this.currentPlayerIndex = 0;
    }
  }

  determineWinner() {
    // Simplified winner determination - in real game, evaluate poker hands
    const activePlayers = this.players.filter(p => !p.folded);
    if (activePlayers.length > 0) {
      activePlayers[0].chips += this.pot;
    }
    this.pot = 0;
  }

  getState(playerId = null) {
    return {
      gameId: this.gameId,
      players: this.players.map(p => ({
        id: p.id,
        name: p.name,
        chips: p.chips,
        cards: p.id === playerId ? p.cards : ['?', '?'], // Hide other players' cards
        bet: p.bet,
        folded: p.folded,
      })),
      communityCards: this.communityCards,
      pot: this.pot,
      currentPlayerIndex: this.currentPlayerIndex,
      phase: this.phase,
    };
  }
}

// Socket.IO connection handling
io.on('connection', (socket) => {
  console.log(`Client connected: ${socket.id}`);

  socket.on('game:join', ({ gameId, playerId, playerName }) => {
    console.log(`Player ${playerName} joining game ${gameId}`);

    let game = games.get(gameId);
    if (!game) {
      game = new PokerGame(gameId);
      games.set(gameId, game);
    }

    if (game.addPlayer(playerId, playerName)) {
      socket.join(gameId);
      playerSockets.set(playerId, socket.id);

      // Notify all players
      io.to(gameId).emit('player:joined', { id: playerId, name: playerName });

      // Send game state to all players
      game.players.forEach(player => {
        const playerSocket = io.sockets.sockets.get(playerSockets.get(player.id));
        if (playerSocket) {
          playerSocket.emit('game:state', game.getState(player.id));
        }
      });

      // Auto-start if enough players
      if (game.players.length >= 2 && game.phase === 'waiting') {
        setTimeout(() => {
          game.startGame();
          game.players.forEach(player => {
            const playerSocket = io.sockets.sockets.get(playerSockets.get(player.id));
            if (playerSocket) {
              playerSocket.emit('game:state', game.getState(player.id));
            }
          });
        }, 2000);
      }
    } else {
      socket.emit('error', { message: 'Cannot join game' });
    }
  });

  socket.on('game:action', ({ action, amount }) => {
    // Find player's game
    for (const [gameId, game] of games) {
      const playerId = Array.from(playerSockets.entries())
        .find(([_, sid]) => sid === socket.id)?.[0];

      if (playerId && game.players.find(p => p.id === playerId)) {
        if (game.performAction(playerId, action, amount)) {
          // Send updated state to all players
          game.players.forEach(player => {
            const playerSocket = io.sockets.sockets.get(playerSockets.get(player.id));
            if (playerSocket) {
              playerSocket.emit('game:state', game.getState(player.id));
            }
          });
        }
        break;
      }
    }
  });

  socket.on('disconnect', () => {
    console.log(`Client disconnected: ${socket.id}`);

    // Remove player from games
    const playerId = Array.from(playerSockets.entries())
      .find(([_, sid]) => sid === socket.id)?.[0];

    if (playerId) {
      for (const [gameId, game] of games) {
        if (game.players.find(p => p.id === playerId)) {
          game.removePlayer(playerId);
          io.to(gameId).emit('player:left', { id: playerId });

          // Send updated state
          game.players.forEach(player => {
            const playerSocket = io.sockets.sockets.get(playerSockets.get(player.id));
            if (playerSocket) {
              playerSocket.emit('game:state', game.getState(player.id));
            }
          });

          // Clean up empty games
          if (game.players.length === 0) {
            games.delete(gameId);
          }
        }
      }
      playerSockets.delete(playerId);
    }
  });
});

// REST API endpoints
app.get('/health', (req, res) => {
  res.json({ status: 'ok', games: games.size });
});

app.get('/games', (req, res) => {
  const gamesList = Array.from(games.values()).map(g => ({
    gameId: g.gameId,
    players: g.players.length,
    phase: g.phase,
  }));
  res.json(gamesList);
});

const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
  console.log(`🎰 Poker WebSocket server running on port ${PORT}`);
});
