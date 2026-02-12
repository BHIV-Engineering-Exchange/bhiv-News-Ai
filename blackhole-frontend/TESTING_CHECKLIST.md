# 🧪 Testing Checklist - News AI Frontend

## Pre-Testing Setup

- [ ] Backend server is running on `http://localhost:8000`
- [ ] Frontend is running on `http://localhost:3000`
- [ ] Environment variables are configured
- [ ] Browser console is open for error checking
- [ ] Network tab is open to monitor API calls

---

## 1. End-to-End Flow Testing

### Test Case 1: Complete News Analysis Pipeline
**Steps:**
1. [ ] Navigate to home page (`/`)
2. [ ] Enter a valid news URL (e.g., `https://www.bbc.com/news/technology`)
3. [ ] Click "Analyze" button
4. [ ] Verify loading states appear
5. [ ] Verify pipeline stages update in real-time
6. [ ] Verify results display after completion
7. [ ] Verify all components render correctly:
   - [ ] Scraped data section
   - [ ] Authenticity score
   - [ ] Summary text
   - [ ] Pipeline viewer
   - [ ] Video sidebar
   - [ ] TTS player (if audio available)

**Expected Results:**
- All pipeline stages complete successfully
- Results display within 15-30 seconds
- No console errors
- All UI components visible

---

### Test Case 2: Backend Offline (Mock Data)
**Steps:**
1. [ ] Stop backend server
2. [ ] Refresh frontend page
3. [ ] Enter a news URL
4. [ ] Click "Analyze" button
5. [ ] Verify mock data is used
6. [ ] Verify error message or offline indicator appears

**Expected Results:**
- Mock data displays correctly
- User is informed backend is offline
- App still functions with mock data

---

### Test Case 3: Invalid URL Handling
**Steps:**
1. [ ] Enter invalid URL (e.g., `not-a-url`)
2. [ ] Click "Analyze" button
3. [ ] Verify error message appears
4. [ ] Verify error is user-friendly

**Expected Results:**
- Clear error message displayed
- No app crash
- User can retry with valid URL

---

## 2. Component Testing

### TTS Player Component
- [ ] Audio loads correctly
- [ ] Play button works
- [ ] Pause button works
- [ ] Restart button works
- [ ] Volume slider works
- [ ] Mute button works
- [ ] Progress bar updates during playback
- [ ] Seek functionality works
- [ ] Duration displays correctly
- [ ] Handles missing audio gracefully

### Pipeline Viewer Component
- [ ] All 6 stages display correctly
- [ ] Status indicators show correct states:
  - [ ] Completed (green checkmark)
  - [ ] Processing (spinning loader)
  - [ ] Pending (gray clock)
  - [ ] Failed (red alert)
- [ ] Timestamps display correctly
- [ ] Connector lines show correct colors
- [ ] Compact mode works (if applicable)

### AI Insights Component
- [ ] Sentiment displays correctly
- [ ] Tone displays correctly
- [ ] Credibility score displays (0-100%)
- [ ] Bias score displays
- [ ] Keywords list displays
- [ ] Entities list displays
- [ ] Visual indicators (progress bars, badges) work

### Feedback Panel Component
- [ ] Like button works
- [ ] Skip button works
- [ ] Approve button works
- [ ] Flag button works
- [ ] Toast notification appears on submit
- [ ] Feedback is stored in localStorage
- [ ] Feedback is sent to backend API
- [ ] Flag form appears when flagging
- [ ] Flag requires reason input

### Live Feed Viewer Component
- [ ] News items display in list
- [ ] Category filter works
- [ ] Status filter works
- [ ] Item selection works
- [ ] Selected item highlights correctly
- [ ] Empty state displays when no items
- [ ] Loading state displays while fetching

---

## 3. API Integration Testing

### Health Check Endpoint
- [ ] `GET /health` returns correct response
- [ ] Backend status indicator updates
- [ ] Status shows "online" when backend is up
- [ ] Status shows "offline" when backend is down

### Unified Workflow Endpoint
- [ ] `POST /api/unified-news-workflow` sends correct request
- [ ] Response is parsed correctly
- [ ] Error handling works for failed requests
- [ ] Timeout handling works (if implemented)

### News Items Endpoint
- [ ] `GET /api/news` returns list of items
- [ ] Category filter works
- [ ] Status filter works
- [ ] Limit parameter works
- [ ] Empty response handled gracefully

### Feedback Endpoint
- [ ] `POST /api/feedback` sends correct payload
- [ ] Success response handled
- [ ] Error response handled
- [ ] Feedback persists in localStorage

---

## 4. Error Handling Testing

### Network Errors
- [ ] Handles network timeout
- [ ] Handles connection refused
- [ ] Handles 404 errors
- [ ] Handles 500 errors
- [ ] Error messages are user-friendly
- [ ] Retry mechanism works (if implemented)

### Data Validation Errors
- [ ] Handles missing required fields
- [ ] Handles invalid data types
- [ ] Handles null/undefined values
- [ ] Handles malformed JSON

### UI Error States
- [ ] Empty states display correctly
- [ ] Error states display correctly
- [ ] Loading states display correctly
- [ ] No infinite loading spinners

---

## 5. Responsive Design Testing

### Mobile (< 768px)
- [ ] Layout adapts to mobile
- [ ] Navigation works on mobile
- [ ] Components stack vertically
- [ ] Touch interactions work
- [ ] Text is readable
- [ ] Buttons are tappable

### Tablet (768px - 1280px)
- [ ] Layout adapts to tablet
- [ ] 2-column layout works
- [ ] Components resize appropriately

### Desktop (> 1280px)
- [ ] 3+ column layout works
- [ ] Sidebar displays correctly
- [ ] All components visible
- [ ] Hover states work

---

## 6. Performance Testing

### Load Time
- [ ] Initial page load < 3 seconds
- [ ] API responses < 5 seconds
- [ ] No blocking operations

### Bundle Size
- [ ] Run `npm run build`
- [ ] Check bundle size
- [ ] Verify no unnecessary dependencies
- [ ] Verify code splitting works

### Memory Leaks
- [ ] No memory leaks in console
- [ ] Event listeners cleaned up
- [ ] Timers cleared on unmount

---

## 7. Browser Compatibility Testing

Test in multiple browsers:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

---

## 8. Accessibility Testing

- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] Color contrast meets WCAG standards
- [ ] Alt text on images
- [ ] ARIA labels where needed
- [ ] Focus indicators visible

---

## 9. LocalStorage Testing

- [ ] Feedback history persists
- [ ] Data survives page refresh
- [ ] Data clears when needed
- [ ] No localStorage errors

---

## 10. Integration with Backend Team

### With Noopur (Backend Schema)
- [ ] JSON schema matches frontend expectations
- [ ] All required fields present
- [ ] Data types match
- [ ] Error responses handled

### With Seeya (Orchestration)
- [ ] Workflow endpoint compatible
- [ ] Pipeline status updates work
- [ ] Real-time updates work (if implemented)

### With Sankalp (Audio + Insights)
- [ ] TTS audio format compatible
- [ ] Audio URLs work
- [ ] Insight data structure matches
- [ ] Sentiment/tone values match

---

## Bug Report Template

When reporting bugs, include:

```
**Bug Title**: [Brief description]

**Steps to Reproduce**:
1. 
2. 
3. 

**Expected Behavior**:
[What should happen]

**Actual Behavior**:
[What actually happens]

**Environment**:
- Browser: [Chrome/Firefox/etc]
- OS: [Windows/Mac/Linux]
- Backend Status: [Online/Offline]

**Console Errors**:
[Any console errors]

**Screenshots**:
[If applicable]
```

---

## Test Results Summary

**Date**: _______________
**Tester**: _______________
**Environment**: _______________

**Total Tests**: _______
**Passed**: _______
**Failed**: _______
**Skipped**: _______

**Critical Issues**: _______
**Major Issues**: _______
**Minor Issues**: _______

**Notes**:
_____________________________________________________________
_____________________________________________________________
_____________________________________________________________

---

*Last Updated: January 2025*

