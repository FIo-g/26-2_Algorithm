import { METHODS, type MethodId } from "@/lib/methods";

// Shape geometry in a 24 by 24 box. Charts reuse GlyphShape for their markers.
export function GlyphShape({ method }: { method: MethodId }) {
  const info = METHODS[method];
  const fill = { fill: info.fill };
  switch (info.shape) {
    case "disc":
      return <circle cx="12" cy="12" r="9" style={fill} />;
    case "triangle":
      return <polygon points="12,3 22,20 2,20" style={fill} />;
    case "diamond":
      return <polygon points="12,2 22,12 12,22 2,12" style={fill} />;
    case "square": {
      const side = info.squareSize === "small" ? 10 : info.squareSize === "medium" ? 14 : 18;
      const at = 12 - side / 2;
      return <rect x={at} y={at} width={side} height={side} style={fill} />;
    }
  }
}

// The shape that identifies a method everywhere. Stroke follows the text colour, so it reads on blue and white.
export function MethodGlyph({ method, className }: { method: MethodId; className?: string }) {
  return (
    <svg
      className={["glyph", className].filter(Boolean).join(" ")}
      viewBox="0 0 24 24"
      aria-hidden="true"
      focusable="false"
    >
      <g stroke="currentColor" strokeWidth={2} strokeLinejoin="round">
        <GlyphShape method={method} />
      </g>
    </svg>
  );
}
