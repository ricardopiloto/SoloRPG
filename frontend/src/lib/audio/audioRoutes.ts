export const MENU_AUDIO_ROUTES = new Set([
  "/",
  "/login",
  "/register",
  "/verify-email",
  "/character",
  "/campaigns",
  "/progression",
  "/session/end",
  "/session/death",
  "/landing",
]);

export function normalizePath(path: string): string {
  if (!path || path === "/") return "/";
  const trimmed = path.replace(/\/+$/, "");
  return trimmed || "/";
}

export function isInGameRoute(path: string): boolean {
  return path.startsWith("/play/");
}

export function isMenuAudioRoute(path: string): boolean {
  return MENU_AUDIO_ROUTES.has(normalizePath(path));
}
