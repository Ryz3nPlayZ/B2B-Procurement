;; ASI Seller C Knowledge Base
;; Contains catalog, pricing rules, and business logic for Seller C

;; Base product types
(: Product (-> String String String String))  ; Product(id, name, category, description)
(: Inventory (-> String String Int Float))      ; Inventory(product-id, location, quantity, cost)
(: Pricing (-> String String Float String))    ; Pricing(product-id, tier, price, conditions)

;; Seller C's product catalog
(Product "C001" "Raw Materials" "Materials" "Steel, aluminum, and composite materials")
(Product "C002" "Components" "Manufacturing" "Precision machined components and parts")
(Product "C003" "Packaging" "Logistics" "Custom packaging and shipping materials")
(Product "C004" "Logistics Services" "Services" "Warehousing, distribution, and fulfillment")

;; Inventory levels
(Inventory "C001" "mill-1" 5000 2.50)
(Inventory "C001" "mill-2" 3000 2.50)
(Inventory "C002" "factory-1" 2000 15.75)
(Inventory "C002" "factory-2" 1500 15.75)
(Inventory "C003" "warehouse-1" 10000 0.85)
(Inventory "C003" "warehouse-2" 8000 0.85)

;; Pricing tiers
(Pricing "C001" "spot" 3.25 "immediate-delivery")
(Pricing "C001" "contract" 2.75 "min-1000-tons")
(Pricing "C001" "futures" 2.50 "6-month-contract")
(Pricing "C002" "standard" 18.50 "standard-specs")
(Pricing "C002" "custom" 25.00 "custom-machining")
(Pricing "C002" "bulk" 16.75 "min-10000-units")
(Pricing "C003" "standard" 1.25 "standard-sizes")
(Pricing "C003" "custom" 2.50 "custom-design")
(Pricing "C004" "storage" 0.15 "per-cubic-foot-month")
(Pricing "C004" "handling" 0.05 "per-pound")

;; Supply chain capabilities
(: supplier-network (-> String String String))  ; supplier(vendor-id, category, reliability)
(supplier-network "S001" "raw-materials" "high")
(supplier-network "S002" "machining" "high")
(supplier-network "S003" "packaging" "medium")
(supplier-network "S004" "logistics" "high")

;; Quality standards
(: quality-standard (-> String String String))  ; standard(product-id, spec, requirement)
(quality-standard "C001" "ASTM-A36" "structural-steel")
(quality-standard "C001" "ISO-9001" "quality-management")
(quality-standard "C002" "AS9100" "aerospace-quality")
(quality-standard "C002" "ISO-14001" "environmental")
(quality-standard "C003" "ISTA" "packaging-standards")

;; Manufacturing capabilities
(: capability (-> String String String))  ; capability(process, capacity, precision)
(capability "machining" "high-volume" "tolerance-0.001")
(capability "welding" "custom" "certified-welders")
(capability "assembly" "automated" "quality-controlled")
(capability "packaging" "flexible" "custom-designs")

;; Geographic presence
(: facility (-> String String String))  ; facility(location, type, capacity)
(facility "Detroit" "manufacturing" "high")
(facility "Chicago" "distribution" "high")
(facility "Houston" "materials" "medium")
(facility "Los-Angeles" "packaging" "medium")

;; Transportation and logistics
(: shipping-method (-> String String Int))  ; method(service, speed, cost-multiplier)
(shipping-method "ground" "standard" 1)
(shipping-method "air" "express" 3)
(shipping-method "rail" "bulk" 0.5)
(shipping-method "ocean" "international" 0.3)

;; Sustainability initiatives
(: sustainability (-> String String String))  ; sustainability(initiative, impact, certification)
(sustainability "recycling" "waste-reduction" "ISO-14001")
(sustainability "energy" "renewable-power" "LEED")
(sustainability "materials" "recycled-content" "FSC")
(sustainability "transport" "carbon-neutral" "Carbon-Trust")

;; Customer relationship management
(: customer-tier (-> String String String))  ; tier(customer-id, level, benefits)
(: payment-terms (-> String String Int))    ; terms(customer-id, type, days)
(: credit-rating (-> String String Float))  ; rating(customer-id, agency, score)

;; Market positioning
(: market-position (-> String String String))  ; position(category, strategy, advantage)
(market-position "materials" "cost-leadership" "scale-efficiency")
(market-position "components" "quality" "precision-machining")
(market-position "packaging" "customization" "design-flexibility")
(market-position "logistics" "reliability" "tracking-systems")

;; Risk management
(: risk-factor (-> String String Float))  ; risk-factor(category, description, weight)
(risk-factor "commodity" "price-volatility" 0.4)
(risk-factor "supply" "vendor-reliability" 0.3)
(risk-factor "demand" "customer-volatility" 0.3)

;; Performance metrics
(: performance-target (-> String String Float))  ; target(metric, period, value)
(performance-target "on-time-delivery" "monthly" 98.0)
(performance-target "quality-defects" "monthly" 0.5)
(performance-target "customer-satisfaction" "quarterly" 4.2)
(performance-target "cost-reduction" "annual" 5.0)

;; Innovation and R&D
(: innovation (-> String String String))  ; innovation(area, capability, investment)
(innovation "materials" "new-alloys" "high")
(innovation "process" "automation" "medium")
(innovation "packaging" "sustainable" "high")
(innovation "logistics" "tracking" "medium")

;; Compliance and certifications
(: compliance (-> String String String))  ; compliance(regulation, requirement, status)
(compliance "OSHA" "safety-standards" "certified")
(compliance "EPA" "environmental" "compliant")
(compliance "DOT" "transportation" "licensed")
(compliance "ISO" "quality" "certified")

;; Decision support functions
(: can-fulfill (-> String String))  ; can-fulfill(product-id, requirements)
(: optimal-pricing (-> String String Float))  ; optimal-pricing(product-id, context, price)
(: negotiation-strategy (-> String String String))  ; strategy(deal-id, approach, parameters)
(: capacity-planning (-> String String))  ; capacity-planning(period, availability)
(: risk-assessment (-> String String))  ; risk-assessment(project-id, level)

