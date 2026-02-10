import { PlayingCard } from './PlayingCard';

interface PlayerSeatProps {
  name: string;
  chips: number;
  cards: string[];
  isActive?: boolean;
  bet?: number;
  position: 'top' | 'left' | 'right' | 'bottom';
}

export function PlayerSeat({ name, chips, cards, isActive = false, bet = 0, position }: PlayerSeatProps) {
  const positionClasses = {
    top: 'top-4',
    bottom: 'bottom-4',
    left: 'left-4',
    right: 'right-4'
  };

  const alignmentClasses = {
    top: 'items-center',
    bottom: 'items-center',
    left: 'items-start',
    right: 'items-end'
  };

  return (
    <div className={`absolute ${positionClasses[position]} flex flex-col gap-2 ${alignmentClasses[position]} animate-fade-in`}>
      {/* Player Info */}
      <div className={`
        bg-gray-800/90 backdrop-blur-sm rounded-lg px-4 py-2
        border-2 transition-all duration-300
        ${isActive ? 'border-yellow-400 shadow-lg shadow-yellow-400/50' : 'border-gray-700'}
      `}>
        <div className="flex items-center gap-2 mb-1">
          <div className={`w-2 h-2 rounded-full ${isActive ? 'bg-green-400 animate-pulse' : 'bg-gray-500'}`} />
          <span className="font-semibold text-sm">{name}</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="text-yellow-400 text-lg">💰</span>
          <span className="text-white font-bold">${chips.toLocaleString()}</span>
        </div>
      </div>

      {/* Cards */}
      <div className="flex gap-1">
        {cards.map((card, i) => (
          <PlayingCard key={i} card={card} small className="animate-slide-in" />
        ))}
      </div>

      {/* Bet */}
      {bet > 0 && (
        <div className="chip bg-red-600 animate-bounce-in">
          <span className="text-white">💸</span>
          <span className="text-white">${bet}</span>
        </div>
      )}
    </div>
  );
}
