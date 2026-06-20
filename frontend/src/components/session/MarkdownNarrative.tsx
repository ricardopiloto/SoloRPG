"use client";

import ReactMarkdown from "react-markdown";

interface Props {
  content: string;
  streaming?: boolean;
  className?: string;
}

export function MarkdownNarrative({ content, streaming, className }: Props) {
  const text = streaming ? content : content;

  return (
    <div className={`narrative-block ${className ?? ""} ${streaming ? "opacity-90" : ""}`}>
      <ReactMarkdown
        components={{
          p: ({ children }) => <p className="mb-3 last:mb-0">{children}</p>,
          strong: ({ children }) => (
            <strong className="font-semibold text-wfrp-highlight">{children}</strong>
          ),
          em: ({ children }) => <em className="italic text-wfrp-fg/90">{children}</em>,
          ul: ({ children }) => (
            <ul className="list-disc list-inside mb-3 space-y-1">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal list-inside mb-3 space-y-1">{children}</ol>
          ),
          li: ({ children }) => <li className="text-wfrp-fg">{children}</li>,
          hr: () => (
            <hr className="border-wfrp-border/50 my-4" />
          ),
          blockquote: ({ children }) => (
            <blockquote className="border-l-2 border-wfrp-accent/60 pl-3 italic text-wfrp-muted my-3">
              {children}
            </blockquote>
          ),
          // Keep headings subtle — this is narrative text, not docs
          h1: ({ children }) => (
            <p className="font-display text-lg text-wfrp-highlight mb-2">{children}</p>
          ),
          h2: ({ children }) => (
            <p className="font-display text-base text-wfrp-highlight mb-2">{children}</p>
          ),
          h3: ({ children }) => (
            <p className="font-display text-sm text-wfrp-highlight mb-1">{children}</p>
          ),
          // Strip links — no URLs in narrative
          a: ({ children }) => <span className="text-wfrp-accent">{children}</span>,
          // Code blocks shouldn't appear in GM narrative, render as plain
          code: ({ children }) => <span className="font-mono text-sm">{children}</span>,
        }}
      >
        {text}
      </ReactMarkdown>
      {streaming && (
        <span className="inline-block w-0.5 h-4 bg-wfrp-accent ml-0.5 animate-pulse" />
      )}
    </div>
  );
}
