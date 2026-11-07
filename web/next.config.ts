import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Rewrites to proxy Clerk API if running both on localhost
  async rewrites() {
    return [
      {
        source: "/api/clerk/:path*",
        destination: `${process.env.NEXT_PUBLIC_CLERK_API_URL || "http://127.0.0.1:8000"}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
