# ABS Industrial Intelligence Platform

Production-grade multi-tenant SaaS platform for industrial bolt tightening integrity monitoring and engineering analytics.

## Core Capabilities

- Multi-tenant architecture with strict `tenant_id` scoping on all tenant-owned entities.
- JWT authentication and role-based access control.
- ABS internal operations portal + client read-only portal.
- Work-order ingestion from Excel and torque execution reconciliation from Excel/CSV/tool exports.
- Joint lifecycle automation (`Pending`, `In Progress`, `Certified`, `Rework Required`).
- Digital circular bolt layout with engineering status colors.
- Analytics (FPY, completion, torque-angle, heatmap, tool/operator analytics).
- AI quality monitoring (deviation/failure/tool anomaly indicators).
- PDF report generation with ABS/client branding and QR verification.
- Notifications, audit logs, subscription/billing controls, seat and usage guardrails.
- Real-time dashboard update path via tenant websocket channel.

## Architecture

- Backend: FastAPI + SQLAlchemy + PostgreSQL
- Frontend: Streamlit enterprise dashboard
- Containerization: Docker
- Cloud-ready: Kubernetes manifests with HPA for horizontal scaling

## Multi-Tenant Isolation Model

- `tenant_id` is present on all tenant-owned tables.
- Every API request resolves tenant context from JWT + optional `X-Tenant-ID` (ABS roles only).
- All queries enforce tenant filtering.
- ABS roles can switch active tenant context; client roles are tenant-bound.

## Role Matrix

- `SUPER_ADMIN`
- `ABS_ENGINEER`
- `CLIENT_ADMIN`
- `CLIENT_ENGINEER`
- `CLIENT_VIEWER` (read-only)

## Repository Structure

- `backend/app/main.py` FastAPI entrypoint + landing page
- `backend/app/models/` tenant-aware domain model
- `backend/app/api/v1/` REST APIs and websocket route
- `backend/app/services/` parsing, reconciliation, analytics, AI monitoring, reporting
- `frontend/app.py` enterprise dashboard + client portal behavior
- `deploy/docker-compose.yml` local container stack
- `deploy/k8s/` Kubernetes deployment manifests

## Database Highlights

Tables include:

- Tenancy and IAM: `tenants`, `users`
- Engineering: `projects`, `sites`, `work_orders`, `joints`, `bolts`, `executions`
- Operations: `tools`, `operators`, `notifications`, `audit_logs`, `ai_alerts`
- Reporting and branding: `reports`, `branding`
- Billing: `subscription_plans`, `tenant_subscriptions`

## Key APIs

- Auth: `/api/v1/auth/*`
- Tenants: `/api/v1/tenants`
- Projects/Sites: `/api/v1/projects*`
- Work Orders: `/api/v1/work-orders*`
- Joints/Bolts: `/api/v1/joints*`, `/api/v1/bolts*`
- Execution Sync: `/api/v1/executions/upload`
- Analytics: `/api/v1/analytics/dashboard`
- Reports + QR verify: `/api/v1/reports*`, `/api/v1/verify/{token}`
- Notifications/Audit/Billing: `/api/v1/notifications*`, `/api/v1/audit-logs`, `/api/v1/billing*`
- Realtime: `/api/v1/dashboard/ws?token=<jwt>`

## Local Run (Docker)

1. `cd deploy`
2. `docker compose up --build`
3. Access:
   - Platform: `http://localhost`
   - Backend docs: `http://localhost:8000/docs`
   - Frontend direct: `http://localhost:8501`

## Default Seed Account

- Email: `superadmin@abs.com`
- Password: `ChangeMe@123`

Change secrets and passwords before production deployment.

## Production Guidance

- Use managed PostgreSQL and Redis.
- Set strong `JWT_SECRET_KEY` and TLS.
- Configure secure object storage for logos/reports.
- Add centralized logging/metrics (CloudWatch/Azure Monitor/Prometheus).
- Enable WAF, private networking, and regular vulnerability scanning.
