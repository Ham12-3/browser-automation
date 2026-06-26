import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "OmniBrowse Agent",
  description: "Local, visible, permission-based browser automation."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

