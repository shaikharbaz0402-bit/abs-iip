from __future__ import annotations

from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import get_password_hash
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.billing import SubscriptionPlan, TenantSubscription
from app.models.enums import PlanType, UserRole
from app.models.tenant import Tenant
from app.models.user import User


def init_db() -> None:
    Base.metadata.create_all(bind=engine)

    settings = get_settings()
    with SessionLocal() as db:
        plans = {
            PlanType.BASIC: (499.0, 10, 5000),
            PlanType.PROFESSIONAL: (1499.0, 50, 50000),
            PlanType.ENTERPRISE: (4999.0, 500, 500000),
        }

        for plan_name, (price, seats, usage) in plans.items():
            exists = db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.name == plan_name))
            if exists is None:
                db.add(
                    SubscriptionPlan(
                        name=plan_name,
                        monthly_price=price,
                        seat_limit=seats,
                        usage_limit=usage,
                    )
                )

        tenant = db.scalar(select(Tenant).where(Tenant.slug == "abs-internal"))
        if tenant is None:
            tenant = Tenant(
                name="ABS Internal",
                slug="abs-internal",
                contact_email=settings.seed_super_admin_email,
            )
            db.add(tenant)
            db.flush()

        plan = db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.name == PlanType.ENTERPRISE))
        subscription = db.scalar(
            select(TenantSubscription).where(TenantSubscription.tenant_id == tenant.id)
        )
        if subscription is None and plan is not None:
            db.add(
                TenantSubscription(
                    tenant_id=tenant.id,
                    plan_id=plan.id,
                )
            )

        user = db.scalar(select(User).where(User.tenant_id == tenant.id, User.email == settings.seed_super_admin_email))
        if user is None:
            db.add(
                User(
                    tenant_id=tenant.id,
                    email=settings.seed_super_admin_email,
                    full_name="ABS Super Admin",
                    hashed_password=get_password_hash(settings.seed_super_admin_password),
                    role=UserRole.SUPER_ADMIN,
                    is_active=True,
                )
            )

        db.commit()


if __name__ == "__main__":
    init_db()
