import type { ReactNode } from "react";

export type PlateTone = "blue" | "white" | "yellow" | "steel";

export type PlateProps = {
  tone: PlateTone;
  id?: string;
  labelledBy?: string; // id of the heading inside the plate
  className?: string;
  children: ReactNode;
};

// One section of the page is one sign.
export function Plate({ tone, id, labelledBy, className, children }: PlateProps) {
  const classes = ["plate", `plate--${tone}`, className].filter(Boolean).join(" ");
  return (
    <section id={id} aria-labelledby={labelledBy} className={classes}>
      {children}
    </section>
  );
}
