// @ts-check
import { test, expect } from '@playwright/test';

test.describe('E-Connect Basic API Test', () => {
  test('should verify backend API is accessible', async ({ request }) => {
    // Test if the backend API is running and accessible
    try {
      console.log('Testing backend API at http://localhost:8000');
      
      // Test the backend API docs endpoint (FastAPI automatically provides this)
      const response = await request.get('http://localhost:8000/docs');
      
      console.log(`Backend API responded with status: ${response.status()}`);
      
      // FastAPI docs should return 200 or redirect (3xx)
      expect(response.status()).toBeLessThan(500);
      
      if (response.status() === 200) {
        console.log('✅ Backend API is accessible and responding correctly');
      } else if (response.status() >= 300 && response.status() < 400) {
        console.log('✅ Backend API is accessible (redirected)');
      } else {
        console.log(`⚠️ Backend API responded with status ${response.status()}`);
      }
      
    } catch (error) {
      console.log('❌ Backend API test failed:', error.message);
      throw new Error('Backend API is not accessible. Please make sure the backend server is running on port 8000.');
    }
  });
});
