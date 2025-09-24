# Manual Testing Checklist for E-Connect

## 🎯 Quick Manual Testing Guide

Use this checklist for manual verification of key functionality before deployment.

---

## 📋 Pre-Testing Setup

### ✅ Environment Check
- [ ] Backend server running at `http://localhost:8000`
- [ ] Frontend server running at `http://localhost:5173`
- [ ] MongoDB running at `localhost:27017`
- [ ] All terminal windows accessible
- [ ] Test browser ready (Chrome/Firefox recommended)

### ✅ Test Data Preparation
- [ ] Create test user account
- [ ] Note down test credentials
- [ ] Prepare test documents/data if needed

---

## 🔐 Authentication Testing

### User Registration
- [ ] Open frontend URL: `http://localhost:5173`
- [ ] Navigate to signup/registration
- [ ] Fill in test user details:
  - Name: `Test User Manual`
  - Email: `manual_test@econnect.com`
  - Password: `TestPassword123!`
- [ ] Click submit
- [ ] Verify success message/redirect
- [ ] Check if JWT token is stored (Developer Tools > Application > Local Storage)

### User Login
- [ ] Navigate to login page
- [ ] Enter test credentials
- [ ] Click login
- [ ] Verify successful login
- [ ] Check role-based dashboard appears
- [ ] Verify sidebar navigation is accessible

### Session Management
- [ ] Refresh the page - should stay logged in
- [ ] Close and reopen browser - check if login persists
- [ ] Test logout functionality
- [ ] Verify redirect to login page after logout

---

## ⏰ Attendance Management Testing

### Clock-in Process
- [ ] Navigate to Clock-in section
- [ ] Click "Clock In" button
- [ ] Verify timestamp appears
- [ ] Check success notification
- [ ] Verify button state changes (Clock In → Clock Out)

### Clock-out Process
- [ ] Click "Clock Out" button (after clock-in)
- [ ] Verify working hours calculation
- [ ] Check success notification
- [ ] Verify button state resets

### Attendance History
- [ ] Navigate to attendance dashboard/history
- [ ] Verify today's attendance record appears
- [ ] Check date filtering works
- [ ] Verify data formatting (time, duration)
- [ ] Test date range selection

---

## 🏖️ Leave Management Testing

### Leave Request Submission
- [ ] Navigate to Leave Request section
- [ ] Select leave type (dropdown)
- [ ] Choose future date (date picker)
- [ ] Enter reason for leave
- [ ] Submit request
- [ ] Verify success message
- [ ] Check if request appears in history

### Leave History
- [ ] Navigate to Leave History
- [ ] Verify submitted request appears
- [ ] Check status (Pending/Approved/Rejected)
- [ ] Test filtering by status/date
- [ ] Verify request details display correctly

### Leave Approval (Admin/Manager Flow)
- [ ] Login as admin/manager account
- [ ] Navigate to Leave Approval section
- [ ] Verify pending requests appear
- [ ] Test approve functionality
- [ ] Test reject functionality
- [ ] Verify status updates reflect immediately

---

## 🏠 Work from Home Testing

### WFH Request
- [ ] Navigate to Work from Home section
- [ ] Select date range for WFH
- [ ] Choose IP address (if applicable)
- [ ] Enter reason
- [ ] Submit request
- [ ] Verify confirmation message

### WFH History
- [ ] Check WFH request history
- [ ] Verify request status
- [ ] Test date filtering
- [ ] Check request details accuracy

---

## ✅ Task Management Testing

### Task Creation
- [ ] Navigate to Task section
- [ ] Click "Add Task" or similar
- [ ] Fill task details:
  - Title
  - Description
  - Due date
  - Priority
- [ ] Save task
- [ ] Verify task appears in task list

### Task Assignment (Manager)
- [ ] Login as manager
- [ ] Navigate to task assignment
- [ ] Select team members
- [ ] Assign task to multiple users
- [ ] Verify assignment confirmation

### Task Updates
- [ ] Edit existing task
- [ ] Update status (In Progress, Completed)
- [ ] Modify due date
- [ ] Save changes
- [ ] Verify updates reflect correctly

---

## 🔔 Notification System Testing

### Real-time Notifications
- [ ] Navigate to notifications section
- [ ] Check notification bell icon (unread count)
- [ ] Verify notifications display correctly
- [ ] Test mark as read functionality
- [ ] Test "Mark all as read"

### Notification Types
- [ ] Create a leave request → check for notification
- [ ] Submit attendance → check for notification
- [ ] Assign task → check for notification
- [ ] Test different priority levels (Low, Medium, High, Urgent)

### WebSocket Connection
- [ ] Open browser developer tools → Network tab
- [ ] Look for WebSocket connection
- [ ] Verify real-time updates work
- [ ] Test connection recovery (refresh page)

---

## 👥 User Management Testing (Admin)

### Employee Management
- [ ] Login as admin
- [ ] Navigate to Employee Management
- [ ] Add new employee:
  - Personal details
  - Position/Department
  - Manager assignment
- [ ] Verify employee appears in list
- [ ] Test edit employee functionality
- [ ] Test employee search/filtering

### Role-based Access
- [ ] Test different user roles:
  - Regular User permissions
  - Manager permissions
  - HR permissions
  - Admin permissions
- [ ] Verify restricted access works correctly
- [ ] Test unauthorized access handling

---

## 🔧 System Integration Testing

### Database Persistence
- [ ] Create test data (attendance, leave, task)
- [ ] Refresh browser
- [ ] Verify data persists
- [ ] Test data consistency across sessions

### Error Handling
- [ ] Test with invalid data
- [ ] Test network disconnection
- [ ] Test server errors
- [ ] Verify user-friendly error messages

### Performance
- [ ] Test page load times
- [ ] Test with multiple concurrent users
- [ ] Check memory usage (Developer Tools)
- [ ] Verify responsive behavior

---

## 📱 Responsive Design Testing

### Desktop Testing
- [ ] Test at 1920x1080 resolution
- [ ] Verify all elements visible
- [ ] Check scrolling behavior
- [ ] Test all interactive elements

### Mobile Detection
- [ ] Use browser dev tools to simulate mobile
- [ ] Verify mobile warning message appears
- [ ] Test different device sizes
- [ ] Check touch-friendly elements

---

## 🛡️ Security Testing

### Input Validation
- [ ] Test SQL injection attempts
- [ ] Test XSS attempts
- [ ] Test file upload security
- [ ] Verify input sanitization

### Authentication Security
- [ ] Test password strength requirements
- [ ] Test session timeout
- [ ] Test unauthorized API access
- [ ] Verify HTTPS enforcement

---

## 📊 Final Validation

### Cross-browser Testing
- [ ] Test in Chrome
- [ ] Test in Firefox  
- [ ] Test in Edge
- [ ] Test in Safari (if available)

### End-to-end Workflows
- [ ] Complete employee onboarding flow
- [ ] Complete leave request to approval flow
- [ ] Complete task assignment to completion flow
- [ ] Complete attendance tracking for full day

### Production Readiness
- [ ] Verify all test data can be cleaned
- [ ] Check production configuration
- [ ] Verify SSL certificates
- [ ] Test backup/restore procedures

---

## ✅ Test Completion Checklist

### Critical Issues (Must Fix)
- [ ] Authentication working
- [ ] Core attendance functionality
- [ ] Database connectivity
- [ ] Security vulnerabilities

### Important Issues (Should Fix)
- [ ] Leave management flow
- [ ] Task management
- [ ] Notification system
- [ ] User interface issues

### Nice-to-have Issues (Could Fix)
- [ ] Performance optimizations
- [ ] UI/UX improvements
- [ ] Additional features
- [ ] Mobile responsiveness

---

## 📝 Test Results Documentation

### For Each Test Section
- **Status**: ✅ Pass / ❌ Fail / ⚠️ Warning
- **Notes**: Any issues or observations
- **Screenshots**: If issues found
- **Time Taken**: Duration for each section

### Overall Assessment
- **Ready for Deployment**: Yes/No
- **Critical Issues Found**: List any blocking issues
- **Recommendations**: Next steps

---

## 🚀 Deployment Go/No-Go Decision

### Ready for Deployment If:
- ✅ All critical tests pass
- ✅ No security vulnerabilities
- ✅ Core workflows complete successfully
- ✅ Database operations stable
- ✅ Error handling working

### Not Ready for Deployment If:
- ❌ Authentication failures
- ❌ Data loss or corruption
- ❌ Security vulnerabilities
- ❌ Core functionality broken
- ❌ System instability

---

**Testing Date**: _______________
**Tester Name**: _______________
**Environment**: Development/Staging/Pre-Production
**Overall Status**: ✅ Ready / ⚠️ Needs Attention / ❌ Not Ready
