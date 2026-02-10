interface ActionButtonProps {
  onClick: () => void;
  children: React.ReactNode;
  variant?: 'primary' | 'danger' | 'success';
  disabled?: boolean;
}

export function ActionButton({ onClick, children, variant = 'primary', disabled = false }: ActionButtonProps) {
  const variantClasses = {
    primary: 'bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white',
    danger: 'bg-red-600 hover:bg-red-700 active:bg-red-800 text-white',
    success: 'bg-green-600 hover:bg-green-700 active:bg-green-800 text-white'
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        px-6 py-3 rounded-lg font-bold text-lg
        transition-all duration-200 transform
        hover:scale-105 active:scale-95
        disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100
        shadow-lg hover:shadow-xl
        ${variantClasses[variant]}
      `}
    >
      {children}
    </button>
  );
}
