import type { ReactNode } from "react";

export type PlateTone = "blue";

export type PlateProps = {
  tone: PlateTone;
  inline?: boolean; // sized by its content inside the article column, no outer margin
  children: ReactNode;
};

// A sign set inside the page column (inline), sized by its content.
export function Plate({ tone, inline, children }: PlateProps) {
  const classes = ["plate", `plate--${tone}`, inline && "plate--inline"].filter(Boolean).join(" ");
  return <section className={classes}>{children}</section>;
}
