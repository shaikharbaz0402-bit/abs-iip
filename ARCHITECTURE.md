# Cloud Architecture Blueprint

## Reference Deployment

- API Tier: FastAPI containers behind load balancer
- UI Tier: Streamlit containers behind load balancer
- Data Tier: PostgreSQL (managed, HA)
- Cache/Event Tier: Redis (pub/sub and cache)
- Object Storage: S3/Azure Blob for report and logo storage
- Observability: Prometheus/Grafana + centralized logs

## Scalability

- Stateless JWT-based API servers
- Horizontal pod autoscaling for backend/frontend
- Database connection pooling and indexed tenant-aware access patterns
- Async websocket channel for dashboard update events

## Security Controls

- Role-based API guards
- Tenant-scoped filtering in all query paths
- Password hashing (bcrypt)
- Token-based access control
- Optional field-level encryption via Fernet
- Audit trail for regulated engineering workflows

## Multi-Tenant Isolation Strategy

1. Logical isolation via `tenant_id` on all tenant-owned rows.
2. Application-level tenant filters in every endpoint.
3. ABS-only cross-tenant switch via `X-Tenant-ID` with elevated roles.
4. Optional extension: PostgreSQL Row-Level Security (RLS).

## CI/CD Recommendation

- Build and scan images on pull requests.
- Run unit/integration tests.
- Promote immutable image tags to staging and production.
- Apply zero-downtime rolling updates.
