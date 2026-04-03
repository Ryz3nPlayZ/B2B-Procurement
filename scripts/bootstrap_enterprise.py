"""Bootstrap ProcureOS with a first organization and admin user.

Usage:
  python scripts/bootstrap_enterprise.py --org "Acme" --email "admin@acme.com"
"""

from __future__ import annotations

import argparse

from backend.db.database import init_db
from backend.schemas.models import OrganizationCreate, UserCreate
from backend.services.procurement import create_organization, create_user


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--org", required=True, help="Organization name")
    parser.add_argument("--plan", default="enterprise", choices=["starter", "growth", "enterprise"])
    parser.add_argument("--email", required=True, help="Admin email")
    parser.add_argument("--role", default="admin", choices=["admin", "sourcing_manager", "analyst", "viewer"])
    args = parser.parse_args()

    init_db()
    org = create_organization(OrganizationCreate(name=args.org, plan=args.plan))
    user = create_user(UserCreate(org_id=org["id"], email=args.email, role=args.role))

    print("Bootstrap complete")
    print(f"org_id={org['id']}")
    print(f"user_id={user['id']}")
    print(f"api_key={user['api_key']}")


if __name__ == "__main__":
    main()
