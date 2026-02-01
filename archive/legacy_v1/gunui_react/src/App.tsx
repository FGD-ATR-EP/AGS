import { useEffect, useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { useMachine } from '@xstate/react';
import { ritualMachine } from './machines/ritualMachine';
import { useAetherBus } from './hooks/useAetherBus';
import { useVAD } from './hooks/useVAD';
import VisualEchoNode from './components/VisualEchoNode';
import ActuatorButton from './components/ActuatorButton';
import MockInput from './components/MockInput';

const App = () => {
  const [state, send] = useMachine(ritualMachine);
  const { lastResponse, isConnected, sendMockTranscription } = useAetherBus('ws://localhost:8000/ws/v2/stream');

  const onSpeechEnd = () => {
    if (state.matches('listening')) {
      send({ type: 'COMMIT' });
    }
  };

  const vad = useVAD(onSpeechEnd);

  useEffect(() => {
    if (state.matches('listening')) {
      vad.start();
    } else {
      vad.pause();
    }
  }, [state.value, vad]);

  // Handle backend responses
  useEffect(() => {
      if (lastResponse && state.matches('processing')) {
          send({ type: 'COMPLETE' });
      }
  }, [lastResponse, state.value]);

  const visualProps = useMemo(() => {
    if (!lastResponse) return { shape: 'sphere' as const, color: '#06b6d4', energy: 0.1 };
    return {
      shape: (lastResponse.payload.shape || 'sphere') as any,
      color: lastResponse.payload.color_code || '#FFFFFF',
      energy: lastResponse.payload.energy || 0.1
    };
  }, [lastResponse]);

  const handleActuatorClick = () => {
    if (state.matches('idle')) {
      send({ type: 'WAKE' });
    } else if (state.matches('listening')) {
      send({ type: 'COMMIT' });
    }
  };

  const handleMockSend = (text: string) => {
      send({ type: 'COMMIT' });
      sendMockTranscription(text);
  };

  return (
    <div className="relative w-full h-full bg-[#050505] overflow-hidden">
      {/* 3D Visual Layer */}
      <div className="absolute inset-0 z-0">
        <Canvas camera={{ position: [0, 0, 5], fov: 45 }}>
          <color attach="background" args={['#050505']} />
          <ambientLight intensity={0.5} />
          <VisualEchoNode
            shape={visualProps.shape}
            color={visualProps.color}
            energy={visualProps.energy}
          />
        </Canvas>
      </div>

      {/* Interface Overlays */}
      <div className="absolute top-8 left-8 pointer-events-none select-none">
        <h1 className="text-white/30 font-bold tracking-[0.3em] text-sm uppercase">Aetherium Genesis</h1>
        <div className="flex items-center gap-2 mt-2">
            <div className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-cyan-500 shadow-[0_0_8px_cyan]' : 'bg-red-500'}`} />
            <span className="text-[10px] text-white/20 font-mono tracking-widest">{isConnected ? 'UPLINK ACTIVE' : 'OFFLINE'}</span>
        </div>
      </div>

      {lastResponse?.transcript_preview && (
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 translate-y-32 text-center pointer-events-none select-none">
          <p className="text-cyan-400/40 font-mono text-[10px] tracking-widest uppercase italic">"{lastResponse.transcript_preview}"</p>
        </div>
      )}

      {lastResponse?.text_content && (
          <div className="absolute bottom-40 left-1/2 -translate-x-1/2 w-full max-w-lg text-center px-6 pointer-events-none select-none">
              <p className="text-white/70 font-mono text-xs leading-relaxed tracking-wider">{lastResponse.text_content}</p>
          </div>
      )}

      <ActuatorButton state={state.value as string} onClick={handleActuatorClick} />

      <MockInput onSend={handleMockSend} />

      {/* Decorative elements */}
      <div className="absolute top-12 right-12 text-white/10 font-mono text-[8px] flex flex-col items-end gap-1 pointer-events-none">
          <span>PHI_COEFFICIENT: 0.618</span>
          <span>ENTROPY_INDEX: {(visualProps.energy * 10).toFixed(4)}</span>
      </div>
    </div>
  );
};

export default App;
