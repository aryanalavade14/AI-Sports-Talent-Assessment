import { TestType, TestResult } from '../types';

const API_BASE_URL = 'https://example.com/api';

export interface UploadPayload {
  athlete_id: string;
  test_type: TestType;
  video: string;
}

export async function uploadAssessment(_payload: UploadPayload): Promise<TestResult> {
  // Integration boundary for the real backend.
  // Replace this mock implementation when the team backend is available.
  throw new Error('Real backend is not connected. Use analyzeTest() for local demo mode.');
}

export { API_BASE_URL };