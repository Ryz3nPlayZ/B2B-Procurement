;; ASI Buyer Schema MeTTa Definitions
;; Defines buyer-specific types and relationships

;; Buyer agent types
(: Buyer (-> String String String))  ; Buyer(id, type, status)
(: Procurement (-> String String String))  ; Procurement(id, type, status)
(: RFQ (-> String String String))  ; RFQ(id, buyer-id, status)
(: Evaluation (-> String String Float))  ; Evaluation(id, criteria, score)

;; Procurement process types
(: Process (-> String String String))  ; Process(id, name, stage)
(: Stage (-> String String String))  ; Stage(id, name, process)
(: Workflow (-> String String String))  ; Workflow(id, name, status)

;; Requirement types
(: Requirement (-> String String String))  ; Requirement(id, type, description)
(: Specification (-> String String String))  ; Specification(id, type, details)
(: Constraint (-> String String String))  ; Constraint(id, type, condition)

;; Policy and rule types
(: Policy (-> String String String))  ; Policy(id, name, description)
(: Rule (-> String String String))  ; Rule(id, name, condition)
(: Guideline (-> String String String))  ; Guideline(id, name, instruction)

;; Budget and financial types
(: Budget (-> String String Float))  ; Budget(id, period, amount)
(: Allocation (-> String String Float))  ; Allocation(id, category, amount)
(: Approval (-> String String String))  ; Approval(id, level, status)

;; Vendor and supplier types
(: Vendor (-> String String String))  ; Vendor(id, name, status)
(: Supplier (-> String String String))  ; Supplier(id, name, category)
(: Relationship (-> String String String))  ; Relationship(id, type, status)

;; Evaluation and scoring types
(: Score (-> String String Float))  ; Score(id, criteria, value)
(: Criteria (-> String String Float))  ; Criteria(id, name, weight)
(: Rating (-> String String Float))  ; Rating(id, scale, value)

;; Negotiation types
(: Negotiation (-> String String String))  ; Negotiation(id, type, status)
(: Strategy (-> String String String))  ; Strategy(id, name, approach)
(: Tactic (-> String String String))  ; Tactic(id, name, method)

;; Decision support types
(: Decision (-> String String String))  ; Decision(id, type, outcome)
(: Recommendation (-> String String String))  ; Recommendation(id, type, advice)
(: Analysis (-> String String String))  ; Analysis(id, type, result)

;; Risk and compliance types
(: Risk (-> String String Float))  ; Risk(id, type, level)
(: Compliance (-> String String String))  ; Compliance(id, regulation, status)
(: Audit (-> String String String))  ; Audit(id, type, result)

;; Performance and metrics types
(: Metric (-> String String Float))  ; Metric(id, name, value)
(: KPI (-> String String Float))  ; KPI(id, name, target)
(: Benchmark (-> String String Float))  ; Benchmark(id, category, value)

;; Communication and notification types
(: Notification (-> String String String))  ; Notification(id, type, message)
(: Alert (-> String String String))  ; Alert(id, type, condition)
(: Report (-> String String String))  ; Report(id, type, content)

;; Integration and workflow types
(: Integration (-> String String String))  ; Integration(id, system, status)
(: Workflow (-> String String String))  ; Workflow(id, name, status)
(: Process (-> String String String))  ; Process(id, name, type)

;; Buyer-specific relationships
(: has-requirement (-> String String))  ; has-requirement(buyer-id, requirement-id)
(: follows-policy (-> String String))  ; follows-policy(buyer-id, policy-id)
(: evaluates-vendor (-> String String))  ; evaluates-vendor(buyer-id, vendor-id)
(: negotiates-with (-> String String))  ; negotiates-with(buyer-id, seller-id)

;; Procurement workflow states
(: workflow-state (-> String String))  ; workflow-state(process-id, state)
(: stage-completion (-> String String))  ; stage-completion(stage-id, status)
(: approval-status (-> String String))  ; approval-status(decision-id, status)

;; Buyer capabilities and constraints
(: capability (-> String String String))  ; capability(buyer-id, type, level)
(: constraint (-> String String String))  ; constraint(buyer-id, type, limit)
(: preference (-> String String String))  ; preference(buyer-id, type, value)

;; Market and competitive intelligence
(: market-data (-> String String String))  ; market-data(category, source, data)
(: competitor (-> String String String))  ; competitor(id, name, position)
(: trend (-> String String String))  ; trend(category, direction, confidence)

;; Quality and standards
(: quality-standard (-> String String String))  ; quality-standard(id, organization, requirement)
(: certification (-> String String String))  ; certification(id, type, issuer)
(: compliance-requirement (-> String String String))  ; compliance-requirement(id, regulation, requirement)

;; Financial and budget management
(: budget-category (-> String String Float))  ; budget-category(id, name, amount)
(: cost-center (-> String String String))  ; cost-center(id, name, manager)
(: approval-level (-> String String String))  ; approval-level(id, amount, approver)

;; Decision support functions
(: should-negotiate (-> String String))  ; should-negotiate(quote-id, reason)
(: can-approve (-> String String String))  ; can-approve(approver, amount, conditions)
(: risk-assessment (-> String String))  ; risk-assessment(vendor-id, level)
(: optimal-strategy (-> String String String))  ; optimal-strategy(situation, context, strategy)

