export interface Product {
  id: string;
  title: string;
  price: number;
  url: string;
  image: string;
}

export interface IntentState {
  userInput: string;
  products: Product[];
  isLoading: boolean;
  error: string | null;
  setUserInput: (input: string) => void;
  parseIntent: (input: string) => Promise<void>;
  clearError: () => void;
  clearProducts: () => void;
} 