// Caution sign. Decorative: the caveat sentence after it carries the meaning.
export function CautionTriangle({ className }: { className?: string }) {
  return (
    <svg
      className={["caution", className].filter(Boolean).join(" ")}
      viewBox="0 0 24 24"
      aria-hidden="true"
      focusable="false"
    >
      <path d="M12 3.5 L21.5 20 H2.5 Z" className="caution-field" />
      <rect x="11" y="8.5" width="2" height="7" rx="1" className="caution-mark" />
      <circle cx="12" cy="17.6" r="1.2" className="caution-mark" />
    </svg>
  );
}
