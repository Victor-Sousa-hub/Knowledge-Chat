"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import {
  sendMessage,
  uploadDocument,
  getSessionDocuments,
  terminateSession,
  SessionDocument,
  SourceReference,
} from "@/app/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: SourceReference[];
}

interface Props {
  sessionId: string;
  onNewSession: () => void;
}

export default function ChatInterface({ sessionId, onNewSession }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [documents, setDocuments] = useState<SessionDocument[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  function handleCopySession() {
    navigator.clipboard.writeText(sessionId).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const refreshDocuments = useCallback(async () => {
    try {
      const result = await getSessionDocuments(sessionId);
      setDocuments(result.documents);
    } catch {
      // silently fail if session has no docs yet
    }
  }, [sessionId]);

  useEffect(() => {
    refreshDocuments();
  }, [refreshDocuments]);

  async function handleSend() {
    const question = input.trim();
    if (!question || loading) return;

    setInput("");
    setError(null);
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);

    try {
      const res = await sendMessage(sessionId, question);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.answer, sources: res.sources },
      ]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erro ao enviar mensagem.");
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    e.target.value = "";

    setUploading(true);
    setError(null);
    try {
      await uploadDocument(sessionId, file);
      await refreshDocuments();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao enviar arquivo.");
    } finally {
      setUploading(false);
    }
  }

  async function handleTerminate() {
    if (!confirm("Encerrar sessão e remover todos os documentos?")) return;
    try {
      await terminateSession(sessionId);
      setDocuments([]);
      setMessages([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao encerrar sessão.");
    }
  }

  function formatFileSize(bytes: number) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  return (
    <div className="flex h-screen bg-zinc-950 text-zinc-100">
      {/* Sidebar */}
      <aside className="w-64 flex flex-col border-r border-zinc-800 bg-zinc-900 shrink-0">
        <div className="p-4 border-b border-zinc-800">
          <h1 className="text-sm font-semibold text-zinc-100 tracking-wide uppercase">
            Knowledge Chat
          </h1>
          <div className="mt-2 flex flex-col gap-1">
            <span className="text-xs text-zinc-500">ID da sessão</span>
            <div className="flex items-center gap-1.5">
              <span className="text-xs text-zinc-400 font-mono break-all leading-snug flex-1">
                {sessionId}
              </span>
              <button
                onClick={handleCopySession}
                title="Copiar ID da sessão"
                className="shrink-0 rounded p-1 text-zinc-500 hover:text-zinc-200 hover:bg-zinc-700 transition-colors"
              >
                {copied ? <CheckIcon /> : <CopyIcon />}
              </button>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-medium text-zinc-400 uppercase tracking-wide">
              Documentos
            </span>
            <span className="text-xs text-zinc-500">{documents.length}</span>
          </div>

          {documents.length === 0 ? (
            <p className="text-xs text-zinc-600 italic">Nenhum documento na sessão.</p>
          ) : (
            <ul className="space-y-2">
              {documents.map((doc, i) => (
                <li
                  key={i}
                  className="flex flex-col gap-0.5 rounded-lg bg-zinc-800 px-3 py-2"
                >
                  <span className="text-xs text-zinc-200 truncate" title={doc.name}>
                    {doc.name}
                  </span>
                  <span className="text-xs text-zinc-500">{formatFileSize(doc.size)}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="p-4 space-y-2 border-t border-zinc-800">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.txt,.md"
            className="hidden"
            onChange={handleFileChange}
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="w-full flex items-center justify-center gap-2 rounded-lg bg-zinc-700 hover:bg-zinc-600 disabled:opacity-50 disabled:cursor-not-allowed px-3 py-2 text-sm font-medium transition-colors"
          >
            {uploading ? (
              <>
                <Spinner size={14} />
                Enviando…
              </>
            ) : (
              <>
                <UploadIcon />
                Enviar documento
              </>
            )}
          </button>
          <p className="text-center text-xs text-zinc-600">PDF · TXT · Markdown</p>

          <button
            onClick={onNewSession}
            className="w-full flex items-center justify-center gap-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 px-3 py-2 text-sm font-medium text-zinc-300 transition-colors"
          >
            <PlusIcon />
            Nova sessão
          </button>

          {documents.length > 0 && (
            <button
              onClick={handleTerminate}
              className="w-full rounded-lg border border-red-900 text-red-400 hover:bg-red-950 px-3 py-2 text-sm font-medium transition-colors"
            >
              Encerrar sessão
            </button>
          )}
        </div>
      </aside>

      {/* Main chat area */}
      <main className="flex flex-1 flex-col min-w-0">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full gap-3 text-center">
              <div className="rounded-full bg-zinc-800 p-4">
                <ChatIcon />
              </div>
              <p className="text-zinc-400 text-sm max-w-xs">
                Envie uma mensagem ou carregue um documento para começar.
              </p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {msg.role === "assistant" && (
                <div className="shrink-0 w-8 h-8 rounded-full bg-zinc-700 flex items-center justify-center text-xs font-bold text-zinc-300">
                  AI
                </div>
              )}
              <div className={`max-w-2xl flex flex-col gap-2 ${msg.role === "user" ? "items-end" : "items-start"}`}>
                <div
                  className={`rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                    msg.role === "user"
                      ? "bg-zinc-700 text-zinc-100 rounded-br-sm"
                      : "bg-zinc-800 text-zinc-100 rounded-bl-sm"
                  }`}
                >
                  {msg.content}
                </div>

                {msg.sources && msg.sources.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {msg.sources.map((src, j) => (
                      <span
                        key={j}
                        className="inline-flex items-center gap-1 rounded-full bg-zinc-800 border border-zinc-700 px-2 py-0.5 text-xs text-zinc-400"
                        title={src.uri}
                      >
                        <DocumentIcon />
                        {src.file}
                        {src.pages.length > 0 && (
                          <span className="text-zinc-600">p. {src.pages.join(", ")}</span>
                        )}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {msg.role === "user" && (
                <div className="shrink-0 w-8 h-8 rounded-full bg-zinc-600 flex items-center justify-center text-xs font-bold text-zinc-300">
                  U
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex gap-3 justify-start">
              <div className="shrink-0 w-8 h-8 rounded-full bg-zinc-700 flex items-center justify-center text-xs font-bold text-zinc-300">
                AI
              </div>
              <div className="rounded-2xl rounded-bl-sm bg-zinc-800 px-4 py-3 flex items-center gap-1">
                <span className="w-1.5 h-1.5 bg-zinc-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
                <span className="w-1.5 h-1.5 bg-zinc-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
                <span className="w-1.5 h-1.5 bg-zinc-400 rounded-full animate-bounce" />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Error banner */}
        {error && (
          <div className="mx-4 mb-2 rounded-lg bg-red-950 border border-red-800 px-4 py-2 text-sm text-red-300 flex items-center justify-between gap-2">
            <span>{error}</span>
            <button onClick={() => setError(null)} className="text-red-400 hover:text-red-200 shrink-0">
              ✕
            </button>
          </div>
        )}

        {/* Input area */}
        <div className="border-t border-zinc-800 p-4">
          <div className="flex gap-3 items-end max-w-4xl mx-auto">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Digite sua mensagem… (Enter para enviar, Shift+Enter para nova linha)"
              rows={1}
              disabled={loading}
              className="flex-1 resize-none rounded-xl bg-zinc-800 border border-zinc-700 focus:border-zinc-500 focus:outline-none px-4 py-3 text-sm text-zinc-100 placeholder:text-zinc-500 disabled:opacity-50 transition-colors max-h-40 overflow-y-auto"
              style={{ fieldSizing: "content" } as React.CSSProperties}
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="shrink-0 rounded-xl bg-zinc-100 hover:bg-white disabled:opacity-40 disabled:cursor-not-allowed text-zinc-900 px-4 py-3 font-medium text-sm transition-colors flex items-center gap-2"
            >
              {loading ? <Spinner size={16} /> : <SendIcon />}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

function Spinner({ size = 16 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      className="animate-spin"
    >
      <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
    </svg>
  );
}

function SendIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="22" y1="2" x2="11" y2="13" />
      <polygon points="22 2 15 22 11 13 2 9 22 2" />
    </svg>
  );
}

function UploadIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="17 8 12 3 7 8" />
      <line x1="12" y1="3" x2="12" y2="15" />
    </svg>
  );
}

function ChatIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-zinc-500">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
  );
}

function PlusIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="5" x2="12" y2="19" />
      <line x1="5" y1="12" x2="19" y2="12" />
    </svg>
  );
}

function CopyIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-green-400">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

function DocumentIcon() {
  return (
    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
    </svg>
  );
}
