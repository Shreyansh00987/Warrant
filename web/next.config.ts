import type { NextConfig } from "next";

function getBackendUrl(): string {
  const envUrl = process.env.NEXT_PUBLIC_CLERK_API_URL;
  if (!envUrl) return "http://127.0.0.1:8000";
  if (
    envUrl === "warrant-clerk" ||
    envUrl === "http://warrant-clerk" ||
    envUrl === "https://warrant-clerk"
  ) {
    return "https://warrant-clerk.onrender.com";
  }
  if (envUrl.startsWith("http://") || envUrl.startsWith("https://")) {
    return envUrl.replace(/\/$/, "");
  }
  return `https://${envUrl.replace(/\/$/, "")}`;
}

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Rewrites to proxy Clerk API if running both on localhost or cloud
  async rewrites() {
    return [
      {
        source: "/api/clerk/:path*",
        destination: `${getBackendUrl()}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
