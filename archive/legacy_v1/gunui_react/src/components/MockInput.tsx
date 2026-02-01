import React, { useState, useEffect } from 'react';

interface MockInputProps {
  onSend: (text: string) => void;
}

const MockInput: React.FC<MockInputProps> = ({ onSend }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [text, setText] = useState('');

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.shiftKey && e.key === 'M') {
        setIsVisible(!isVisible);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isVisible]);

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 border border-cyan-500 p-6 rounded-lg w-full max-w-md shadow-[0_0_20px_rgba(6,182,212,0.3)]">
        <h2 className="text-cyan-400 font-mono text-sm mb-4 tracking-widest uppercase">Subsurface Transmission</h2>
        <input
          autoFocus
          className="w-full bg-black border-b border-cyan-800 text-cyan-500 font-mono p-2 outline-none focus:border-cyan-400 transition-colors"
          placeholder="Enter intent..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              onSend(text);
              setText('');
              setIsVisible(false);
            }
            if (e.key === 'Escape') setIsVisible(false);
          }}
        />
        <div className="mt-4 flex justify-between text-[10px] text-gray-500 font-mono">
          <span>CTRL+SHIFT+M to hide</span>
          <span>ENTER to commit</span>
        </div>
      </div>
    </div>
  );
};

export default MockInput;
