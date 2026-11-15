"use client";

import { useEffect, useState } from "react";

const LINKS = [
  { href: "#map", label: "Map" },
  { href: "#same-answer", label: "Same answer" },
  { href: "#methods", label: "Methods" },
  { href: "#results", label: "Results" },
  { href: "#congestion", label: "Congestion" },
  { href: "#team", label: "Team" },
];

// The row scrolls sideways inside itself on narrow screens. The page itself does not scroll sideways.
export function SiteNav() {
  const [current, setCurrent] = useState<string | null>(null);

  useEffect(() => {
    // shortcut: a thin band near the top of the viewport decides "in view", not the whole section,
    // so a tall section is marked as soon as it reaches the reading line.
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) setCurrent(entry.target.id);
        }
      },
      { rootMargin: "-40% 0px -55% 0px" },
    );
    for (const link of LINKS) {
      const section = document.getElementById(link.href.slice(1));
      if (section) observer.observe(section);
    }
    return () => observer.disconnect();
  }, []);

  return (
    <nav className="site-nav" aria-label="Sections">
      {LINKS.map((link) => (
        <a
          key={link.href}
          href={link.href}
          className="subplate"
          aria-current={current === link.href.slice(1) ? "true" : undefined}
        >
          {link.label}
        </a>
      ))}
    </nav>
  );
}
