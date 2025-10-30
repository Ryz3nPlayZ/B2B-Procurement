;; ASI Seller Schema MeTTa Definitions
;; Defines seller-specific types and relationships

;; Seller agent types
(: Seller (-> String String String))  ; Seller(id, type, status)
(: Catalog (-> String String String))  ; Catalog(id, name, status)
(: Inventory (-> String String Int))  ; Inventory(product-id, location, quantity)
(: Pricing (-> String String Float))  ; Pricing(product-id, tier, price)

;; Product and service types
(: Product (-> String String String))  ; Product(id, name, category)
(: Service (-> String String String))  ; Service(id, name, category)
(: Offering (-> String String String))  ; Offering(id, type, description)

;; Inventory and stock types
(: Stock (-> String String Int))  ; Stock(product-id, location, quantity)
(: Warehouse (-> String String String))  ; Warehouse(id, location, capacity)
(: Location (-> String String String))  ; Location(id, type, address)

;; Pricing and cost types
(: Price (-> String String Float))  ; Price(product-id, tier, amount)
(: Cost (-> String String Float))  ; Cost(product-id, type, amount)
(: Margin (-> String String Float))  ; Margin(product-id, type, percentage)

;; Customer and relationship types
(: Customer (-> String String String))  ; Customer(id, name, tier)
(: Relationship (-> String String String))  ; Relationship(id, type, status)
(: Contract (-> String String String))  ; Contract(id, type, status)

;; Sales and marketing types
(: Lead (-> String String String))  ; Lead(id, source, status)
(: Opportunity (-> String String String))  ; Opportunity(id, type, status)
(: Campaign (-> String String String))  ; Campaign(id, name, status)

;; Quote and proposal types
(: Quote (-> String String String))  ; Quote(id, customer-id, status)
(: Proposal (-> String String String))  ; Proposal(id, type, status)
(: Bid (-> String String String))  ; Bid(id, opportunity-id, status)

;; Negotiation and deal types
(: Negotiation (-> String String String))  ; Negotiation(id, type, status)
(: Deal (-> String String String))  ; Deal(id, type, status)
(: Agreement (-> String String String))  ; Agreement(id, type, status)

;; Fulfillment and delivery types
(: Order (-> String String String))  ; Order(id, customer-id, status)
(: Fulfillment (-> String String String))  ; Fulfillment(id, order-id, status)
(: Delivery (-> String String String))  ; Delivery(id, order-id, status)

;; Quality and certification types
(: Quality (-> String String Float))  ; Quality(product-id, metric, value)
(: Certification (-> String String String))  ; Certification(id, type, issuer)
(: Standard (-> String String String))  ; Standard(id, organization, requirement)

;; Capability and capacity types
(: Capability (-> String String String))  ; Capability(id, type, level)
(: Capacity (-> String String Int))  ; Capacity(id, type, amount)
(: Resource (-> String String String))  ; Resource(id, type, availability)

;; Performance and metrics types
(: Metric (-> String String Float))  ; Metric(id, name, value)
(: KPI (-> String String Float))  ; KPI(id, name, target)
(: Performance (-> String String Float))  ; Performance(id, metric, value)

;; Risk and compliance types
(: Risk (-> String String Float))  ; Risk(id, type, level)
(: Compliance (-> String String String))  ; Compliance(id, regulation, status)
(: Audit (-> String String String))  ; Audit(id, type, result)

;; Market and competitive types
(: Market (-> String String String))  ; Market(id, name, segment)
(: Competitor (-> String String String))  ; Competitor(id, name, position)
(: Trend (-> String String String))  ; Trend(id, category, direction)

;; Innovation and R&D types
(: Innovation (-> String String String))  ; Innovation(id, area, investment)
(: Research (-> String String String))  ; Research(id, project, status)
(: Development (-> String String String))  ; Development(id, project, status)

;; Financial and revenue types
(: Revenue (-> String String Float))  ; Revenue(id, source, amount)
(: Profit (-> String String Float))  ; Profit(id, period, amount)
(: Margin (-> String String Float))  ; Margin(id, product, percentage)

;; Seller-specific relationships
(: offers-product (-> String String))  ; offers-product(seller-id, product-id)
(: has-inventory (-> String String))  ; has-inventory(seller-id, product-id)
(: serves-customer (-> String String))  ; serves-customer(seller-id, customer-id)
(: competes-with (-> String String))  ; competes-with(seller-id, competitor-id)

;; Sales process states
(: sales-stage (-> String String))  ; sales-stage(opportunity-id, stage)
(: quote-status (-> String String))  ; quote-status(quote-id, status)
(: deal-probability (-> String String Float))  ; deal-probability(deal-id, stage, probability)

;; Inventory management
(: stock-level (-> String String Int))  ; stock-level(product-id, location, quantity)
(: reorder-point (-> String String Int))  ; reorder-point(product-id, location, threshold)
(: lead-time (-> String String Int))  ; lead-time(product-id, supplier, days)

;; Pricing strategies
(: pricing-strategy (-> String String String))  ; pricing-strategy(product-id, approach, parameters)
(: discount-rule (-> String String String))  ; discount-rule(product-id, condition, percentage)
(: volume-pricing (-> String String String))  ; volume-pricing(product-id, tier, price)

;; Customer relationship management
(: customer-tier (-> String String String))  ; customer-tier(customer-id, level, benefits)
(: loyalty-program (-> String String String))  ; loyalty-program(customer-id, level, rewards)
(: satisfaction-score (-> String String Float))  ; satisfaction-score(customer-id, metric, value)

;; Market positioning
(: market-position (-> String String String))  ; market-position(seller-id, category, strategy)
(: competitive-advantage (-> String String String))  ; competitive-advantage(seller-id, area, strength)
(: value-proposition (-> String String String))  ; value-proposition(seller-id, customer, benefit)

;; Operational capabilities
(: production-capacity (-> String String Int))  ; production-capacity(seller-id, product, units)
(: delivery-capability (-> String String String))  ; delivery-capability(seller-id, region, service)
(: support-capability (-> String String String))  ; support-capability(seller-id, type, level)

;; Decision support functions
(: can-fulfill (-> String String))  ; can-fulfill(product-id, requirements)
(: optimal-pricing (-> String String Float))  ; optimal-pricing(product-id, context, price)
(: negotiation-strategy (-> String String String))  ; strategy(deal-id, approach, parameters)
(: capacity-planning (-> String String))  ; capacity-planning(period, availability)

