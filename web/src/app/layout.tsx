import type { Metadata } from "next";
import { IBM_Plex_Mono, IBM_Plex_Sans } from "next/font/google";
import "./globals.css";

const ibmSans = IBM_Plex_Sans({
  variable: "--font-ibm-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const ibmMono = IBM_Plex_Mono({
  variable: "--font-ibm-mono",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "LOCAL BENCH — Offline LLM measurement on Apple Silicon",
  description:
    "Private local assistant on Ollama with Pydantic-validated job extraction and a 3-model benchmark on Apple M4.",
  openGraph: {
    title: "LOCAL BENCH",
    description:
      "Measured offline. Picked with data. Structured job extraction + model comparison on a Mac laptop.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${ibmSans.variable} ${ibmMono.variable} h-full`}>
      <body className="min-h-full antialiased">{children}</body>
    </html>
  );
}
