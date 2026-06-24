const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

import { authHeaders as storedAuthHeaders, clearAuth } from "./auth-storage";

export type AuthUser = {
  id: string;
  email: string;
  email_verified: boolean;
  created_at?: string;
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
  user: AuthUser;
  starter_character?: Character;
};

export type AuthConfig = {
  auth_mode: string;
  login_username: string;
  registration_enabled: boolean;
};

export type Character = {
  id: string;
  name: string;
  status: string;
  attributes: Record<string, number>;
  wounds_current: number;
  wounds_max: number;
  fate_current: number;
  fate_max: number;
  fortune_current: number;
  fortune_max: number;
  careers: { name: string; tier: number }[];
  skills: { name: string; advances: number }[];
  talents: { name: string }[];
  trappings: { name: string; encumbrance: number; description?: string; image_url?: string }[];
  xp_total: number;
  xp_spent: number;
  background?: string;
};

export type Campaign = {
  id: string;
  character_id: string;
  status: string;
  tone?: string;
  opening_location?: string;
  character_name?: string;
  created_at: string;
  active_session_id?: string | null;
  active_session_paused?: boolean;
  active_session_time_remaining?: number | null;
};

export type SkillCatalog = {
  skills: Array<{ name: string; linked_attribute: string }>;
};

export type CampaignNpc = {
  id: string;
  name: string;
  known_name?: string | null;
  met_location?: string | null;
  role?: string | null;
  relationship_status: string;
};

export type ProgressionOptions = {
  character_id: string;
  xp_available: number;
  skills: Array<{
    name: string;
    linked_attribute: string;
    cost: number;
    current_advances: number;
    affordable: boolean;
  }>;
  talents: Array<{
    name: string;
    cost: number;
    owned: boolean;
    affordable: boolean;
  }>;
};

export type GameSession = {
  id: string;
  campaign_id: string;
  mode: string;
  is_active: boolean;
  is_first_session: boolean;
  duration_minutes: number;
  time_remaining_minutes: number;
  turn_phase?: string;
  combat_state?: CombatState | null;
};

export type CombatState = {
  turn: number;
  order: Array<{ nome: string; initiative: number; tipo?: string }>;
  current_index: number;
};

export type PendingTest = {
  payload: {
    tipo?: string;
    atributo?: string;
    pericia?: string;
    modificador?: number;
    descricao?: string;
    obrigatorio?: boolean;
    opcao_alternativa?: string | null;
  };
  setup_narrative?: string;
};

export type TurnResponse = {
  narrative: string;
  roll_results: Array<{
    type: string;
    roll?: number;
    target?: number;
    success?: boolean;
    damage?: number;
    llm_text?: string;
    skill?: string;
    attribute?: string;
    modifier?: number;
  }>;
  images: Array<{ job_id: string; type: string; url?: string; status?: string }>;
  session_ended: boolean;
  xp_awarded: number;
  player_summary?: string;
  time_remaining_minutes: number;
  mode: string;
  turn_phase?: string;
  pending_test?: PendingTest | null;
  combat_state?: CombatState | null;
  scene_mood?: string | null;
};

export type SessionDetail = GameSession & {
  character_id?: string;
  character_name?: string;
  opening_location?: string;
  tone?: string;
  paused_at?: string | null;
};

export type SessionTurnOut = {
  id: string;
  session_id: string;
  role: string;
  content: string;
  metadata?: Record<string, unknown> | null;
  created_at: string;
};

export type QuickRollResult = {
  roll: number;
  target: number;
  success: boolean;
  levels: number;
  roll_type: string;
  key: string;
  modifier: number;
  narration_hint: string;
};

export type ImageJob = {
  id: string;
  status: string;
  image_type: string;
  image_url: string | null;
  placeholder_url: string | null;
};

export type StreamEvent =
  | { type: "token"; content: string }
  | ({ type: "done" } & TurnResponse);

export type RollResultResponse = {
  roll_results: TurnResponse["roll_results"];
  turn_phase: string;
  mode: string;
  combat_state?: CombatState | null;
  fortune_current?: number | null;
  fortune_max?: number | null;
  fortune_reroll_available?: boolean;
};

export type RollHistoryEntry = {
  label: string;
  roll: number;
  target: number;
  success: boolean;
  levels: number;
  type: string;
  spontaneous?: boolean;
  timestamp: number;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}/api${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...storedAuthHeaders(),
      ...init?.headers,
    },
  });
  if (res.status === 401) {
    clearAuth();
  }
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || res.statusText);
  }
  return res.json();
}

function authRequest<T>(path: string, init?: RequestInit): Promise<T> {
  return request<T>(path, init);
}

export const api = {
  getAuthConfig: () =>
    request<AuthConfig>("/auth/config"),
  register: (email: string, password: string, password_confirm: string) =>
    request<{ user_id: string; email: string; verification_required: boolean }>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, password_confirm }),
    }),
  verifyEmail: (email: string, code: string) =>
    request<AuthResponse>("/auth/verify-email", {
      method: "POST",
      body: JSON.stringify({ email, code }),
    }),
  resendVerification: (email: string) =>
    request<{ ok: boolean }>("/auth/resend-verification", {
      method: "POST",
      body: JSON.stringify({ email }),
    }),
  login: (email: string, password: string) =>
    request<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  me: () => authRequest<AuthUser>("/auth/me"),
  listPregen: () => authRequest<Array<{ index: number; name: string; background: string; career: string }>>("/characters/pregen"),
  listSkills: () => request<SkillCatalog>("/rules/skills"),
  getCreationOptions: () => request<{ options: Record<string, unknown> }>("/rules/character-creation"),
  listCareers: (tier = 1) => request<{ careers: import("@/lib/character-creation").CareerSummary[] }>(`/rules/careers?tier=${tier}`),
  getCareer: (id: string) => request<import("@/lib/character-creation").CareerDetail>(`/rules/careers/${id}`),
  validateCreation: (draft: import("@/lib/character-creation").CharacterCreationDraft) =>
    request<{ valid: boolean; errors: Array<{ step: string; field: string; message: string }>; computed: import("@/lib/character-creation").CreationPreview | null }>(
      "/characters/validate-creation",
      { method: "POST", body: JSON.stringify({ draft }) }
    ),
  rollCreationAttributes: () => request<{ attributes: Record<string, number> }>("/characters/creation/roll-attributes", { method: "POST", body: "{}" }),
  rollCreationCareer: (draft: import("@/lib/character-creation").CharacterCreationDraft) =>
    request<{ roll: number; career: import("@/lib/character-creation").CareerDetail; career_roll_count: number; career_roll_options: string[]; xp_award: number }>(
      "/characters/creation/roll-career",
      { method: "POST", body: JSON.stringify({ draft }) }
    ),
  rollSpeciesTalent: (draft: import("@/lib/character-creation").CharacterCreationDraft) =>
    request<{ talent: string }>("/characters/creation/roll-species-talent", { method: "POST", body: JSON.stringify({ draft }) }),
  generateBackground: (body: {
    name: string;
    career: string;
    species?: string;
    talents?: string[];
    skills_summary?: string;
    trappings?: string[];
    hints?: string;
  }) => authRequest<{ background: string }>("/characters/generate-background", { method: "POST", body: JSON.stringify(body) }),
  createCharacterFromDraft: (draft: import("@/lib/character-creation").CharacterCreationDraft) =>
    authRequest<Character>("/characters", { method: "POST", body: JSON.stringify({ draft }) }),
  createPregen: (template_index: number, name?: string) =>
    authRequest<Character>("/characters/pregen", { method: "POST", body: JSON.stringify({ template_index, name }) }),
  createCharacter: (data: Partial<Character> & { name: string }) =>
    authRequest<Character>("/characters", { method: "POST", body: JSON.stringify(data) }),
  listCharacters: () => authRequest<Character[]>("/characters"),
  getCharacter: (id: string) => authRequest<Character>(`/characters/${id}`),
  listCampaigns: () => authRequest<Campaign[]>("/campaigns"),
  createCampaign: (character_id: string) =>
    authRequest<Campaign>("/campaigns", { method: "POST", body: JSON.stringify({ character_id }) }),
  completeCampaign: (campaignId: string) =>
    authRequest<Campaign>(`/campaigns/${campaignId}/complete`, { method: "POST", body: "{}" }),
  getActiveSession: (campaignId: string) =>
    authRequest<GameSession>(`/campaigns/${campaignId}/active-session`),
  getProgressionOptions: (characterId: string) =>
    authRequest<ProgressionOptions>(`/characters/${characterId}/progression`),
  startSession: (campaignId: string, duration_minutes = 45) =>
    authRequest<GameSession>(`/campaigns/${campaignId}/sessions`, {
      method: "POST",
      body: JSON.stringify({ duration_minutes }),
    }),
  sendAction: (sessionId: string, action: string) =>
    authRequest<TurnResponse>(`/sessions/${sessionId}/turn`, {
      method: "POST",
      body: JSON.stringify({ action }),
    }),
  async *streamAction(sessionId: string, action: string): AsyncGenerator<StreamEvent> {
    const res = await fetch(`${API}/api/sessions/${sessionId}/turn/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...storedAuthHeaders() },
      body: JSON.stringify({ action }),
    });
    if (!res.ok) {
      const err = await res.text();
      throw new Error(err || res.statusText);
    }
    const reader = res.body!.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split("\n\n");
      buffer = parts.pop() || "";
      for (const part of parts) {
        const line = part.trim();
        if (!line.startsWith("data:")) continue;
        const payload = line.slice(5).trim();
        if (payload) yield JSON.parse(payload) as StreamEvent;
      }
    }
    if (buffer.trim().startsWith("data:")) {
      const payload = buffer.trim().slice(5).trim();
      if (payload) yield JSON.parse(payload) as StreamEvent;
    }
  },
  rollTest: (sessionId: string, roll: number) =>
    authRequest<RollResultResponse>(`/sessions/${sessionId}/roll`, {
      method: "POST",
      body: JSON.stringify({ roll }),
    }),
  fortuneReroll: (sessionId: string, roll: number) =>
    authRequest<RollResultResponse>(`/sessions/${sessionId}/roll/fortune-reroll`, {
      method: "POST",
      body: JSON.stringify({ roll }),
    }),
  async *streamRollNarrate(sessionId: string): AsyncGenerator<StreamEvent> {
    const res = await fetch(`${API}/api/sessions/${sessionId}/roll/narrate/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...storedAuthHeaders() },
      body: "{}",
    });
    if (!res.ok) {
      const err = await res.text();
      throw new Error(err || res.statusText);
    }
    const reader = res.body!.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split("\n\n");
      buffer = parts.pop() || "";
      for (const part of parts) {
        const line = part.trim();
        if (!line.startsWith("data:")) continue;
        const payload = line.slice(5).trim();
        if (payload) yield JSON.parse(payload) as StreamEvent;
      }
    }
    if (buffer.trim().startsWith("data:")) {
      const payload = buffer.trim().slice(5).trim();
      if (payload) yield JSON.parse(payload) as StreamEvent;
    }
  },
  buySkill: (characterId: string, skill_name: string, linked_attribute: string) =>
    authRequest<Character>(`/characters/${characterId}/progression/skill`, {
      method: "POST",
      body: JSON.stringify({ skill_name, linked_attribute }),
    }),
  buyTalent: (characterId: string, talent_name: string) =>
    authRequest<Character>(`/characters/${characterId}/progression/talent`, {
      method: "POST",
      body: JSON.stringify({ talent_name }),
    }),
  getSession: (sessionId: string) => authRequest<SessionDetail>(`/sessions/${sessionId}`),
  pauseSession: (sessionId: string) =>
    authRequest<SessionDetail>(`/sessions/${sessionId}/pause`, { method: "POST", body: "{}" }),
  resumeSession: (sessionId: string) =>
    authRequest<SessionDetail>(`/sessions/${sessionId}/resume`, { method: "POST", body: "{}" }),
  getSessionHistory: (sessionId: string) =>
    authRequest<SessionTurnOut[]>(`/sessions/${sessionId}/history`),
  quickRoll: (sessionId: string, roll_type: string, key: string, modifier = 0, roll?: number) =>
    authRequest<QuickRollResult>(`/sessions/${sessionId}/quick-roll`, {
      method: "POST",
      body: JSON.stringify({ roll_type, key, modifier, ...(roll !== undefined ? { roll } : {}) }),
    }),
  getImageJob: (jobId: string) => request<ImageJob>(`/images/${jobId}`),
  getDiary: (campaignId: string) =>
    authRequest<Array<{ id: string; content: string; created_at: string }>>(`/campaigns/${campaignId}/diary`),
  listCampaignNpcs: (campaignId: string) =>
    authRequest<{ npcs: CampaignNpc[] }>(`/campaigns/${campaignId}/npcs`),
  getMap: (campaignId: string) =>
    authRequest<Array<{ name: string; description?: string; image_url?: string; revealed: boolean }>>(
      `/campaigns/${campaignId}/map`
    ),
};
