import { PlayerSeat } from './PlayerSeat';
import { CommunityCards } from './CommunityCards';
import { PotDisplay } from './PotDisplay';
import { ActionButton } from './ActionButton';

interface Player {
  name: string;
  chips: number;
  cards: string[];
  bet: number;
}

interface PokerTableProps {
  players: Player[];
  communityCards: string[];
  pot: number;
  currentPlayerIndex: number;
  onFold: () => void;
  onCall: () => void;
  onRaise: () => void;
}

export function PokerTable({
  players,
  communityCards,
  pot,
  currentPlayerIndex,
  onFold,
  onCall,
  onRaise
}: PokerTableProps) {
  const positions: ('top' | 'left' | 'right' | 'bottom')[] = ['bottom', 'left', 'top', 'right'];

  return (
    <div className="relative w-full h-screen flex items-center justify-center p-8">
      {/* Poker Table */}
      <div className="poker-table w-[900px] h-[600px] relative">
        {/* Players */}
        {players.map((player, index) => (
          <PlayerSeat
            key={index}
            name={player.name}
            chips={player.chips}
            cards={player.cards}
            bet={player.bet}
            position={positions[index]}
            isActive={index === currentPlayerIndex}
          />
        ))}

        {/* Pot */}
        <PotDisplay amount={pot} />

        {/* Community Cards */}
        <CommunityCards cards={communityCards} />
      </div>

      {/* Action Buttons */}
      <div className="fixed bottom-8 left-1/2 -translate-x-1/2 flex gap-4 bg-gray-900/90 backdrop-blur-sm px-8 py-4 rounded-2xl border-2 border-gray-700 shadow-2xl">
        <ActionButton onClick={onFold} variant="danger">
          ❌ Fold
        </ActionButton>
        <ActionButton onClick={onCall} variant="primary">
          ✅ Call $50
        </ActionButton>
        <ActionButton onClick={onRaise} variant="success">
          ⬆️ Raise
        </ActionButton>
      </div>
    </div>
  );
}
