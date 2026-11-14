// Stop sign. Used at most twice on the page.
export function StopOctagon({ className }: { className?: string }) {
  return (
    <svg
      className={["stop", className].filter(Boolean).join(" ")}
      viewBox="0 0 100 100"
      role="img"
      aria-label="Stop"
      focusable="false"
    >
      <polygon points="30,4 70,4 96,30 96,70 70,96 30,96 4,70 4,30" className="stop-field" />
      <text x="50" y="50" textAnchor="middle" dominantBaseline="central" className="stop-text">
        STOP
      </text>
    </svg>
  );
}
