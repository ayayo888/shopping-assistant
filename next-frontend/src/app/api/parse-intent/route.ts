import { NextResponse } from 'next/server';
import OpenAI from 'openai';
import type { Product } from '@/types';

// Initialize the OpenAI client with OpenRouter configuration
const openrouter = new OpenAI({
  baseURL: 'https://openrouter.ai/api/v1',
  apiKey: process.env.OPENROUTER_API_KEY,
  defaultHeaders: {
    'HTTP-Referer': 'https://github.com/ayayo888/shopping-assistant',
    'X-Title': 'Shopping Assistant',
  },
});

const systemPrompt = `
You are an intelligent shopping assistant. Your task is to analyze the user's input text and determine their shopping intent.

Your response MUST be a valid JSON object that conforms to the following TypeScript interface:
interface Response {
  products: Product[];
}

Each product object must conform to this interface:
interface Product {
  id: string; // A unique identifier, can be a product ID from URL or a random string.
  title: string;
  price: number;
  url: string; // The original URL if provided, or a placeholder URL.
  image: string; // A valid image URL. For real products, find one. Otherwise, use "https://via.placeholder.com/300x300.png?text=Product+Image".
}

- If the input is a valid URL, extract the product details.
- If the input is a product name or description, imagine a realistic product that matches.
- If you cannot identify a clear shopping intent or find any relevant product, you MUST return a JSON object with an empty products array: { "products": [] }.
- Do not include any explanations, apologies, or extra text outside of the JSON object in your response. Just the JSON.
`;

export async function POST(request: Request) {
  console.log("--- API Route Handler Called ---");
  console.log("Is OPENROUTER_API_KEY present?", !!process.env.OPENROUTER_API_KEY);

  try {
    const body = await request.json();
    const { text } = body;
    console.log("Received user input:", text);

    if (!text || typeof text !== 'string') {
      return NextResponse.json({ detail: 'Invalid input' }, { status: 400 });
    }

    const completion = await openrouter.chat.completions.create({
      model: 'openai/gpt-4o-mini',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: text },
      ],
      response_format: { type: 'json_object' },
    });

    const jsonResponse = completion.choices[0]?.message?.content;
    console.log("Raw response string from LLM:", jsonResponse);

    if (!jsonResponse) {
      console.log("LLM returned no content. Responding with empty array.");
      return NextResponse.json([]);
    }

    try {
        const responseObject: { products: Product[] } = JSON.parse(jsonResponse);
        console.log("Successfully parsed LLM response:", responseObject);
        return NextResponse.json(responseObject.products);
    } catch (e) {
        console.error("Failed to parse JSON response from LLM:", e);
        console.log("LLM response did not conform to expected JSON object with a 'products' key. Responding with empty array.");
        return NextResponse.json([]);
    }

  } catch (error) {
    console.error("--- ERROR in API Route ---", error);
    return NextResponse.json({ detail: 'Internal Server Error' }, { status: 500 });
  }
} 