interface PotDisplayProps {
  amount: number;
}

export function PotDisplay({ amount }: PotDisplayProps) {
  return (
    <div className="absolute left-1/2 top-1/3 -translate-x-1/2 -translate-y-1/2">
      <div className="chip bg-gradient-to-br from-yellow-500 to-yellow-600 text-white text-xl px-6 py-3 shadow-2xl border-2 border-yellow-400 animate-pulse">
        <span>🏆</span>
        <span className="font-bold">Pot: ${amount.toLocaleString()}</span>
      </div>
    </div>
  );
}
