export type RootStackParamList = {
  Splash: undefined;
  Onboarding: undefined;
  Auth: undefined;
  Main: undefined;
  TestSelection: undefined;
  Instructions: { testType: 'situp' | 'vertical_jump' };
  Checklist: { testType: 'situp' | 'vertical_jump' };
  Camera: { testType: 'situp' | 'vertical_jump' };
  Preview: { testType: 'situp' | 'vertical_jump'; videoUri: string };
  Processing: { testType: 'situp' | 'vertical_jump'; videoUri?: string };
  Result: { testType: 'situp' | 'vertical_jump'; result: any; durationSeconds?: number };
  Performance: undefined;
  Settings: undefined;
};