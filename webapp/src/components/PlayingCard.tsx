interface PlayingCardProps {
  card: string;
  small?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

export function PlayingCard({ card, small = false, className = '', style }: PlayingCardProps) {
  const isHidden = card === '?';
  const isRed = card.includes('♥') || card.includes('♦');

  return (
    <div
      className={`
        card
        ${isHidden ? 'card-back' : ''}
        ${small ? '!w-12 !h-16 !text-lg' : ''}
        ${className}
      `}
      style={style}
    >
      {isHidden ? (
        <div className="text-white/30 text-3xl">🎴</div>
      ) : (
        <div className={`flex flex-col items-center justify-center ${isRed ? 'text-red-500' : 'text-gray-900'}`}>
          <span className="font-bold leading-none">{card}</span>
        </div>
      )}
    </div>
  );
}
