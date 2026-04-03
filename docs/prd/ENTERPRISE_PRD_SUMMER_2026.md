# ProcureOS Enterprise PRD (Summer 2026)

## 1) Executive Summary
ProcureOS is an enterprise intake-to-award procurement platform for mid-market and enterprise operators that need **faster cycle time**, **auditability**, and **AI-assisted decisioning** without ripping out ERP.

This PRD defines a product companies would pay for immediately:
- Multi-tenant procurement workspace
- Supplier master + catalog master
- RFQ workflow (draft → published → evaluated → awarded)
- Structured bid capture and weighted scoring
- Policy/role-gated approvals and awarding
- API-first backend for ERP/finance integrations

---

## 2) Market Research (why now)

### Macro demand signals
1. Public procurement alone is massive: the World Bank estimates governments spend **~$9.5T annually** and in many developing countries that is **15–22% of GDP**. This supports demand for better procurement tooling and analytics.
   - Source: World Bank, *Procurement for Development* (updated April 14, 2020): https://www.worldbank.org/en/topic/procurement-for-development

2. Independent industry estimates show strong software growth:
   - Procurement software market estimated at **$9.27B (2024)**, projected **$21.17B by 2033** (9.7% CAGR).
   - Source: Grand View Research, *Procurement Software Market*: https://www.grandviewresearch.com/industry-analysis/procurement-software-market-report

3. Venture momentum remains strong in 2025–2026 procurement automation:
   - Levelpath raised **$55M Series B** (June 30, 2025).
   - Didero raised **$30M Series A** for agentic manufacturing procurement (February 12, 2026).
   - Lio raised **$30M Series A** (March 5, 2026).
   - Source: TechCrunch:
     - https://techcrunch.com/2025/06/30/next-gen-procurement-platform-levelpath-nabs-55m/
     - https://techcrunch.com/2026/02/12/didero-lands-30m-to-put-manufacturing-procurement-on-agentic-autopilot/
     - https://techcrunch.com/2026/03/05/lio-ai-series-a-a16z-30m-raise-automate-enterprise-procurement/

### Problem definition
Enterprise procurement is still fragmented across email, spreadsheets, ERP forms, and point tools. Teams lack:
- one request-to-award workflow,
- standardized scoring and decision rationale,
- role-bound controls + audit readiness,
- fast ingestion into ERP/finance systems.

### ICP (initial customer profile)
- 500–5,000 employee companies with distributed procurement
- Sectors: manufacturing, logistics, healthcare, SaaS/IT procurement heavy organizations
- Buyer roles: VP Procurement, Head of Strategic Sourcing, Controller, Ops Finance

### Business model hypothesis
- SaaS per organization + usage bands (RFQs/year + suppliers)
- Starter: $2k–$4k/mo
- Growth: $6k–$12k/mo
- Enterprise: $25k+/mo + SSO/SLA/compliance packages

---

## 3) Product Scope

## Must-have (Phase 1)
1. Org + user management with role-based API access
2. Supplier management (category, risk, preferred)
3. Catalog item management (SKU, target price)
4. RFQ lifecycle workflow
5. Bid submission + score evaluation engine
6. Awarding workflow with rationale and immutable records
7. API-first architecture for future UI and integrations

## Should-have (Phase 2)
1. Approval chains and spend policy constraints
2. ERP adapters (NetSuite, SAP, Dynamics)
3. Contract object + renewal reminders
4. Event streaming and webhook framework

## Could-have (Phase 3)
1. Agentic quote chasing and negotiation copilots
2. Risk signals (sanctions, geopolitical disruptions)
3. Tail-spend autonomous sourcing

---

## 4) Functional Requirements

### FR-1 Multi-tenancy
- All domain objects are scoped to organization (`org_id`)
- API key auth resolves `user_id`, `org_id`, `role`

### FR-2 Access Control
- Roles: `admin`, `sourcing_manager`, `analyst`, `viewer`
- Create/publish/evaluate/award operations are role-gated

### FR-3 Supplier Master
- Create/list suppliers with risk and preferred status

### FR-4 Catalog Master
- Create/list purchasable items with target economics

### FR-5 RFQ Lifecycle
- Create RFQ in `draft`
- Publish RFQ to accept bids
- Evaluate bids with weighted strategy (`balanced`, `cost`, `quality`, `resilience`)
- Award bid with business rationale

### FR-6 Scoring Transparency
- Store per-bid sub-scores and composite score
- Deterministic scoring explainable to auditors

### FR-7 Auditability
- Persist timestamps and user-driven actions
- Keep award rationale as required text

---

## 5) Non-Functional Requirements
- API p95 < 300ms for common reads under moderate load
- Strong input validation via Pydantic models
- Referential integrity with enforced foreign keys
- Backward-compatible versioned API prefix (`/v1`)
- Testable service architecture

---

## 6) Success Metrics
- RFQ cycle-time reduction (baseline vs. 30/60/90 days)
- % RFQs with complete scoring and rationale
- Supplier response rate and award confidence
- Gross dollar value influenced through platform

---

## 7) Risks and Mitigations
- **Risk**: “Yet another procurement dashboard” perception  
  **Mitigation**: Focus on workflow automation + audit-ready outcomes.
- **Risk**: Integration friction with ERP  
  **Mitigation**: API-first + eventual prebuilt connectors.
- **Risk**: Model trust  
  **Mitigation**: deterministic scoring baseline before agentic automation.

---

## 8) Delivery Plan (8 weeks)
- **Weeks 1–2**: Core data model + API + auth
- **Weeks 3–4**: RFQ lifecycle + scoring + awarding
- **Weeks 5–6**: Approval policies + webhook events
- **Weeks 7–8**: ERP integration adapter + pilot hardening

---

## 9) Current implementation mapping (this PR)
Implemented now:
- Multi-tenant backend foundation
- Role-gated API auth via API keys
- Supplier + catalog + RFQ + bids + evaluation + awards
- SQLite relational schema with foreign keys
- Tests for end-to-end lifecycle behavior

Not yet implemented:
- SSO, full approval chains, ERP connectors, async jobs, SOC2 controls
