import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "MedAI - Multi-Agent Medical Decision Support",
  description:
    "Enterprise AI platform for medical decision support using multi-agent systems, RAG, and predictive analytics.",
  keywords: ["medical AI", "decision support", "multi-agent", "healthcare", "analytics"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans antialiased animated-gradient min-h-screen`}>
        {children}
      </body>
    </html>
  );
}
