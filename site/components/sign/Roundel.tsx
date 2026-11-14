// Roundel for each graph's top speed (vmax, from length and time), not a posted limit.
export function Roundel({ kph, className }: { kph: number; className?: string }) {
  const value = Math.round(kph);
  return (
    <span className={["roundel", className].filter(Boolean).join(" ")} role="img" aria-label={`Top speed ${value} km/h`}>
      {value}
    </span>
  );
}
