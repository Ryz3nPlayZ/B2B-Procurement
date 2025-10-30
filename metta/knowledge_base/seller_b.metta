;; ASI Seller B Knowledge Base (Margin-Focused Persona)
;; Strategy: Premium positioning, high margins, selective negotiations

;; --- Strategic Persona ---
(: persona (-> String))
(persona margin-focused)

(: strategy-instruction (-> String String))
(strategy-instruction margin-focused "Your goal is to maintain high profit margins. Only negotiate when absolutely necessary. Emphasize your premium quality, superior specifications, and brand reputation. Walk away from deals that don't meet your margin requirements.")

;; --- Product Catalog ---
(: Product (-> String String String String))
(Product TS-100 Industrial-Sensor Electronics Premium-temperature-sensor-with-superior-accuracy)

;; --- Inventory & Pricing ---
(: Inventory (-> String String Int Float))
(Inventory TS-100 premium-warehouse 200 48.00)

(: Pricing (-> String String Float String))
(Pricing TS-100 retail 119.99 standard)
(Pricing TS-100 wholesale 75 min-50-units)
(Pricing TS-100 bulk 68 min-200-units)

;; --- Negotiation Rigidity ---
(: min-acceptable-price (-> String Float))
(min-acceptable-price TS-100 70.00)  ; Will NOT go below $70

(: max-discount-percent (-> String Float))
(max-discount-percent TS-100 10.0)  ; Only 10% max discount

;; --- Business Logic ---
(: delivery-time (-> String Int))
(delivery-time TS-100 8)  ; Slower but premium service -  days

(: warranty (-> String Int))
(warranty TS-100 24)  ; 24-month warranty (2x longer)

(: specification (-> String String String))
(specification TS-100 precision ±0.2C)  ; BETTER precision
(specification TS-100 range -55C-to-150C)  ; WIDER range
(specification TS-100 origin Germany)  ; Premium origin
(specification TS-100 response-time 1-second)  ; FASTER response

;; --- Certifications ---
(: certification (-> String String String))
(certification TS-100 ISO9001 TUV-Nord)
(certification TS-100 CE TUV-SUD)
(certification TS-100 RoHS SGS)
(certification TS-100 ATEX Dekra)  ; Extra certification

;; --- LLM Instructions ---
(: llm-instruction (-> String String))
(llm-instruction system-prompt "You are a premium sales agent for Seller B. Your products are superior quality with better specifications. Generate ONLY the quote message body - no preambles. Be confident, professional, and justify your premium pricing with superior specs and warranty.")

(llm-instruction negotiation-style "Stand firm on pricing. Only offer small discounts for large orders. Emphasize your superior precision, wider temperature range, longer warranty, and German manufacturing. Make it clear you are the premium option.")