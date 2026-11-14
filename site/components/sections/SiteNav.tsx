import { SubPlate } from "@/components/sign/SubPlate";

const LINKS = [
  { href: "#map", label: "Map" },
  { href: "#same-answer", label: "Same answer" },
  { href: "#methods", label: "Methods" },
  { href: "#results", label: "Results" },
  { href: "#congestion", label: "Congestion" },
  { href: "#limits", label: "Limits" },
  { href: "#team", label: "Team" },
];

// The row scrolls sideways inside itself on narrow screens. The page itself does not scroll sideways.
export function SiteNav() {
  return (
    <nav className="site-nav" aria-label="Sections">
      {LINKS.map((link) => (
        <SubPlate key={link.href} href={link.href}>
          {link.label}
        </SubPlate>
      ))}
    </nav>
  );
}
