import { IntentInputForm } from "@/components/IntentInputForm";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-start p-24">
      <div className="w-full max-w-3xl">
        <IntentInputForm />
      </div>
    </main>
  );
}
