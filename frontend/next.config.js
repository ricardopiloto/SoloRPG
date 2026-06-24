/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  images: {
    remotePatterns: [{ protocol: "https", hostname: "placehold.co" }],
  },

  // COOP/COEP headers required for SharedArrayBuffer used by Ammo.js (DiceBox physics).
  // These must be present on the HTML document for the browser to allow Workers + WASM.
  // The Caddy reverse proxy should also forward/add these for full coverage of static assets.
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "Cross-Origin-Opener-Policy", value: "same-origin" },
          { key: "Cross-Origin-Embedder-Policy", value: "require-corp" },
        ],
      },
    ];
  },

  // Allow WASM files used by @3d-dice/dice-box (AmmoJS physics engine)
  // and prevent webpack from trying to bundle the Worker scripts served from /assets/
  webpack(config, { isServer }) {
    if (!isServer) {
      // Enable async WebAssembly (required for ammo.wasm used by dice physics)
      config.experiments = {
        ...config.experiments,
        asyncWebAssembly: true,
      };
    }
    return config;
  },
};

module.exports = nextConfig;
