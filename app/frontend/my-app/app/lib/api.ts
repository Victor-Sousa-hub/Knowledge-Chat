const API_URL = process.env.NEXT_PUBLIC_API_URL;

export interface ChatRequest {
  session_id: string;
  question: string;
}

export interface SourceReference {
  file: string;
  uri: string;
  pages: number[];
}

export interface ChatResponse {
  answer: string;
  session_id: string;
  sources: SourceReference[];
}

export interface UploadDocumentResponse {
  file_name: string;
  s3_key: string;
  bucket: string;
  ingestion_job_id: string;
  message: string;
}

export interface SessionDocument {
  name: string;
  size: number;
}

export interface SessionDocumentsResponse {
  session_id: string;
  documents: SessionDocument[];
  total: number;
}

export interface TerminateSessionResponse {
  session_id: string;
  deleted_documents: number;
  message: string;
}

export async function sendMessage(session_id: string, question: string): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/chat/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id, question }),
  });
  if (!res.ok) throw new Error(`Chat error: ${res.status}`);
  return res.json();
}

export async function uploadDocument(session_id: string, file: File): Promise<UploadDocumentResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_URL}/sessions/${session_id}/documents/`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? `Upload error: ${res.status}`);
  }
  return res.json();
}

export async function getSessionDocuments(session_id: string): Promise<SessionDocumentsResponse> {
  const res = await fetch(`${API_URL}/session/sessions/${session_id}/history`);
  if (!res.ok) throw new Error(`History error: ${res.status}`);
  return res.json();
}

export async function terminateSession(session_id: string): Promise<TerminateSessionResponse> {
  const res = await fetch(`${API_URL}/session/sessions/${session_id}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error(`Terminate error: ${res.status}`);
  return res.json();
}
