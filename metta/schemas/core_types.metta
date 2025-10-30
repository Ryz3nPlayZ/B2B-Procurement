;; ASI Core Types MeTTa Schema
;; Defines fundamental types used across the ASI system

;; Basic entity types
(: Entity (-> String String))  ; Entity(id, type)
(: Agent (-> String String String))  ; Agent(id, type, status)
(: Deal (-> String String String))  ; Deal(id, type, status)
(: Message (-> String String String))  ; Message(id, type, content)

;; Product and service types
(: Product (-> String String String String))  ; Product(id, name, category, description)
(: Service (-> String String String String))  ; Service(id, name, category, description)
(: Price (-> String Float String String))  ; Price(currency, amount, conditions, validity)
(: Quantity (-> String Int String))  ; Quantity(unit, amount, specification)

;; Temporal types
(: Timestamp (-> String String))  ; Timestamp(id, iso-format)
(: Duration (-> String Float String))  ; Duration(id, value, unit)
(: Deadline (-> String String String))  ; Deadline(id, timestamp, type)

;; Geographic types
(: Location (-> String String String))  ; Location(id, type, address)
(: Region (-> String String String))  ; Region(id, name, country)
(: Zone (-> String String String))  ; Zone(id, type, coverage)

;; Quality and certification types
(: Certification (-> String String String String))  ; Certification(id, type, issuer, validity)
(: Quality (-> String String Float))  ; Quality(metric, standard, value)
(: Standard (-> String String String))  ; Standard(id, organization, description)

;; Financial types
(: Currency (-> String String Float))  ; Currency(code, name, exchange-rate)
(: Payment (-> String String Float String))  ; Payment(id, method, amount, status)
(: Invoice (-> String String Float String))  ; Invoice(id, number, amount, status)

;; Communication types
(: Channel (-> String String String))  ; Channel(id, type, endpoint)
(: Protocol (-> String String String))  ; Protocol(id, type, version)
(: Format (-> String String String))  ; Format(id, type, specification)

;; Relationship types
(: Relationship (-> String String String String))  ; Relationship(id, type, from, to)
(: Dependency (-> String String String))  ; Dependency(id, type, target)
(: Constraint (-> String String String))  ; Constraint(id, type, condition)

;; State and status types
(: State (-> String String String))  ; State(id, type, value)
(: Status (-> String String String))  ; Status(id, type, value)
(: Transition (-> String String String))  ; Transition(id, from, to)

;; Metric and measurement types
(: Metric (-> String String Float))  ; Metric(id, type, value)
(: Measurement (-> String String Float String))  ; Measurement(id, type, value, unit)
(: KPI (-> String String Float String))  ; KPI(id, name, target, period)

;; Risk and security types
(: Risk (-> String String Float))  ; Risk(id, type, level)
(: Security (-> String String String))  ; Security(id, type, level)
(: Compliance (-> String String String))  ; Compliance(id, regulation, status)

;; Workflow and process types
(: Process (-> String String String))  ; Process(id, name, type)
(: Step (-> String String String))  ; Step(id, name, process)
(: Workflow (-> String String String))  ; Workflow(id, name, status)

;; Decision and evaluation types
(: Decision (-> String String String))  ; Decision(id, type, outcome)
(: Evaluation (-> String String Float))  ; Evaluation(id, criteria, score)
(: Criteria (-> String String Float))  ; Criteria(id, name, weight)

;; Configuration and settings types
(: Configuration (-> String String String))  ; Configuration(id, key, value)
(: Setting (-> String String String))  ; Setting(id, category, value)
(: Parameter (-> String String String))  ; Parameter(id, name, value)

;; Event and notification types
(: Event (-> String String String))  ; Event(id, type, description)
(: Notification (-> String String String))  ; Notification(id, type, message)
(: Alert (-> String String String))  ; Alert(id, type, condition)

;; Validation and constraint types
(: Validation (-> String String String))  ; Validation(id, rule, result)
(: Constraint (-> String String String))  ; Constraint(id, type, condition)
(: Rule (-> String String String))  ; Rule(id, name, condition)

;; Integration and API types
(: API (-> String String String))  ; API(id, endpoint, version)
(: Integration (-> String String String))  ; Integration(id, system, status)
(: Endpoint (-> String String String))  ; Endpoint(id, type, url)

;; Metadata and annotation types
(: Metadata (-> String String String))  ; Metadata(id, key, value)
(: Annotation (-> String String String))  ; Annotation(id, type, content)
(: Tag (-> String String String))  ; Tag(id, name, category)

