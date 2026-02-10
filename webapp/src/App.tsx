import { useState } from 'react'
import './index.css'

// Simple Playing Card Component
function PlayingCard({ card, small = false }: { card: string; small?: boolean }) {
  const isHidden = card === '?'
  const isRed = card.includes('♥') || card.includes('♦')

  return (
    <div className={`card ${isHidden ? 'card-back' : ''} ${small ? '!w-12 !h-16 !text-lg' : ''}`}>
      {isHidden ? (
        <div className="text-white/30">🎴</div>
      ) : (
        <div className={`flex flex-col items-center ${isRed ? 'text-red-500' : 'text-gray-900'}`}>
          <span className="font-bold">{card}</span>
        </div>
      )}
    </div>
  )
}

// Poker Table Component
function PokerTable() {
  const [pot] = useState(200)
  const [communityCards] = useState(['A♥', 'K♦', 'Q♣'])
  const [currentBet] = useState(50)

  const players = [
    { id: 1, name: 'Вы', chips: 1000, cards: ['A♠', 'K♠'], position: 'bottom-4 left-1/2 -translate-x-1/2' },
    { id: 2, name: 'Игрок 2', chips: 850, cards: ['?', '?'], position: 'top-4 left-1/4' },
    { id: 3, name: 'Игрок 3', chips: 1200, cards: ['?', '?'], position: 'top-4 right-1/4' },
    { id: 4, name: 'Игрок 4', chips: 600, cards: ['?', '?'], position: 'bottom-4 right-8' },
  ]

  return (
    <div className="w-full max-w-4xl">
      <div className="relative w-full h-[500px] poker-table">
        {/* Community Cards */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex gap-2">
          {communityCards.map((card, i) => (
            <PlayingCard key={i} card={card} />
          ))}
          <PlayingCard card="?" />
          <PlayingCard card="?" />
        </div>

        {/* Pot */}
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-8">
          <div className="chip bg-yellow-500 text-gray-900">
            💰 ${pot}
          </div>
        </div>

        {/* Players */}
        {players.map((player) => (
          <div key={player.id} className={`absolute ${player.position}`}>
            <div className="bg-gray-800/90 rounded-xl p-3 backdrop-blur-sm border border-gray-700 min-w-[150px]">
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-sm">{player.name}</span>
                <span className="chip bg-blue-500 text-xs">${player.chips}</span>
              </div>

              <div className="flex gap-1 justify-center">
                {player.cards.map((card, i) => (
                  <div key={i} className="scale-75">
                    <PlayingCard card={card} small />
                  </div>
                ))}
              </div>

              {player.id === 1 && (
                <div className="mt-2 flex gap-1 text-xs">
                  <button className="flex-1 bg-red-500 hover:bg-red-600 rounded py-1 font-semibold transition">
                    Fold
                  </button>
                  <button className="flex-1 bg-green-500 hover:bg-green-600 rounded py-1 font-semibold transition">
                    Call ${currentBet}
                  </button>
                  <button className="flex-1 bg-yellow-500 hover:bg-yellow-600 rounded py-1 font-semibold transition text-gray-900">
                    Raise
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 flex justify-center gap-4 text-sm">
        <div className="chip bg-purple-500">🎲 Flop</div>
        <div className="chip bg-orange-500">💵 Bet: ${currentBet}</div>
      </div>
    </div>
  )
}

// Main App
function App() {
  const [gameStarted, setGameStarted] = useState(false)

  return (
    <div className="min-h-screen p-4 flex flex-col items-center justify-center">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
          🎰 Poker Club
        </h1>
        <p className="text-gray-400">Texas Hold'em • Mini App</p>
      </div>

      {!gameStarted ? (
        <button
          onClick={() => setGameStarted(true)}
          className="px-8 py-4 bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl font-bold text-lg shadow-lg hover:scale-105 transition-all"
        >
          🃏 Start Game
        </button>
      ) : (
        <PokerTable />
      )}

      <div className="mt-8 text-center text-sm text-gray-500">
        <p>Powered by Telegram Mini Apps</p>
      </div>
    </div>
  )
}

export default App
