export function FateGems({ current, max }: { current: number; max: number }) {
  return (
    <span className="tracking-widest text-sm">
      {Array.from({ length: max }, (_, i) => (
        <span key={i} className={i < current ? "fate-gem-filled" : "fate-gem-empty"}>
          {i < current ? "◆" : "◇"}
        </span>
      ))}
    </span>
  );
}
