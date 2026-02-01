import { useMicVAD } from "@ricky0123/vad-react";

export const useVAD = (onSpeechEnd: (text: string) => void) => {
  const vad = useMicVAD({
    onSpeechEnd: () => {
        // In a real scenario, we'd transcribe here.
        // For the mock, we just trigger the callback.
        // We'll use the audio energy as a proxy for visual feedback if needed.
        onSpeechEnd("MOCKED_VOICE_INPUT");
    },
    onFrameProcessed: () => {
        // can use probabilities.isSpeech to drive visual energy
    },
    startOnLoad: false,
  });

  return vad;
};
