/** Mirrors backend ENABLE_CUSTOM_CHARGEN — wizard UI when true. */
export const customChargenEnabled =
  process.env.NEXT_PUBLIC_ENABLE_CUSTOM_CHARGEN === "true";

/** Mirrors backend APP_ENV — development enables dev master login hints. */
export const isDevAppEnv =
  (process.env.NEXT_PUBLIC_APP_ENV || "development") === "development";
