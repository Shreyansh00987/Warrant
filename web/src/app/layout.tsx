import type { Metadata } from "next";
import "./globals.css";
import { Navigation } from "@/components/Navigation";

export const metadata: Metadata = {
  title: "Warrant — Every Agent-Made Change, Traced to the Human Who Said Yes",
  description:
    "Deterministic gatekeeper and hash-linked ledger for AI coding agents powered by Switch.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-paper text-ink selection:bg-rule selection:text-ink">
        <Navigation />
        <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8">{children}</main>
        <footer className="hairline-t bg-paper py-8 mt-16 text-center text-xs font-mono text-ink-muted">
          <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
            <div>
              WARRANT · Flip the Switch Hackathon 2026 · WeMakeDevs × DevTools Academy × Switch
            </div>
            <div>
              No Switch, no warrant.
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
