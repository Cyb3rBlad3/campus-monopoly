/**
 * 与《CampusMonopoly_Improved_Rules.md》第十三节对齐的精简类型。
 * 字段以后端实际返回为准，此处用于 TypeScript 提示与联调。
 */

export interface GameSettings {
  maxPlayers: number;
  maxHandCards: number;
  parentTransferInterval: number;
  coWinRoundLimit: number;
  turnActionLimitSeconds?: number;
  turnCountdownWarnSeconds?: number;
}

export interface CurrentTurnContext {
  playerId: string;
  triggeredEventId?: string | null;
  drawnCardId?: string | null;
}

export interface SavingGoal {
  type: string;
  targetRate: number;
  targetAmount: number;
  completed: boolean;
}

export interface PlayerStats {
  partTimeCount: number;
  studyCount: number;
  socialActionCount: number;
  helpCount: number;
  lowMoodCount: number;
  averageEnergyTotal: number;
  averageEnergySamples: number;
}

export interface PlayerTurnMemory {
  lastActionType: string;
  lastWorkedTurn: number;
  consecutiveNoSocialTurns: number;
  partTimeBlockedTurns: number;
}

export interface PlayerTurnFlags {
  rolled: boolean;
  usedCard: boolean;
  tileActionUsed: boolean;
}

export interface ActionCard {
  id: string;
  name: string;
  type: string;
}

export interface PlayerStatus {
  id: string;
  name: string;
  duration: number;
  sourceCardId?: string;
  effects?: Record<string, unknown>;
}

export interface Player {
  id: string;
  name: string;
  avatarId?: string;
  pieceColor?: string;
  money: number;
  position: number;
  bankrupt: boolean;
  socialValue: number;
  financeValue: number;
  mood: number;
  energy: number;
  grade: number;
  cognition: number;
  savingGoal?: SavingGoal;
  deposits: unknown[];
  handCards: ActionCard[];
  statuses: PlayerStatus[];
  stats?: PlayerStats;
  turnMemory?: PlayerTurnMemory;
  turnFlags?: PlayerTurnFlags;
}

export interface Tile {
  id: string;
  name: string;
  type: string;
  position: number;
  cost: number;
  actions?: string[];
  icon?: string;
}

export interface GameDecks {
  actionCardDeck: unknown[];
  passiveEventDeck: unknown[];
  discardPile: unknown[];
}

export type GameStatus = "waiting" | "playing" | "finished";
export type TurnPhase = "waiting" | "awaiting_roll" | "awaiting_action" | "finished";

export interface GameState {
  gameId: string;
  roomId: string;
  status: GameStatus | string;
  round: number;
  turnIndex: number;
  currentPlayerId: string;
  initialAllowance: number;
  commonFund: number;
  publicReserve: number;
  board: Tile[];
  players: Player[];
  decks: GameDecks;
  lastResult: TurnResult | null;
  turnDeadlineAt?: string | null;
  currentTurnContext?: CurrentTurnContext | null;
  settings: GameSettings;
  turnPhase?: TurnPhase | string;
  winnerPlayerId?: string | null;
  creatorPlayerId?: string;
  version?: number;
}

export interface TurnResult {
  playerId: string;
  dice: number;
  fromPosition: number;
  toPosition: number;
  tileId: string;
  moneyDelta: number;
  moodDelta: number;
  energyDelta: number;
  gradeDelta: number;
  cognitionDelta: number;
  socialValueDelta: number;
  financeValueDelta: number;
  drawnCardId?: string;
  triggeredEventId?: string;
  messages: string[];
}
