import { Athlete, HistoryItem, TestDefinition } from '../types';
import { colors } from '../theme';

export const mockAthlete: Athlete = {
  id: 'ATH-001',
  name: 'Arya',
  email: 'arya@example.com',
  age: 20,
  sport: 'Multi-sport',
  avatarInitials: 'AN'
};

export const testDefinitions: TestDefinition[] = [
  {
    id: 'situp',
    title: 'Sit-ups',
    shortTitle: 'Sit-ups',
    description: 'Measure core endurance with a guided repetition assessment.',
    duration: '60 sec',
    accent: colors.primary,
    icon: 'fitness'
  },
  {
    id: 'vertical_jump',
    title: 'Vertical Jump',
    shortTitle: 'Vertical Jump',
    description: 'Capture explosive lower-body performance through video.',
    duration: '45 sec',
    accent: colors.violet,
    icon: 'trending-up'
  }
];

export const initialHistory: HistoryItem[] = [
  {
    id: 'hist-1',
    testType: 'situp',
    result: 32,
    unit: 'reps',
    date: 'Today',
    duration: '01:00',
    syncStatus: 'synced'
  },
  {
    id: 'hist-2',
    testType: 'vertical_jump',
    result: 46,
    unit: 'cm',
    date: 'Yesterday',
    duration: '00:45',
    syncStatus: 'synced'
  }
];