// @ts-check
import { test, expect } from '@playwright/test';

test.describe('E-Connect Dashboard Tests', () => {
  // Mock authentication for dashboard tests
  test.beforeEach(async ({ page }) => {
    // Mock localStorage with valid user data
    await page.addInitScript(() => {
      localStorage.setItem('userid', '64dc593f3a8d45840b144623');
      localStorage.setItem('name', 'Test User');
      localStorage.setItem('email', 'testuser@example.com');
      localStorage.setItem('isloggedin', 'true');
      localStorage.setItem('isadmin', 'false');
      localStorage.setItem('access_token', 'mock_access_token');
    });

    // Mock API responses
    await page.route('**/signin', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          _id: '64dc593f3a8d45840b144623',
          name: 'Test User',
          email: 'testuser@example.com',
          isloggedin: true,
          isadmin: false,
          access_token: 'mock_access_token'
        })
      });
    });

    // Mock attendance data
    await page.route('**/attendance/**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            date: new Date().toISOString(),
            clockIn: '09:00:00',
            clockOut: '17:00:00',
            status: 'Present'
          }
        ])
      });
    });
  });

  test('should display user dashboard correctly', async ({ page }) => {
    await page.goto('/User/Clockin_int');
    
    // Check if sidebar is present
    await expect(page.locator('[data-testid="sidebar"], .sidebar, nav')).toBeVisible();
    
    // Check for main dashboard content area
    await expect(page.locator('#temp, .dashboard-content, main')).toBeVisible();
  });

  test('should navigate to clock-in page', async ({ page }) => {
    await page.goto('/User/Clockin_int');
    
    // Check if we can see clock-in related elements
    // This might include clock display, clock-in button, etc.
    await expect(page).toHaveURL(/.*\/User\/Clockin_int.*/);
  });

  test('should navigate to settings page', async ({ page }) => {
    await page.goto('/User/Setting');
    
    // Verify navigation to settings
    await expect(page).toHaveURL(/.*\/User\/Setting.*/);
  });

  test('should navigate to user profile', async ({ page }) => {
    await page.goto('/User/profile');
    
    // Verify navigation to profile
    await expect(page).toHaveURL(/.*\/User\/profile.*/);
  });

  test('should navigate to leave management', async ({ page }) => {
    await page.goto('/User/Leave');
    
    // Verify navigation to leave page
    await expect(page).toHaveURL(/.*\/User\/Leave.*/);
  });

  test('should navigate to leave history', async ({ page }) => {
    await page.goto('/User/LeaveHistory');
    
    // Verify navigation to leave history
    await expect(page).toHaveURL(/.*\/User\/LeaveHistory.*/);
  });

  test('should navigate to holiday list', async ({ page }) => {
    await page.goto('/User/Holidaylist');
    
    // Verify navigation to holiday list
    await expect(page).toHaveURL(/.*\/User\/Holidaylist.*/);
  });

  test('should navigate to work from home', async ({ page }) => {
    await page.goto('/User/Workfromhome');
    
    // Verify navigation to WFH page
    await expect(page).toHaveURL(/.*\/User\/Workfromhome.*/);
  });

  test('should navigate to todo list', async ({ page }) => {
    await page.goto('/User/todo');
    
    // Verify navigation to todo page
    await expect(page).toHaveURL(/.*\/User\/todo.*/);
  });

  test('should navigate to task page', async ({ page }) => {
    await page.goto('/User/task');
    
    // Verify navigation to task page
    await expect(page).toHaveURL(/.*\/User\/task.*/);
  });

  test('should navigate to notifications', async ({ page }) => {
    await page.goto('/User/notifications');
    
    // Verify navigation to notifications
    await expect(page).toHaveURL(/.*\/User\/notifications.*/);
  });

  test('should handle API test page', async ({ page }) => {
    await page.goto('/User/test');
    
    // Verify navigation to API test page
    await expect(page).toHaveURL(/.*\/User\/test.*/);
  });
});

test.describe('E-Connect Admin Dashboard Tests', () => {
  // Mock admin authentication
  test.beforeEach(async ({ page }) => {
    // Mock localStorage with admin user data
    await page.addInitScript(() => {
      localStorage.setItem('userid', '64dc593f3a8d45840b144624');
      localStorage.setItem('name', 'Admin User');
      localStorage.setItem('email', 'admin@example.com');
      localStorage.setItem('isloggedin', 'true');
      localStorage.setItem('isadmin', 'true');
      localStorage.setItem('access_token', 'mock_admin_token');
    });

    // Mock admin API responses
    await page.route('**/signin', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          _id: '64dc593f3a8d45840b144624',
          name: 'Admin User',
          email: 'admin@example.com',
          isloggedin: true,
          isadmin: true,
          access_token: 'mock_admin_token'
        })
      });
    });
  });

  test('should display admin dashboard correctly', async ({ page }) => {
    await page.goto('/admin/time');
    
    // Check if admin dashboard loads
    await expect(page).toHaveURL(/.*\/admin\/time.*/);
  });

  test('should navigate to leave management (admin)', async ({ page }) => {
    await page.goto('/admin/leave');
    
    // Verify admin leave management page
    await expect(page).toHaveURL(/.*\/admin\/leave.*/);
  });

  test('should navigate to employee list', async ({ page }) => {
    await page.goto('/admin/employees');
    
    // Verify employee list page
    await expect(page).toHaveURL(/.*\/admin\/employees.*/);
  });

  test('should navigate to leave approval', async ({ page }) => {
    await page.goto('/admin/leave-approval');
    
    // Verify leave approval page
    await expect(page).toHaveURL(/.*\/admin\/leave-approval.*/);
  });

  test('should navigate to work from home approval', async ({ page }) => {
    await page.goto('/admin/wfh-approval');
    
    // Verify WFH approval page
    await expect(page).toHaveURL(/.*\/admin\/wfh-approval.*/);
  });

  test('should navigate to admin profile', async ({ page }) => {
    await page.goto('/admin/profile');
    
    // Verify admin profile page
    await expect(page).toHaveURL(/.*\/admin\/profile.*/);
  });
});
