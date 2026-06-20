"use client";

import { useState } from "react";

export function CollapsibleSection({
  title,
  children,
  defaultOpen = false,
}: {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div>
      <button type="button" className="collapsible-trigger" onClick={() => setOpen(!open)}>
        <span>{title}</span>
        <span>{open ? "−" : "+"}</span>
      </button>
      {open && <div className="pl-1 pb-2">{children}</div>}
    </div>
  );
}
