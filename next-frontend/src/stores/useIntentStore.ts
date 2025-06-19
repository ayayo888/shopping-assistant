import { create } from 'zustand';
import type { IntentState, Product } from '@/types';

export const useIntentStore = create<IntentState>((set) => ({
  userInput: '',
  products: [],
  isLoading: false,
  error: null,
  setUserInput: (input) => set({ userInput: input }),
  clearError: () => set({ error: null }),
  clearProducts: () => set({ products: [] }),
  parseIntent: async (input) => {
    set({ isLoading: true, error: null, products: [] });
    try {
      const response = await fetch('/api/parse-intent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: input }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to parse intent');
      }

      const data: Product[] = await response.json();
      
      set({ products: data, isLoading: false });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'An unknown error occurred', isLoading: false });
    }
  },
})); 