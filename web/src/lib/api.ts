export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Source = {
  source: string;
  section: string;
  score: number;
};

export type StreamEvent =
  | { type: "sources"; sources: Source[]; used_context: boolean }
  | { type: "token"; text: string }
  | { type: "error"; message: string }
  | { type: "done"; latency_ms: number };

export async function streamChat(
  question: string,
  previousQuestion: string | null,
  onEvent: (event: StreamEvent) => void,
  signal: AbortSignal,
): Promise<void> {
  const response = await fetch(`${API_URL}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, previous_question: previousQuestion }),
    signal,
  });

  if (!response.ok || !response.body) {
    throw new Error(
      response.status === 422
        ? "Questions must be between 1 and 500 characters."
        : `The assistant is unavailable right now (HTTP ${response.status}).`,
    );
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let newline = buffer.indexOf("\n");
    while (newline >= 0) {
      const line = buffer.slice(0, newline).trim();
      buffer = buffer.slice(newline + 1);
      if (line) onEvent(JSON.parse(line) as StreamEvent);
      newline = buffer.indexOf("\n");
    }
  }

  if (buffer.trim()) onEvent(JSON.parse(buffer) as StreamEvent);
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/health`, { cache: "no-store" });
    if (!response.ok) return false;
    const data = await response.json();
    return data?.qdrant?.status === "ok";
  } catch {
    return false;
  }
}

const DOC_LABELS: Record<string, string> = {
  about: "About",
  skills: "Skills",
  "education-experience": "Education & experience",
  santa: "Santa",
  coldbrew: "ColdBrew",
  "menu-detector": "Menu Detector",
  "face-detection": "Face Detection",
  "juno-assistant": "Juno Assistant",
};

export function sourceLabel(source: Source): string {
  const stem = source.source.split("/").pop()?.replace(/\.md$/, "") ?? source.source;
  const doc = DOC_LABELS[stem] ?? stem;
  const section = source.section.split(">").pop()?.trim() ?? source.section;
  return `${doc} · ${section}`;
}
