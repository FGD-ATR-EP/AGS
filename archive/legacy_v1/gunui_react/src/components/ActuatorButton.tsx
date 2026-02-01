import React from 'react';

interface ActuatorButtonProps {
  state: string;
  onClick: () => void;
}

const ActuatorButton: React.FC<ActuatorButtonProps> = ({ state, onClick }) => {
  return (
    <div className="fixed bottom-12 left-1/2 -translate-x-1/2 z-40">
      <button
        onClick={onClick}
        className={`
          relative w-20 h-20 rounded-full flex items-center justify-center transition-all duration-700
          ${state === 'idle' ? 'bg-black border border-gray-800' :
            state === 'listening' ? 'bg-cyan-500/10 border border-cyan-400 shadow-[0_0_30px_rgba(34,211,238,0.4)]' :
            'bg-white/10 border border-white animate-pulse'}
        `}
      >
        {/* Inner Core */}
        <div
          className={`
            w-6 h-6 rounded-sm transition-all duration-500
            ${state === 'idle' ? 'bg-gray-700' :
              state === 'listening' ? 'bg-cyan-400 rotate-45 scale-125' :
              'bg-white rotate-90 scale-150'}
          `}
        />

        {/* Glow Ring for Listening */}
        {state === 'listening' && (
          <div className="absolute inset-0 rounded-full border border-cyan-400 animate-ping opacity-20" />
        )}
      </button>

      <div className="text-center mt-4 font-mono text-[10px] tracking-widest text-gray-500 uppercase">
        {state === 'idle' ? 'Void Standby' : state === 'listening' ? 'Listening' : 'Processing'}
      </div>
    </div>
  );
};

export default ActuatorButton;
