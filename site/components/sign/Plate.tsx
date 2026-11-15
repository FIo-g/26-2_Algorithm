import type { ReactNode } from "react";

export type PlateTone = "blue" | "white" | "yellow" | "steel";

export type PlateProps = {
  tone: PlateTone;
  id?: string;
  labelledBy?: string; // id of the heading inside the plate
  inline?: boolean; // sized by its content inside the article column, no outer margin
  className?: string;
  children: ReactNode;
};

// A sign set inside the page column (inline), sized by its content.
export function Plate({ tone, id, labelledBy, inline, className, children }: PlateProps) {
  const classes = ["plate", `plate--${tone}`, inline && "plate--inline", className].filter(Boolean).join(" ");
  return (
    <section id={id} aria-labelledby={labelledBy} className={classes}>
      {children}
    </section>
  );
}
