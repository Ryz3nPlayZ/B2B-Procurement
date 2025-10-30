# MeTTa Knowledge Graph Documentation

## Overview

The ASI system uses MeTTa (Meta Type Theory) as its knowledge representation language for storing and querying business rules, policies, and domain knowledge. This document describes the MeTTa schemas and knowledge bases used in the system.

## Knowledge Base Structure

### 1. Buyer Policies (`buyer_policies.metta`)

Contains procurement policies, constraints, and decision rules for buyer agents.

#### Core Types
```metta
(: Product (-> String String String))  ; Product(name, category, specification)
(: Price (-> String Float String))     ; Price(currency, amount, conditions)
(: Certification (-> String String String))  ; Certification(type, issuer, validity)
```

#### Procurement Policies
```metta
(: procurement-policy (-> String String))  ; policy(name, description)
(procurement-policy "competitive-bidding" "All purchases over $10,000 must go through competitive bidding process")
(procurement-policy "vendor-diversification" "No single vendor should account for more than 40% of total procurement")
```

#### Budget Constraints
```metta
(: budget-constraint (-> String Float String))  ; constraint(type, limit, period)
(budget-constraint "quarterly" 100000.0 "Q1-2024")
(budget-constraint "annual" 500000.0 "2024")
```

#### Quality Requirements
```metta
(: quality-requirement (-> String String Float))  ; requirement(metric, standard, threshold)
(quality-requirement "delivery-time" "standard" 7.0)  ; 7 days standard delivery
(quality-requirement "warranty" "minimum" 12.0)      ; 12 months minimum warranty
```

#### Decision Rules
```metta
(: evaluate-quote (-> String String Float))  ; evaluate-quote(quote-id, criteria, score)
(: negotiation-strategy (-> String String String))  ; strategy(deal-id, approach, parameters)
(: should-negotiate (-> String String))  ; should-negotiate(quote-id, reason)
```

### 2. Seller Knowledge Bases

#### Seller A (`seller_a.metta`)
Industrial equipment and components supplier.

```metta
(: Product (-> String String String String))  ; Product(id, name, category, description)
(Product "A001" "Industrial Sensors" "Electronics" "High-precision temperature and pressure sensors")
(Product "A002" "Control Systems" "Automation" "PLC-based control systems for manufacturing")

(: Inventory (-> String String Int Float))      ; Inventory(product-id, location, quantity, cost)
(Inventory "A001" "warehouse-1" 150 45.50)
(Inventory "A001" "warehouse-2" 75 45.50)

(: Pricing (-> String String Float String))    ; Pricing(product-id, tier, price, conditions)
(Pricing "A001" "retail" 89.99 "standard")
(Pricing "A001" "wholesale" 67.50 "min-100-units")
```

#### Seller B (`seller_b.metta`)
Software and IT services provider.

```metta
(Product "B001" "Software Solutions" "Software" "Enterprise software and cloud solutions")
(Product "B002" "IT Infrastructure" "Hardware" "Servers, networking equipment, and storage")

(: sla (-> String String String))  ; sla(service, metric, commitment)
(sla "B001" "uptime" "99.9-percent")
(sla "B001" "response-time" "4-hours")
```

#### Seller C (`seller_c.metta`)
Raw materials and manufacturing supplier.

```metta
(Product "C001" "Raw Materials" "Materials" "Steel, aluminum, and composite materials")
(Product "C002" "Components" "Manufacturing" "Precision machined components and parts")

(: quality-standard (-> String String String))  ; standard(product-id, spec, requirement)
(quality-standard "C001" "ASTM-A36" "structural-steel")
(quality-standard "C002" "AS9100" "aerospace-quality")
```

### 3. Schema Definitions

#### Core Types (`core_types.metta`)
Fundamental types used across the system.

```metta
(: Entity (-> String String))  ; Entity(id, type)
(: Agent (-> String String String))  ; Agent(id, type, status)
(: Deal (-> String String String))  ; Deal(id, type, status)
(: Message (-> String String String))  ; Message(id, type, content)

(: Product (-> String String String String))  ; Product(id, name, category, description)
(: Service (-> String String String String))  ; Service(id, name, category, description)
(: Price (-> String Float String String))  ; Price(currency, amount, conditions, validity)

(: Timestamp (-> String String))  ; Timestamp(id, iso-format)
(: Duration (-> String Float String))  ; Duration(id, value, unit)
(: Deadline (-> String String String))  ; Deadline(id, timestamp, type)
```

#### Buyer Schema (`buyer_schema.metta`)
Buyer-specific types and relationships.

```metta
(: Buyer (-> String String String))  ; Buyer(id, type, status)
(: Procurement (-> String String String))  ; Procurement(id, type, status)
(: RFQ (-> String String String))  ; RFQ(id, buyer-id, status)

(: Requirement (-> String String String))  ; Requirement(id, type, description)
(: Policy (-> String String String))  ; Policy(id, name, description)
(: Budget (-> String String Float))  ; Budget(id, period, amount)

(: has-requirement (-> String String))  ; has-requirement(buyer-id, requirement-id)
(: follows-policy (-> String String))  ; follows-policy(buyer-id, policy-id)
(: evaluates-vendor (-> String String))  ; evaluates-vendor(buyer-id, vendor-id)
```

#### Seller Schema (`seller_schema.metta`)
Seller-specific types and relationships.

```metta
(: Seller (-> String String String))  ; Seller(id, type, status)
(: Catalog (-> String String String))  ; Catalog(id, name, status)
(: Inventory (-> String String Int))  ; Inventory(product-id, location, quantity)

(: Product (-> String String String))  ; Product(id, name, category)
(: Pricing (-> String String Float))  ; Pricing(product-id, tier, price)
(: Customer (-> String String String))  ; Customer(id, name, tier)

(: offers-product (-> String String))  ; offers-product(seller-id, product-id)
(: has-inventory (-> String String))  ; has-inventory(seller-id, product-id)
(: serves-customer (-> String String))  ; serves-customer(seller-id, customer-id)
```

## Query Patterns

### 1. Policy Queries
```metta
;; Get all procurement policies
(match &self (procurement-policy $name $description)
    [(procurement-policy $name $description)])

;; Get budget constraints
(match &self (budget-constraint $type $limit $period)
    [(budget-constraint $type $limit $period)])
```

### 2. Inventory Queries
```metta
;; Get inventory for a product
(match &self (Inventory $product-id $location $quantity $cost)
    [(Inventory "A001" $location $quantity $cost)])

;; Get pricing information
(match &self (Pricing $product-id $tier $price $conditions)
    [(Pricing "A001" $tier $price $conditions)])
```

### 3. Decision Support Queries
```metta
;; Check if negotiation should proceed
(match &self (should-negotiate $quote-id $reason)
    [(should-negotiate $quote-id $reason)])

;; Get approval requirements
(match &self (approval-level $level $approver $conditions)
    [(approval-level $level $approver $conditions)])
```

## Knowledge Base Operations

### 1. Fact Addition
```python
# Add new procurement policy
engine.add_fact("(procurement-policy \"sustainability\" \"All products must meet environmental standards\")")

# Add inventory update
engine.add_fact("(Inventory \"A001\" \"warehouse-1\" 200 45.50)")
```

### 2. Query Execution
```python
# Query procurement policies
query = """
(match &self (procurement-policy $name $description)
    [(procurement-policy $name $description)])
"""
results = engine.execute_query(query)
```

### 3. Knowledge Base Updates
```python
# Update inventory
engine.update_inventory("seller_a_001", {
    "A001": [{"location": "warehouse-1", "quantity": 200, "cost": 45.50}]
})
```

## Integration with Python

### 1. Buyer Queries
```python
from metta.queries.buyer_queries import BuyerQueries

buyer_queries = BuyerQueries(metta_engine)

# Get procurement policies
policies = buyer_queries.get_procurement_policies()

# Get budget constraints
constraints = buyer_queries.get_budget_constraints()

# Evaluate quote
evaluation = buyer_queries.evaluate_quote(quote_data)
```

### 2. Seller Queries
```python
from metta.queries.seller_queries import SellerQueries

seller_queries = SellerQueries(metta_engine)

# Get inventory
inventory = seller_queries.get_inventory()

# Get pricing rules
pricing = seller_queries.get_pricing_rules()

# Assess fulfillment capability
capability = seller_queries.assess_fulfillment_capability(requirements)
```

## Best Practices

### 1. Schema Design
- Use descriptive type names
- Include clear documentation
- Maintain consistency across schemas
- Use appropriate arity for relations

### 2. Query Optimization
- Use specific patterns in queries
- Avoid overly broad matches
- Cache frequently used queries
- Monitor query performance

### 3. Knowledge Base Maintenance
- Regular validation of facts
- Incremental updates
- Version control for schemas
- Backup and recovery procedures

### 4. Integration Patterns
- Use wrapper classes for complex queries
- Implement error handling
- Provide fallback mechanisms
- Monitor knowledge base health

## Performance Considerations

### 1. Query Caching
- Cache frequently used queries
- Implement cache invalidation
- Monitor cache hit rates
- Optimize cache size

### 2. Knowledge Base Size
- Monitor knowledge base growth
- Implement archiving strategies
- Optimize fact storage
- Regular cleanup procedures

### 3. Query Performance
- Profile slow queries
- Optimize query patterns
- Use appropriate indexes
- Monitor execution times

## Troubleshooting

### 1. Common Issues
- Invalid MeTTa syntax
- Missing type definitions
- Query timeout issues
- Knowledge base corruption

### 2. Debugging Techniques
- Enable query logging
- Use query validation
- Monitor knowledge base status
- Implement health checks

### 3. Recovery Procedures
- Knowledge base backup
- Schema validation
- Fact verification
- System restart procedures

