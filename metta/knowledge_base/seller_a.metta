;; ASI Seller A Knowledge Base (Deal-Focused Persona)
;; Strategy: Win deals through flexibility, speed, and competitive pricing

;; --- Strategic Persona ---
(: persona (-> String))
(persona deal-focused)

(: strategy-instruction (-> String String))
(strategy-instruction deal-focused "Your primary goal is to win the deal. Be flexible on price and terms to secure the contract. Emphasize your speed, reliability, and value for money. You are willing to negotiate and offer discounts to close deals.")

;; --- Product Catalog ---
(: Product (-> String String String String))
(Product TS-100 Industrial-Sensor Electronics High-precision-temperature-sensor-for-industrial-applications)

;; --- Inventory & Pricing ---
(: Inventory (-> String String Int Float))
(Inventory TS-100 main-warehouse 500 42.00)

(: Pricing (-> String String Float String))
(Pricing TS-100 retail 89.99 standard)
(Pricing TS-100 wholesale 65.00 min-50-units)
(Pricing TS-100 bulk 55.00 min-100-units)

;; --- Negotiation Flexibility ---
(: min-acceptable-price (-> String Float))
(min-acceptable-price TS-100 62.00)  ; Will go as low as \$62 to win (CHANGED from \$50)

(: max-discount-percent (-> String Float))
(max-discount-percent TS-100 25.0)  ; Can discount up to 25%

;; --- Business Logic ---
(: delivery-time (-> String Int))
(delivery-time TS-100 5)  ; Fast delivery - 5 days

(: warranty (-> String Int))
(warranty TS-100 12)  ; 12-month warranty

(: specification (-> String String String))
(specification TS-100 precision ±0.5C)
(specification TS-100 range -40C-to-125C)
(specification TS-100 origin Vietnam)
(specification TS-100 response-time 2-seconds)

;; --- Certifications ---
(: certification (-> String String String))
(certification TS-100 ISO9001 Bureau-Veritas)
(certification TS-100 CE TUV-SUD)
(certification TS-100 RoHS Intertek)

;; --- LLM Instructions ---
(: llm-instruction (-> String String))
(llm-instruction system-prompt "You are a pragmatic and efficient sales agent for Seller A. Your goal is to win the deal through competitive pricing and fast delivery. Be willing to negotiate. Generate ONLY the quote message body - no preambles. Be direct, friendly, and focus on value and speed.")

(llm-instruction negotiation-style "Be flexible and accommodating. If the buyer pushes back on price, offer discounts or bundle deals. Emphasize your fast 5-day delivery and willingness to work with their budget.")