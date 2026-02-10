import { PlayingCard } from './PlayingCard';

interface CommunityCardsProps {
  cards: string[];
}

export function CommunityCards({ cards }: CommunityCardsProps) {
  return (
    <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
      <div className="flex flex-col items-center gap-4">
        {/* Community Cards */}
        <div className="flex gap-2 bg-gray-900/50 backdrop-blur-sm rounded-xl p-4 border-2 border-gray-700">
          {cards.map((card, i) => (
            <PlayingCard
              key={i}
              card={card}
              className="animate-bounce-in"
              style={{ animationDelay: `${i * 0.1}s` } as React.CSSProperties}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
