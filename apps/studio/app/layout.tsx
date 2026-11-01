import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "WebVerse AI — Build a world, not just a website",
  description: "Generate immersive, responsive websites with AI and interactive 3D scenes.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
