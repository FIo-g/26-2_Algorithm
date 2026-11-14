import type { MouseEventHandler, ReactNode } from "react";

export type SubPlateProps = {
  children: ReactNode;
  href?: string; // renders a link
  onClick?: MouseEventHandler<HTMLButtonElement>; // renders a button (client parents only)
  pressed?: boolean; // toggle button: sets aria-pressed
  checked?: boolean; // radio plate: role="radio" with aria-checked
  role?: "radio" | "tab";
  disabled?: boolean;
  className?: string;
  id?: string;
  tabIndex?: number;
  "aria-controls"?: string;
};

// The white supplementary plate. Static label, link or button, decided by the props.
// Without a handler or state props it renders a plain span, so it works in Server Components.
export function SubPlate(props: SubPlateProps) {
  const { children, href, onClick, pressed, checked, role, disabled, className, id, tabIndex } = props;
  const classes = ["subplate", className].filter(Boolean).join(" ");

  if (href) {
    const external = href.startsWith("http");
    return (
      <a
        id={id}
        href={href}
        className={classes}
        target={external ? "_blank" : undefined}
        rel={external ? "noopener noreferrer" : undefined}
        tabIndex={tabIndex}
      >
        {children}
      </a>
    );
  }

  const isButton = onClick !== undefined || pressed !== undefined || checked !== undefined || role !== undefined;
  if (isButton) {
    return (
      <button
        type="button"
        id={id}
        className={classes}
        onClick={onClick}
        disabled={disabled}
        role={role}
        aria-pressed={pressed}
        aria-checked={checked}
        aria-controls={props["aria-controls"]}
        tabIndex={tabIndex}
      >
        {children}
      </button>
    );
  }

  return (
    <span id={id} className={classes}>
      {children}
    </span>
  );
}
