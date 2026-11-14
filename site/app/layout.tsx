import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Gothic_A1, Overpass } from "next/font/google";
import "./globals.css";

const overpass = Overpass({
  subsets: ["latin"],
  weight: ["400", "700", "800"],
  variable: "--font-overpass",
  display: "swap",
});

// Hangul is only used for place and team names, so it is not preloaded.
const gothicA1 = Gothic_A1({
  weight: ["800"],
  variable: "--font-gothic-a1",
  display: "swap",
  preload: false,
});

export const metadata: Metadata = {
  title: "Seoul shortest paths: the same answer for less",
  description:
    "Four exact shortest-path methods compared on the real Seoul road network, each checked against Dijkstra before it was timed.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className={`${overpass.variable} ${gothicA1.variable}`}>
      <body>{children}</body>
    </html>
  );
}
