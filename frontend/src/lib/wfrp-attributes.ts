export const ATTRIBUTE_ORDER = [
  "WS",
  "BS",
  "S",
  "T",
  "I",
  "Ag",
  "Dex",
  "Int",
  "WP",
  "Fel",
] as const;

export type AttributeKey = (typeof ATTRIBUTE_ORDER)[number];

export const ATTRIBUTE_LABELS: Record<AttributeKey, string> = {
  WS: "Weapon Skill",
  BS: "Ballistic Skill",
  S: "Strength",
  T: "Toughness",
  I: "Initiative",
  Ag: "Agility",
  Dex: "Dexterity",
  Int: "Intelligence",
  WP: "Willpower",
  Fel: "Fellowship",
};

export type SkillCatalogEntry = {
  name: string;
  linked_attribute: string;
};

export function computeSkillTarget(
  attributes: Record<string, number>,
  skillName: string,
  catalog: SkillCatalogEntry[],
  ownedSkills: { name: string; advances: number }[]
): number {
  const entry = catalog.find((s) => s.name === skillName);
  if (!entry) return 30;
  const base = attributes[entry.linked_attribute] ?? 30;
  const owned = ownedSkills.find((s) => s.name === skillName);
  return base + (owned?.advances ?? 0);
}

/**
 * WFRP sheet meta: advances before linked attribute.
 * @example formatSkillRowMeta("Fel", 4) → "4+[Fel]"
 * @example formatSkillRowMeta("Ag", 0) → "[Ag]"
 */
export function formatSkillRowMeta(linkedAttribute: string, advances: number): string {
  const tag = `[${linkedAttribute}]`;
  return advances > 0 ? `${advances}+${tag}` : tag;
}
