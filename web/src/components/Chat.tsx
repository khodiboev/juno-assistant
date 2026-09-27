"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { checkHealth, Source, sourceLabel, streamChat } from "@/lib/api";
import { profile, starterQuestions } from "@/data/profile";
import { ArrowUpIcon, CheckIcon, CopyIcon, StopIcon } from "./Icons";
import styles from "./Chat.module.css";

type Status = "streaming" | "done" | "stopped" | "error";

type Message = {
  id: number;
  role: "user" | "assistant";
  text: string;
  sources?: Source[];
  usedContext?: boolean;
  latencyMs?: number;
  status?: Status;
};

type Health = "checking" | "online" | "offline";

const MAX_LENGTH = 500;

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [health, setHealth] = useState<Health>("checking");
  const [copiedId, setCopiedId] = useState<number | null>(null);
  const controllerRef = useRef<AbortController | null>(null);
  const nextIdRef = useRef(1);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    checkHealth().then((ok) => setHealth(ok ? "online" : "offline"));
  }, []);

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages]);

  const updateMessage = (id: number, patch: (m: Message) => Partial<Message>) => {
    setMessages((prev) => prev.map((m) => (m.id === id ? { ...m, ...patch(m) } : m)));
  };

  const ask = async (raw: string) => {
    const question = raw.trim();
    if (!question || busy) return;

    const previousQuestion = [...messages].reverse().find((m) => m.role === "user")?.text ?? null;
    const userId = nextIdRef.current++;
    const assistantId = nextIdRef.current++;
    setMessages((prev) => [
      ...prev,
      { id: userId, role: "user", text: question },
      { id: assistantId, role: "assistant", text: "", status: "streaming" },
    ]);
    setInput("");
    setBusy(true);

    const controller = new AbortController();
    controllerRef.current = controller;

    try {
      await streamChat(
        question,
        previousQuestion,
        (event) => {
          if (event.type === "sources") {
            updateMessage(assistantId, () => ({ sources: event.sources, usedContext: event.used_context }));
          } else if (event.type === "token") {
            updateMessage(assistantId, (m) => ({ text: m.text + event.text }));
          } else if (event.type === "error") {
            updateMessage(assistantId, () => ({ text: event.message, status: "error" }));
          } else if (event.type === "done") {
            updateMessage(assistantId, (m) => ({
              latencyMs: event.latency_ms,
              status: m.status === "error" ? "error" : "done",
            }));
          }
        },
        controller.signal,
      );
    } catch (error) {
      if (controller.signal.aborted) {
        updateMessage(assistantId, () => ({ status: "stopped" }));
      } else {
        const message =
          error instanceof Error && error.message.startsWith("Questions")
            ? error.message
            : "Can't reach the assistant. Check that the backend is running, then try again.";
        updateMessage(assistantId, () => ({ text: message, status: "error" }));
        setHealth("offline");
      }
    } finally {
      controllerRef.current = null;
      setBusy(false);
      inputRef.current?.focus();
    }
  };

  const onSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (busy) {
      controllerRef.current?.abort();
    } else {
      ask(input);
    }
  };

  const copy = async (message: Message) => {
    try {
      await navigator.clipboard.writeText(message.text);
      setCopiedId(message.id);
      setTimeout(() => setCopiedId((current) => (current === message.id ? null : current)), 1500);
    } catch {
      setCopiedId(null);
    }
  };

  const asked = new Set(messages.filter((m) => m.role === "user").map((m) => m.text));
  const followUps = starterQuestions.filter((s) => !asked.has(s.question)).slice(0, 3);
  const isEmpty = messages.length === 0;

  const composer = (
    <form className={styles.form} onSubmit={onSubmit}>
      <label htmlFor="question" className="visually-hidden">
        Your question
      </label>
      <input
        id="question"
        ref={inputRef}
        className={styles.input}
        type="text"
        value={input}
        maxLength={MAX_LENGTH}
        autoComplete="off"
        placeholder="Ask about Juno's experience, projects or skills…"
        onChange={(e) => setInput(e.target.value)}
      />
      <button
        type="submit"
        className={busy ? `${styles.send} ${styles.stop}` : styles.send}
        aria-label={busy ? "Stop generating" : "Send question"}
        disabled={!busy && !input.trim()}
      >
        {busy ? <StopIcon /> : <ArrowUpIcon />}
      </button>
    </form>
  );

  return (
    <main className={styles.chat}>
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <div>
            <h2 className={styles.title}>Ask about {profile.nickname}</h2>
            <p className={styles.subtitle}>Answers come only from Juno&apos;s own documents</p>
          </div>
          <div className={styles.badge} title={healthLabel(health)}>
            <span className={`${styles.dot} ${styles[health]}`} aria-hidden />
            <span>Qwen2.5-1.5B · RAG</span>
            <span className="visually-hidden">{healthLabel(health)}</span>
          </div>
        </div>
      </header>

      {isEmpty ? (
        <section className={styles.empty}>
          <div className={styles.column}>
            <div className={styles.intro}>
              <h3 className={styles.introTitle}>What would you like to know about Juno?</h3>
              <p className={styles.introText}>
                I answer from his resume and project notes, show where each answer comes from, and tell you when I
                don&apos;t know.
              </p>
            </div>
            {composer}
            <div className={styles.starters}>
              {starterQuestions.map((s) => (
                <button key={s.question} type="button" className={styles.starter} onClick={() => ask(s.question)}>
                  <span className={styles.starterTopic}>{s.topic}</span>
                  <span className={styles.starterQuestion}>{s.question}</span>
                </button>
              ))}
            </div>
          </div>
        </section>
      ) : (
        <>
          <div className={styles.scroll} ref={scrollRef}>
            <ol className={`${styles.column} ${styles.messages}`} aria-live="polite">
              {messages.map((m) =>
                m.role === "user" ? (
                  <li key={m.id} className={styles.userMessage}>
                    {m.text}
                  </li>
                ) : (
                  <li key={m.id} className={styles.assistantMessage}>
                    <div className={styles.assistantAvatar} aria-hidden>
                      {profile.initials}
                    </div>
                    <AssistantBody message={m} copied={copiedId === m.id} onCopy={() => copy(m)} />
                  </li>
                ),
              )}
            </ol>
          </div>

          <div className={styles.composerDock}>
            <div className={styles.column}>
              {followUps.length > 0 && (
                <div className={styles.followUps}>
                  {followUps.map((s) => (
                    <button
                      key={s.question}
                      type="button"
                      className={styles.followUp}
                      onClick={() => ask(s.question)}
                      disabled={busy}
                    >
                      {s.question}
                    </button>
                  ))}
                </div>
              )}
              {composer}
              <p className={styles.note}>Off-topic questions are declined. Answers may be incomplete.</p>
            </div>
          </div>
        </>
      )}
    </main>
  );
}

function AssistantBody({ message, copied, onCopy }: { message: Message; copied: boolean; onCopy: () => void }) {
  const declined = message.status === "done" && message.usedContext === false;

  if (declined) {
    return (
      <div className={styles.assistantBody}>
        <p className={styles.declined}>{message.text}</p>
      </div>
    );
  }

  return (
    <div className={styles.assistantBody}>
      <p className={message.status === "error" ? `${styles.answer} ${styles.answerError}` : styles.answer}>
        {message.text}
        {message.status === "streaming" && <span className={styles.cursor} aria-hidden />}
        {message.status === "streaming" && !message.text && <span className="visually-hidden">Thinking…</span>}
      </p>

      {message.status === "stopped" && <p className={styles.meta}>Stopped</p>}

      {message.status === "done" && (
        <div className={styles.answerFooter}>
          {message.sources && message.sources.length > 0 && (
            <div className={styles.sources}>
              <span className={styles.sourcesLabel}>Sources</span>
              {message.sources.map((s) => (
                <span key={`${s.source}-${s.section}`} className={styles.sourceChip}>
                  {sourceLabel(s)}
                </span>
              ))}
            </div>
          )}
          <div className={styles.actions}>
            {message.latencyMs !== undefined && (
              <span className={styles.meta}>{(message.latencyMs / 1000).toFixed(1)} s</span>
            )}
            <button type="button" className={styles.copy} onClick={onCopy} aria-label="Copy answer">
              {copied ? <CheckIcon /> : <CopyIcon />}
              <span>{copied ? "Copied" : "Copy"}</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function healthLabel(health: Health): string {
  if (health === "online") return "Assistant online";
  if (health === "offline") return "Assistant offline";
  return "Checking assistant status";
}
