declare module "@3d-dice/dice-box" {
  interface DiceBoxConfig {
    /** CSS selector or DOM element to place the dice box canvas in. Defaults to document.body */
    container?: string | HTMLElement;
    /** The ID of the canvas element. Default: 'dice-canvas' */
    id?: string;
    /** Path to static assets. Required. */
    assetPath: string;
    gravity?: number;
    mass?: number;
    friction?: number;
    restitution?: number;
    angularDamping?: number;
    linearDamping?: number;
    spinForce?: number;
    throwForce?: number;
    startingHeight?: number;
    settleTimeout?: number;
    offscreen?: boolean;
    delay?: number;
    lightIntensity?: number;
    enableShadows?: boolean;
    shadowTransparency?: number;
    theme?: string;
    preloadThemes?: string[];
    externalThemes?: Record<string, string>;
    themeColor?: string;
    scale?: number;
    suspendSimulation?: boolean;
    origin?: string;
    onBeforeRoll?: (notation: unknown) => void;
    onDieComplete?: (result: DieResult) => void;
    onRollComplete?: (results: RollResultGroup[]) => void;
    onRemoveComplete?: (result: DieResult) => void;
    onThemeConfigLoaded?: (config: unknown) => void;
    onThemeLoaded?: (config: unknown) => void;
  }

  interface DieResult {
    groupId: number;
    rollId: number;
    sides: number;
    theme: string;
    themeColor?: string;
    value: number;
  }

  interface RollResultGroup {
    id: number;
    mods: unknown[];
    qty: number;
    rolls: DieResult[];
    sides: number;
    theme: string;
    themeColor?: string;
    value: number;
  }

  export default class DiceBox {
    /** v1.1 API: single config object. Use `container` property for the DOM selector. */
    constructor(config: DiceBoxConfig);
    init(): Promise<void>;
    roll(
      notation: string | object | Array<string | object>,
      options?: { theme?: string; newStartPoint?: boolean }
    ): Promise<RollResultGroup[]>;
    add(
      notation: string | object | Array<string | object>,
      options?: { theme?: string; newStartPoint?: boolean }
    ): Promise<RollResultGroup[]>;
    reroll(
      notation: object | object[],
      options?: { remove?: boolean; newStartPoint?: boolean }
    ): Promise<RollResultGroup[]>;
    remove(notation: object | object[]): Promise<RollResultGroup[]>;
    clear(): Promise<void>;
    hide(className?: string): void;
    show(): void;
    getRollResults(): RollResultGroup[];
    updateConfig(config: Partial<DiceBoxConfig>): void;
    onRollComplete: ((results: RollResultGroup[]) => void) | undefined;
    onDieComplete: ((result: DieResult) => void) | undefined;
    onBeforeRoll: ((notation: unknown) => void) | undefined;
    onRemoveComplete: ((result: DieResult) => void) | undefined;
    onThemeConfigLoaded: ((config: unknown) => void) | undefined;
    onThemeLoaded: ((config: unknown) => void) | undefined;
  }
}
