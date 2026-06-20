"use client";

import { useCallback, useEffect, useRef } from "react";

type Side = "left" | "right";

export function ResizeHandle({
  side,
  onResize,
}: {
  side: Side;
  onResize: (width: number) => void;
}) {
  const dragging = useRef(false);
  const startX = useRef(0);
  const startW = useRef(0);

  const onMouseDown = useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault();
      dragging.current = true;
      startX.current = e.clientX;
      const varName = side === "left" ? "--left-w" : "--right-w";
      const current = getComputedStyle(document.documentElement).getPropertyValue(varName);
      startW.current = parseInt(current, 10) || (side === "left" ? 280 : 260);
      document.body.classList.add("resizing");
    },
    [side]
  );

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      if (!dragging.current) return;
      const delta = side === "left" ? e.clientX - startX.current : startX.current - e.clientX;
      const next = Math.max(200, Math.min(420, startW.current + delta));
      onResize(next);
    };
    const onUp = () => {
      if (!dragging.current) return;
      dragging.current = false;
      document.body.classList.remove("resizing");
    };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
  }, [side, onResize]);

  return (
    <div
      className="resize-handle"
      onMouseDown={onMouseDown}
      role="separator"
      aria-orientation="vertical"
      aria-label={side === "left" ? "Redimensionar ficha" : "Redimensionar diários"}
    />
  );
}

export function useSidebarWidths(sessionId: string) {
  const apply = useCallback(
    (left: number, right: number) => {
      document.documentElement.style.setProperty("--left-w", `${left}px`);
      document.documentElement.style.setProperty("--right-w", `${right}px`);
      localStorage.setItem(`wfrp-sidebar-${sessionId}`, JSON.stringify({ left, right }));
    },
    [sessionId]
  );

  useEffect(() => {
    const stored = localStorage.getItem(`wfrp-sidebar-${sessionId}`);
    if (stored) {
      try {
        const { left, right } = JSON.parse(stored);
        apply(left ?? 280, right ?? 260);
      } catch {
        apply(280, 260);
      }
    } else {
      apply(280, 260);
    }
  }, [sessionId, apply]);

  return apply;
}
