"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

export function Navigation() {
  const pathname = usePathname();
  const router = useRouter();
  const [shaInput, setShaInput] = useState("");

  const handleVerifySubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!shaInput.trim()) return;
    const cleanSha = shaInput.trim();
    // Navigate to ledger or prompt
    router.push(`/ledger?verify=${encodeURIComponent(cleanSha)}`);
  };

  const navLinks = [
    { href: "/", label: "Overview" },
    { href: "/ledger", label: "Ledger" },
    { href: "/settings", label: "Settings & Config" },
  ];

  return (
    <header className="hairline-b bg-paper sticky top-0 z-40 backdrop-blur-sm bg-paper/95">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Brand & Subtitle */}
        <div className="flex items-baseline gap-3">
          <Link href="/" className="font-serif font-black text-2xl tracking-tight text-ink hover:text-oxblood transition-colors">
            WARRANT
          </Link>
          <span className="text-xs font-mono text-ink-muted hidden sm:inline">
            Flip the Switch 2026
          </span>
          <span className="px-1.5 py-0.5 text-[9px] font-mono uppercase tracking-wider border border-rule text-ink-muted bg-paper-dark/30">
            Switch Bridge Active
          </span>
        </div>

        {/* Navigation & Quick Verify Input */}
        <div className="flex flex-wrap items-center gap-4 sm:gap-6 text-xs font-mono">
          <nav className="flex items-center gap-4 sm:gap-5">
            {navLinks.map((link) => {
              const isActive = pathname === link.href || (link.href !== "/" && pathname.startsWith(link.href));
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`transition-colors py-1 ${
                    isActive
                      ? "text-ink font-bold border-b border-ink"
                      : "text-ink-muted hover:text-ink"
                  }`}
                >
                  {link.label}
                </Link>
              );
            })}
          </nav>

          {/* Quick Commit Verify Box */}
          <form onSubmit={handleVerifySubmit} className="flex items-center gap-1.5">
            <input
              type="text"
              placeholder="Verify SHA (e.g. 8f4a12c...)"
              value={shaInput}
              onChange={(e) => setShaInput(e.target.value)}
              className="bg-paper-light border border-rule px-2 py-1 text-[11px] font-mono text-ink placeholder:text-ink-muted/50 rounded-[1px] w-36 sm:w-44 focus:outline-none focus:border-ink"
              aria-label="Verify Commit SHA"
            />
            <button
              type="submit"
              className="px-2 py-1 bg-ink text-paper text-[11px] font-mono font-medium hover:bg-oxblood transition-colors rounded-[1px]"
            >
              Verify
            </button>
          </form>
        </div>
      </div>
    </header>
  );
}
