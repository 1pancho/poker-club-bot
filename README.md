# 🎰 Poker Club Bot

<div align="center">

![Poker](https://img.shields.io/badge/Game-Texas_Hold'em-success)
![Telegram](https://img.shields.io/badge/Platform-Telegram-blue)
![Python](https://img.shields.io/badge/Python-3.12+-blue)
![React](https://img.shields.io/badge/React-19-61dafb)
![Node.js](https://img.shields.io/badge/Node.js-20+-green)

**Multiplayer Texas Hold'em Poker for Telegram with beautiful Mini App UI**

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Deployment](DEPLOY.md)

</div>

---

## 🎮 Features

### 🎯 Core Gameplay
- ♠️ Full Texas Hold'em poker implementation
- 🎴 Complete poker hand evaluation (Royal Flush to High Card)
- 💰 Betting rounds: Preflop, Flop, Turn, River
- 🏆 Automatic winner determination
- 👥 Support for 2-8 players per table

### 🎨 Beautiful Mini App
- 🎭 Stunning poker table UI with felt-green design
- 🃏 Animated playing cards with suits
- ⚡ Real-time game updates via WebSocket
- 📱 Mobile-optimized responsive design
- 🎯 Haptic feedback for actions
- 🌗 Dark theme integrated with Telegram

### 🤖 Telegram Bot
- 👤 Player profiles with statistics
- 💎 Virtual chips and rating system
- 🎁 Daily bonus system
- 🏆 Leaderboard
- 📊 Win rate and game history tracking

### 🌐 Real-time Multiplayer
- 🔌 WebSocket server for live games
- 🔄 Instant game state synchronization
- 👥 Player join/leave notifications
- 🎲 Auto-start when enough players join

## 🏗️ Architecture

\`\`\`
┌─────────────────────────────────────────────────────────────┐
│                     Telegram Platform                        │
└────────────────┬────────────────────────────────────────────┘
                 │
       ┌─────────┴──────────┐
       │                    │
  ┌────▼─────┐       ┌─────▼──────┐
  │   Bot    │       │  Mini App  │
  │ (Python) │       │  (React)   │
  └────┬─────┘       └─────┬──────┘
       │                   │
       │              ┌────▼──────────┐
       │              │   WebSocket   │
       │              │    Server     │
       │              │   (Node.js)   │
       │              └────┬──────────┘
       │                   │
  ┌────▼───────────────────▼──────┐
  │    SQLite Database            │
  │  (Players, Games, Stats)      │
  └───────────────────────────────┘
\`\`\`

### Tech Stack

**Backend:**
- Python 3.12+ (Telegram Bot)
- python-telegram-bot library
- SQLAlchemy ORM
- Node.js 20+ (WebSocket Server)
- Socket.IO for real-time communication
- Express for REST API

**Frontend:**
- React 19 with TypeScript
- Vite 7 (build tool)
- Tailwind CSS 4
- Telegram WebApp SDK (@twa-dev/sdk)
- Socket.IO Client

## 🚀 Quick Start

### Prerequisites
\`\`\`bash
# Install Node.js 20+ (using nvm)
nvm install 20
nvm use 20

# Install Python 3.12+
python3 --version
\`\`\`

### 1. Clone & Setup

\`\`\`bash
git clone https://github.com/1pancho/poker-club-bot.git
cd poker-club-bot

# Install Python dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
nano .env  # Add BOT_TOKEN and WEBAPP_URL
\`\`\`

### 2. Run Telegram Bot

\`\`\`bash
python bot.py
\`\`\`

### 3. Run WebSocket Server

\`\`\`bash
cd server
npm install
npm start
\`\`\`

Server runs on port 3001.

### 4. Run Mini App (Development)

\`\`\`bash
cd webapp
npm install
npm run dev
\`\`\`

App opens at http://localhost:5173

### 5. Build for Production

\`\`\`bash
cd webapp
npm run build
\`\`\`

Build output in \`webapp/dist/\`

## 📦 Project Structure

\`\`\`
poker-club-bot/
├── bot.py                  # Telegram bot main file
├── poker_engine.py         # Texas Hold'em game logic
├── database.py             # Database models & queries
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
│
├── server/                 # WebSocket server
│   ├── index.js           # Socket.IO server
│   └── package.json       # Node dependencies
│
└── webapp/                 # Mini App frontend
    ├── src/
    │   ├── components/    # React components
    │   ├── services/      # WebSocket & Telegram services
    │   ├── hooks/         # Custom React hooks
    │   └── App.tsx        # Main app component
    └── package.json
\`\`\`

## 🎯 Game Rules - Texas Hold'em

1. **Blinds**: Small and big blind posted before cards are dealt
2. **Hole Cards**: Each player gets 2 private cards
3. **Betting Rounds**:
   - **Preflop**: After hole cards
   - **Flop**: 3 community cards revealed
   - **Turn**: 4th community card revealed
   - **River**: 5th community card revealed
4. **Showdown**: Best 5-card hand wins

### Hand Rankings (High to Low)
1. 🏆 Royal Flush
2. 💎 Straight Flush
3. 🎯 Four of a Kind
4. 🎭 Full House
5. ♦️ Flush
6. ⚡ Straight
7. 🎲 Three of a Kind
8. 🎪 Two Pair
9. 🎴 One Pair
10. 🃏 High Card

## 🌐 Deployment

See [DEPLOY.md](DEPLOY.md) for detailed deployment instructions.

**Components to deploy:**
1. ✅ Telegram Bot (Python) - systemd service on server
2. ✅ WebSocket Server (Node.js) - PM2 process manager
3. ✅ Mini App (React) - GitHub Pages or Nginx
4. ✅ SSL Certificate - Let's Encrypt (required for Mini Apps)

## 🔧 Configuration

### Environment Variables

**Bot (.env):**
\`\`\`env
BOT_TOKEN=your_telegram_bot_token
WEBAPP_URL=https://your-domain.com/
\`\`\`

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

---

<div align="center">

**Made with ❤️ by Claude & 1pancho**

⭐ Star this repo if you like it! ⭐

</div>
