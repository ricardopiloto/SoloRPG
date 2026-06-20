"use client";

import { ATTRIBUTE_LABELS, ATTRIBUTE_ORDER, type AttributeKey } from "@/lib/wfrp-attributes";

function AttributeValue({ value }: { value: number }) {
  const tens = Math.floor(value / 10);
  const ones = value % 10;
  return (
    <span className="attribute-card-value font-mono tabular-nums">
      <span className="attribute-card-tens">{tens}</span>
      {ones}
    </span>
  );
}

export function AttributeCards({
  attributes,
  disabled,
  onSelect,
}: {
  attributes: Record<string, number>;
  disabled?: boolean;
  onSelect: (key: AttributeKey, value: number) => void;
}) {
  return (
    <div className="attribute-cards-grid">
      {ATTRIBUTE_ORDER.map((key) => {
        const value = attributes[key] ?? 30;
        const label = ATTRIBUTE_LABELS[key];
        return (
          <button
            key={key}
            type="button"
            className="attribute-card rollable"
            disabled={disabled}
            title={label}
            aria-label={`${key}, ${label}, ${value}`}
            onClick={() => onSelect(key, value)}
          >
            <span className="attribute-card-abbr">{key}</span>
            <AttributeValue value={value} />
          </button>
        );
      })}
    </div>
  );
}
