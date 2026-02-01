import { useEffect, useRef, useState, useCallback } from 'react';

export interface VisualUpdatePayload {
  intent: string;
  energy: number;
  shape: 'sphere' | 'cube' | 'vortex' | 'cloud';
  color_code: string;
}

export interface AetherResponse {
  type: string;
  payload: VisualUpdatePayload;
  transcript_preview?: string;
  text_content?: string;
}

export const useAetherBus = (url: string) => {
  const ws = useRef<WebSocket | null>(null);
  const [lastResponse, setLastResponse] = useState<AetherResponse | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  const connect = useCallback(() => {
    const socket = new WebSocket(url);
    ws.current = socket;

    socket.onopen = () => {
      setIsConnected(true);
      console.log('Connected to AetherBus');
      // Get initial state
      socket.send(JSON.stringify({ type: 'GET_IDLE_STATE' }));
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'VISUAL_UPDATE') {
          setLastResponse(data);
        }
      } catch (e) {
        console.error('Failed to parse Aether message', e);
      }
    };

    socket.onclose = () => {
      setIsConnected(false);
      console.log('AetherBus disconnected, retrying...');
      setTimeout(connect, 3000);
    };
  }, [url]);

  useEffect(() => {
    connect();
    return () => ws.current?.close();
  }, [connect]);

  const sendMockTranscription = (text: string) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type: 'MOCK_TRANSCRIPTION', text }));
    }
  };

  const sendAudioChunk = (chunk: Int16Array) => {
      if (ws.current?.readyState === WebSocket.OPEN) {
          ws.current.send(chunk.buffer);
      }
  };

  return { lastResponse, isConnected, sendMockTranscription, sendAudioChunk };
};
