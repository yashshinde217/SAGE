import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SAGE",
  description: "Self-Hosted AI for Grounded Explanation",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
