# PHASE 11 — MOBILE PWA & ADVANCED ACCESSIBILITY SPECIFICATION

**System:** AI-Powered Workforce Management Automation System  
**Phase:** 11 — Mobile / PWA + Advanced Accessibility  
**Date:** 2026-09-27  
**Standard:** Enterprise WCAG 2.1 AA Compliance & Production PWA Architecture  

---

## 1. PWA Architecture

The system has been transformed into a fully installable, responsive, mobile-first Progressive Web App without altering or compromising any existing backend APIs, MongoDB schemas, JWT authentication, RBAC, AI/ML models, RAG chatbot, or Phase 10 integration connectors.

```text
┌────────────────────────────────────────────────────────┐
│            Browser Client / PWA Shell                  │
│   (Desktop • Laptop • Tablet • iOS Safari • Android)   │
└───────────────────────────┬────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ↓                           ↓
   ┌──────────────────────┐    ┌──────────────────────┐
   │ Service Worker Cache │    │ Auth & Live REST API │
   │ (Shell, CSS, JS, SVG)│    │ (Network Only / 503) │
   └──────────────────────┘    └──────────┬───────────┘
                                          │
                                          ↓
                               ┌──────────────────────┐
                               │   FastAPI Backend    │
                               └──────────────────────┘
```

---

## 2. Web App Manifest (`manifest.json`)

The Web App Manifest is served from `/manifest.json` with the following attributes:
- **Application Name:** `HRvantage AI Workforce Management`
- **Short Name:** `HRvantage`
- **Description:** `AI-Powered Enterprise Workforce Management Automation System - Attendance, Shifts, Leaves, Timesheets, Payroll & RAG Chatbot`
- **Start URL:** `/`
- **Scope:** `/`
- **Display Mode:** `standalone`
- **Orientation:** `any` (optimized for `portrait-primary` on mobile devices)
- **Background Color:** `#0B0F19` (matches enterprise dark theme)
- **Theme Color:** `#6366F1` (matches primary brand indigo)
- **Icons:** Scalable vector icons (`/icon-192.svg`, `/icon-512.svg`, `/favicon.svg`) with `any maskable` purposes for adaptive Android home screens.
- **Shortcuts:** Direct quick actions for "Clock In / Out" (`/attendance`), "Apply Leave" (`/leave`), "AI HR Assistant" (`/ai-assistant`), and "My Shifts" (`/shifts`).

---

## 3. Safe Service Worker Caching Strategy (`sw.js`)

In accordance with Section 5 of the Phase 11 specification:
1. **Cached Resources:**
   - Application shell: `/`, `/index.html`, `/manifest.json`
   - Static branding assets: `/favicon.svg`, `/icon-192.svg`, `/icon-512.svg`
   - Static compiled JavaScript and CSS bundles (`.js`, `.css`)
   - Web fonts (`.woff2`, `.ttf`)
2. **Strictly Never Cached (Network-Only):**
   - Authentication endpoints: `/api/v1/auth/*`
   - All REST API endpoints: `/api/*`
   - Sensitive payroll and compensation records: `/api/v1/payroll/*`
   - Private employee personal identification and salary data
   - Internal AI predictive scores (attrition probability, productivity ratings)
   - Live WebSocket connections: `ws://`, `wss://`
3. **Offline Fallback Behavior:**
   - Navigations fallback gracefully to the cached `/index.html` application shell.
   - API requests made while offline return an explicit HTTP 503 JSON payload:
     `{ "error": "NETWORK_OFFLINE", "message": "Enterprise network unavailable. Reconnect to process live HR actions.", "offline": true }`
     rather than serving stale, inaccurate employee or payroll data.

---

## 4. Attendance Offline Safety Decision

Attendance validation is legally and operationally critical. In accordance with Section 7:
- **Decision:** An offline attendance punch is **NEVER** marked as `Present`, `Approved`, or officially recorded locally.
- **Mechanism:**
  1. When offline, clicking "Punch In" or "Punch Out" enqueues a `PendingPunchEvent` in `offlineAttendanceManager`.
  2. The event is tagged with `status: "PENDING_SERVER_VERIFICATION"`, local timestamp, device ID, action type, and GPS coordinates.
  3. The employee is presented with a persistent amber warning:  
     *"⚠️ OFFLINE MODE: Recorded locally. PENDING SERVER VERIFICATION. Official check-in requires server-side identity, GPS geofence, and shift validation once connection is restored."*
  4. When connectivity returns, the queue automatically flushes through `/attendance/check-in` or `/attendance/check-out`, where the FastAPI backend enforces:
     - Geolocation coordinate proximity against office location hub (`location_id`)
     - Shift schedule and grace period calculation
     - Duplicate punch prevention
     - Anomaly detection
  5. The server result is returned and displayed to the employee.

---

## 5. Mobile Navigation & Role-Aware Layout

On screens narrower than 768px (`< 768px`):
1. **Mobile Bottom Navigation Bar (`MobileBottomNav.tsx`):**
   - Fixed at the bottom with `height: 62px` and `paddingBottom: env(safe-area-inset-bottom)`.
   - Touch targets are >= 48px x 48px.
   - **Role-Aware Tabs:**
     - **EMPLOYEE:** Home (`/employee/dashboard`), Clock (`/attendance`), Leaves (`/leave`), Shifts (`/shifts`), AI Help (`/ai-assistant`), Menu.
     - **MANAGER:** Home (`/manager/dashboard`), Team (`/manager/team`), Leaves (`/leave`), Timesheets (`/timesheets`), AI Help (`/ai-assistant`), Menu.
     - **HR / ADMIN:** Home (`/dashboard`), Staff (`/employees`), Attendance (`/attendance`), Analytics (`/reports`), AI Help (`/ai-assistant`), Menu.
2. **Mobile Navigation Drawer:**
   - Triggered via the "Menu" bottom tab or topbar hamburger button.
   - Slides smoothly over screen with a darkened glassmorphic backdrop (`.sidebar-backdrop`).
   - Includes dedicated close button `X` and auto-closes on route change.

---

## 6. Advanced Accessibility (WCAG 2.1 AA)

1. **Semantic Structure & ARIA:**
   - All interactive elements use standard HTML elements (`<button>`, `<a>`, `<input>`).
   - Badges implement `role="status"` and dynamic `aria-label` attributes (`Status: Approved`, `Status: Pending`).
   - Modals implement `role="dialog"`, `aria-modal="true"`, and `aria-labelledby="modal-dialog-title"`.
   - Screen-reader text is supported via the `.sr-only` utility.
2. **Visible Focus Outlines:**
   - Keyboard focus rings implemented via `:focus-visible` with `2px solid var(--primary)` and `outline-offset: 2px`.
3. **Reduced Motion Support:**
   - Media query `@media (prefers-reduced-motion: reduce)` disables unnecessary CSS animations, transitions, and 3D camera transforms.
   - `SceneCanvas.tsx` detects `reducedMotion` from `ThemeContext` and renders high-contrast 2D fallback cards.
4. **Color Contrast & Information Redundancy:**
   - Status indicators do not rely on color alone; every badge includes textual status and semantic icons.

---

## 7. Responsive 3D Canvas Optimization

In accordance with Section 17:
- Three.js scenes (`SceneCanvas.tsx`) detect mobile screens (`window.innerWidth < 768px`).
- Canvas height is scaled down from 350px to 240px to conserve vertical screen space.
- Device Pixel Ratio (`dpr`) is clamped to `[1, 1]` on mobile to eliminate GPU thermal throttling and reduce battery consumption.
- If WebGL is unavailable or fails, `WebGLFallback.tsx` renders a lightweight 2D card. Business operations never depend on WebGL.

---

## 8. Mobile QR & Camera Experience

- `QRScannerModal.tsx` integrates HTML5 MediaDevices camera capture for physical kiosk attendance terminals.
- Camera permissions are requested only upon explicit user interaction ("Scan QR").
- If camera access is denied or unavailable, an accessible fallback form allows manual kiosk terminal code entry (`e.g. KIOSK-BLR-01`).
