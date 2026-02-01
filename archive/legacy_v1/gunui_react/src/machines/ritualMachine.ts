import { createMachine } from 'xstate';

export const ritualMachine = createMachine({
  id: 'ritual',
  initial: 'idle',
  states: {
    idle: {
      on: {
        WAKE: 'listening'
      }
    },
    listening: {
      on: {
        COMMIT: 'processing',
        CANCEL: 'idle',
        SPEAKING: 'listening' // Useful for visual feedback
      }
    },
    processing: {
      on: {
        COMPLETE: 'idle',
        ERROR: 'idle'
      }
    }
  }
});
