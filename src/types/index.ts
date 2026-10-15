export type TestType = 'situp' | 'vertical_jump';

export type TestStatus = 'idle' | 'recording' | 'processing' | 'success' | 'failed';

export type SyncStatus = 'synced' | 'pending';

export type NetworkStatus = 'online' | 'offline';

export interface Athlete {
  id: string;
  name: string;
  email: string;
  age?: number;
  sport?: string;
  avatarInitials: string;
}

export interface TestDefinition {
  id: TestType;
  title: string;
  shortTitle: string;
  description: string;
  duration: string;
  accent: string;
  icon: string;
}

export interface TestSession {
  id: string;
  athleteId: string;
  testType: TestType;
  startedAt: string;
  durationSeconds?: number;
  videoUri?: string;
  status: TestStatus;
  syncStatus: SyncStatus;
}

export interface SitUpResult {
  test_type: 'situp';
  repetitions: number;
  status: 'success';
}

export interface VerticalJumpResult {
  test_type: 'vertical_jump';
  jump_height_cm: number;
  status: 'success';
}

export type TestResult = SitUpResult | VerticalJumpResult;

export interface HistoryItem {
  id: string;
  testType: TestType;
  result: number;
  unit: string;
  date: string;
  duration: string;
  syncStatus: SyncStatus;
}