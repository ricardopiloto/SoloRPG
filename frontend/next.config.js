/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [{ protocol: "https", hostname: "placehold.co" }],
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
