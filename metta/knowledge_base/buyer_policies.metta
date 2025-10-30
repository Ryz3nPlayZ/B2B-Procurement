;; ASI Buyer Knowledge Base

;; --- Procurement Requirements ---
(: procurement-need (-> String Int Float))
(procurement-need TS-100 50 75.00)  ; Need 50 units, budget $75/unit max

;; --- Required Specifications ---
(: required-spec (-> String String String))
(required-spec TS-100 precision ±1.0C-or-better)
(required-spec TS-100 range -40C-to-125C-minimum)

;; --- Required Certifications ---
(: required-certification (-> String String))
(required-certification TS-100 ISO9001)

;; --- Evaluation Criteria (weights) ---
(: evaluation-weight (-> String Float))
(evaluation-weight price 0.50)
(evaluation-weight delivery-time 0.20)
(evaluation-weight warranty 0.15)
(evaluation-weight precision 0.15)

;; --- LLM Instructions ---
(: llm-instruction (-> String String))
(llm-instruction system-prompt "You are a strategic procurement agent. Analyze quotes objectively based on price, delivery, warranty, and specifications. Be willing to negotiate but know when to walk away.")