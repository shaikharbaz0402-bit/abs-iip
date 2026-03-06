# ABS IIP Frontend (Enterprise Multi-Portal)

Enterprise-grade frontend for ABS Industrial Intelligence Platform.

## Stack

- React 18
- Vite
- TypeScript
- Tailwind CSS
- Headless UI
- Recharts
- xlsx

## Portals

- ABS Admin Center (`SUPER_ADMIN`, `ABS_ENGINEER`)
- Project Manager Portal (`CLIENT_ADMIN`)
- Operator Portal (`CLIENT_ENGINEER`)
- Client Portal (`CLIENT_VIEWER`, read-only)

## Admin Center Modules

- Dashboard
- Tenants
- Projects
- Work Orders
- Operators
- Tools
- Analytics
- Reports
- Users
- Billing
- Audit Logs
- Platform Settings (GUI preferences)
- Branding Settings (logo preview + theme controls)

## Run

1. Copy `.env.example` to `.env`.
2. Install dependencies:

```bash
npm install
```

3. Start development server:

```bash
npm run dev
```

Dev port is `http://localhost:3000` to match backend CORS defaults.

## Environment

`VITE_API_BASE_URL` defaults to:

`https://abs-iip-production.up.railway.app`

Override in `.env` if needed.

## Implementation Notes

- Backend was not modified.
- Frontend integrates with existing `/api/v1/*` contracts only.
- JWT + tenant context are managed in a centralized API client.
- 401 handling is centralized and logs out invalid sessions.
- Operator workflow includes drag/drop Excel upload, validation preview, and upload progress.
- Platform settings are GUI-driven and stored client-side unless a backend settings API is added.
