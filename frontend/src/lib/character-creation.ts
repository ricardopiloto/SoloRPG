export type CharacterCreationDraft = {
  step?: string | null;
  species_id: string;
  species_method: "choose" | "roll";
  career_id?: string | null;
  career_method: "choose" | "roll";
  career_roll_count: number;
  career_roll_options: string[];
  attributes_method: "roll" | "allocate";
  attribute_rolls: Record<string, number>;
  attribute_allocated: Record<string, number>;
  attribute_advances: Record<string, number>;
  attributes_swapped: boolean;
  attributes_rerolled: boolean;
  fate_allotted: number;
  species_skills: Record<string, number>;
  career_skills: Record<string, number>;
  career_talent?: string | null;
  species_talents: string[];
  name: string;
  background?: string | null;
};

export const ATTRS = ["WS", "BS", "S", "T", "I", "Ag", "Dex", "Int", "WP", "Fel"] as const;

export const INITIAL_DRAFT: CharacterCreationDraft = {
  species_id: "human",
  species_method: "choose",
  career_method: "choose",
  career_roll_count: 0,
  career_roll_options: [],
  attributes_method: "roll",
  attribute_rolls: {},
  attribute_allocated: {},
  attribute_advances: {},
  attributes_swapped: false,
  attributes_rerolled: false,
  fate_allotted: 2,
  species_skills: {},
  career_skills: {},
  species_talents: [],
  name: "",
  background: "",
};

export const WIZARD_STEPS = [
  "species",
  "career",
  "attributes",
  "skills",
  "trappings",
  "details",
] as const;

export type WizardStep = (typeof WIZARD_STEPS)[number];

export type CreationPreview = {
  attributes: Record<string, number>;
  wounds_max: number;
  fate_max: number;
  fortune_max: number;
  xp_awarded: number;
  xp_spent: number;
  xp_total: number;
  skills: Array<{ name: string; advances: number; linked_attribute: string }>;
  talents: Array<{ name: string }>;
  trappings: Array<{ name: string; encumbrance: number; description?: string }>;
  career: { id: string; name: string } | null;
};

export type CareerSummary = {
  id: string;
  name: string;
  career_group: string;
  class: string;
  tier: number;
};

export type CareerDetail = CareerSummary & {
  skills: string[];
  talents: string[];
  trappings: Array<{ name: string; encumbrance: number; description?: string }>;
};
