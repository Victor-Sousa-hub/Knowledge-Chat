"use client";

import { useState } from "react";

interface Props {
  onSession: (sessionId: string) => void;
}

export default function SessionGate({ onSession }: Props) {
  const [existingId, setExistingId] = useState("");
  const [error, setError] = useState("");

  function handleNew() {
    onSession(crypto.randomUUID());
  }

  function handleExisting() {
    const trimmed = existingId.trim();
    const uuidRegex =
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(trimmed)) {
      setError("ID de sessão inválido. Use o formato UUID.");
      return;
    }
    onSession(trimmed);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") handleExisting();
  }

  return (
    <div className="flex h-screen bg-zinc-950 text-zinc-100 items-center justify-center">
      <div className="w-full max-w-md px-6 flex flex-col gap-8">
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <div className="rounded-full bg-zinc-800 p-4">
              <ChatIcon />
            </div>
          </div>
          <h1 className="text-2xl font-semibold text-zinc-100">Knowledge Chat</h1>
          <p className="text-zinc-400 text-sm mt-2">
            Inicie uma nova sessão ou continue uma existente.
          </p>
        </div>

        <button
          onClick={handleNew}
          className="w-full rounded-xl bg-zinc-100 hover:bg-white text-zinc-900 px-4 py-3 font-medium text-sm transition-colors"
        >
          Nova sessão
        </button>

        <div className="relative flex items-center">
          <div className="flex-grow border-t border-zinc-700" />
          <span className="mx-3 text-xs text-zinc-500">ou</span>
          <div className="flex-grow border-t border-zinc-700" />
        </div>

        <div className="flex flex-col gap-3">
          <label className="text-sm text-zinc-400">Código da sessão existente</label>
          <input
            type="text"
            value={existingId}
            onChange={(e) => {
              setExistingId(e.target.value);
              setError("");
            }}
            onKeyDown={handleKeyDown}
            placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            className="rounded-xl bg-zinc-800 border border-zinc-700 focus:border-zinc-500 focus:outline-none px-4 py-3 text-sm text-zinc-100 placeholder:text-zinc-500 font-mono"
          />
          {error && <p className="text-xs text-red-400">{error}</p>}
          <button
            onClick={handleExisting}
            disabled={!existingId.trim()}
            className="w-full rounded-xl bg-zinc-700 hover:bg-zinc-600 disabled:opacity-40 disabled:cursor-not-allowed px-4 py-3 font-medium text-sm transition-colors"
          >
            Entrar na sessão
          </button>
        </div>
      </div>
    </div>
  );
}

function ChatIcon() {
  return (
    <svg
      width="28"
      height="28"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="text-zinc-500"
    >
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
  );
}
