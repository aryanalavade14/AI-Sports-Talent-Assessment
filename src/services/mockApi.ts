import { TestResult, TestType } from '../types';

export async function analyzeTest(testType: TestType, _videoUri?: string): Promise<TestResult> {
  await new Promise((resolve) => setTimeout(resolve, 1600));

  if (testType === 'situp') {
    return { test_type: 'situp', repetitions: 32, status: 'success' };
  }

  return { test_type: 'vertical_jump', jump_height_cm: 46, status: 'success' };
}