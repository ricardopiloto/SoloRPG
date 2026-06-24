"use client";

import { useLayoutEffect, useRef, useState } from "react";

export function TruncatedText({ children }: { children: string }) {
  const ref = useRef<HTMLSpanElement>(null);
  const [truncated, setTruncated] = useState(false);

  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;

    const check = () => {
      setTruncated(el.scrollWidth > el.clientWidth);
    };

    check();
    const observer = new ResizeObserver(check);
    observer.observe(el);
    return () => observer.disconnect();
  }, [children]);

  return (
    <span ref={ref} className="truncate" title={truncated ? children : undefined}>
      {children}
    </span>
  );
}
