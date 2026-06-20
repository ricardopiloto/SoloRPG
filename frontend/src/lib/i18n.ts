import ptBR from "../../messages/pt-BR.json";

export type Messages = typeof ptBR;

export function getMessages(): Messages {
  return ptBR;
}

/** i18n-ready helper — expand with next-intl middleware when adding locales */
export function t(path: string, params?: Record<string, string | number>): string {
  const keys = path.split(".");
  let value: unknown = getMessages();
  for (const key of keys) {
    value = (value as Record<string, unknown>)?.[key];
  }
  if (typeof value !== "string") return path;
  if (!params) return value;
  return Object.entries(params).reduce(
    (s, [k, v]) => s.replace(`{${k}}`, String(v)),
    value
  );
}
