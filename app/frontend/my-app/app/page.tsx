"use client";

import { useState, useEffect } from "react";
import SessionGate from "@/app/components/SessionGate";
import ChatInterface from "@/app/components/ChatInterface";

const SESSION_KEY = "knowledge_chat_session_id";

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem(SESSION_KEY);
    if (saved) setSessionId(saved);
    setReady(true);
  }, []);

  function handleSession(id: string) {
    localStorage.setItem(SESSION_KEY, id);
    setSessionId(id);
  }

  function handleNewSession() {
    localStorage.removeItem(SESSION_KEY);
    setSessionId(null);
  }

  if (!ready) return null;

  if (!sessionId) {
    return <SessionGate onSession={handleSession} />;
  }

  return <ChatInterface sessionId={sessionId} onNewSession={handleNewSession} />;
}
