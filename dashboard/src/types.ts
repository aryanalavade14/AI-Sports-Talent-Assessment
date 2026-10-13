// These mirror the backend response models in app/schemas/dashboard.py.

export type TestKey = 'vertical_jump' | 'sit_up';

export const TEST_LABEL: Record<TestKey, string> = { vertical_jump: 'Vertical Jump', sit_up: 'Sit-ups' };
export const TEST_UNIT: Record<TestKey, string> = { vertical_jump: 'cm', sit_up: 'reps' };

export interface TestScore {
  result_id: string;
  value: number;
  unit: string;
  percentile: number | null;
  level: string | null;
  norm_reference: string | null;
  norm_median: number | null;
  tested_at: string;
}

export interface AthleteRow {
  athlete_id: string;
  name: string;
  age: number;
  gender: string;
  sport: string | null;
  state: string | null;
  city: string | null;
  region: string | null;
  vertical_jump: TestScore | null;
  sit_up: TestScore | null;
  tests_taken: number;
  overall_percentile: number | null;
  overall_level: string | null;
  flagged_results: number;
  shortlisted: boolean;
}

export interface LeaderboardRow extends AthleteRow {
  rank: number;
}

export interface CountItem { label: string; count: number }
export interface AvgItem { label: string; average_percentile: number; athletes: number }

export interface Summary {
  total_athletes: number;
  athletes_tested: number;
  total_results: number;
  shortlisted: number;
  flagged_results: number;
  average_percentile: number | null;
  average_vertical_jump_cm: number | null;
  average_sit_ups: number | null;
  levels: CountItem[];
  by_region: CountItem[];
  by_sport: AvgItem[];
  by_gender: CountItem[];
}

export interface FilterOptions {
  regions: string[];
  sports: string[];
  genders: string[];
  age_min: number | null;
  age_max: number | null;
}

export interface ShortlistEntry { athlete: AthleteRow; note: string | null; shortlisted_at: string }

export interface Norm {
  test_type: TestKey;
  gender: string;
  age_min: number;
  age_max: number;
  unit: string;
  p10: number; p25: number; p50: number; p75: number; p90: number;
  source: string;
}

export interface Evaluation {
  test_type: TestKey;
  gender: string;
  age: number;
  value: number;
  percentile: number;
  level: string;
  norm_reference: string;
  median: number;
}

export interface Filters { region: string; sport: string; gender: string; ageMin: string; ageMax: string }
export const NO_FILTERS: Filters = { region: '', sport: '', gender: '', ageMin: '', ageMax: '' };
