import type { Metadata } from "next";
import { Cinzel, Crimson_Text, Source_Sans_3 } from "next/font/google";
import "./globals.css";

const cinzel = Cinzel({
  subsets: ["latin"],
  weight: ["500", "600"],
  variable: "--font-cinzel",
});

const crimson = Crimson_Text({
  subsets: ["latin"],
  weight: ["400", "600"],
  style: ["normal", "italic"],
  variable: "--font-crimson",
});

const sourceSans = Source_Sans_3({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-source",
});

export const metadata: Metadata = {
  title: "WFRP Solo",
  description: "RPG solo com GM sintético — Warhammer Fantasy Roleplay 4ª Edição",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className={`${cinzel.variable} ${crimson.variable} ${sourceSans.variable}`}>
      <body className="font-ui min-h-dvh">{children}</body>
    </html>
  );
}
