# XSS Manual Testing Checklist - Quick Reference

## 🎯 Primary Test Locations
- [ ] Leave Request → Reason field
- [ ] Permission Request → Reason field  
- [ ] Other Leave → Reason field
- [ ] Admin Leave Approval page
- [ ] Leave History display

## 🧪 Test Payloads (Copy & Paste Ready)

### Basic Tests
```html
<script>alert('Test 1')</script>
<img src=x onerror=alert('Test 2')>
<svg onload=alert('Test 3')>
```

### Advanced Tests
```html
" onmouseover="alert('Test 4')"
<iframe src=javascript:alert('Test 5')></iframe>
<body onload=alert('Test 6')>
```

## 📋 Testing Procedure

### Step 1: Setup
1. Open browser → Press F12
2. Go to Console tab
3. Navigate to http://localhost:3000
4. Login to application

### Step 2: Test Each Payload
For EACH payload above:
1. Go to Leave Request form
2. Select "Sick Leave" 
3. Pick any date
4. Paste payload in Reason field
5. Click Apply
6. Watch for alert box
7. Check console for errors
8. Note results

### Step 3: Check Different Views
After submitting XSS payload:
1. Check your Leave History
2. Ask admin to check approval page
3. Logout/login and recheck

## 🔍 What You're Looking For

### ✅ XSS SUCCESS (Vulnerability Found):
- Alert box appears
- Console shows script execution
- Page content changes
- External requests in Network tab

### ✅ XSS BLOCKED (Good Security):
- Payload shows as plain text
- HTML entities in source (&lt; &gt;)
- CSP errors in console
- No script execution

## 📸 Document Everything
For each test:
- Screenshot of payload input
- Screenshot of result
- Note: Success/Blocked/Error
- Browser console messages

## 🚨 High Priority Tests

Test these first:
1. `<script>alert('XSS')</script>` in reason field
2. `<img src=x onerror=alert('XSS')>` in reason field  
3. Check if XSS shows in admin approval page
4. Test URL: `http://localhost:3000/User/Leaverequest?test=<script>alert('XSS')</script>`

## ⚡ Quick Test (2 minutes)
1. Open Leave Request form
2. Enter: `<script>alert('Quick XSS Test')</script>`
3. Submit form
4. If alert appears = VULNERABLE ❌
5. If shows as text = PROTECTED ✅
