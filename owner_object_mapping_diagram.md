# 🏠 Owner Object Mapping Strategy

## Data Flow Diagram

```mermaid
graph TD
    A[Property Record] --> B[Extract Owner Info]
    B --> C{Owner Type?}

    C -->|Individual| D[Individual Owner Object]
    C -->|LLC/Business| E[Business Owner Object]

    D --> F[Seller 1: First Name + Last Name]

    E --> G[Business Name Analysis]
    G --> H{Find Individual Behind LLC?}

    H -->|Yes - Property Address = Mailing Address| I[Individual Owner Detected]
    H -->|No - Different Addresses| J[Business Only - No Individual]

    I --> K[Owner Object: Individual + Business]
    J --> L[Owner Object: Business Only]

    K --> M[Seller 1: Individual Name | Business Name]
    L --> N[Seller 1: Business Name Only]

    M --> O[Skip Trace: Individual Name + Mailing Address]
    N --> P[Skip Trace: Business Name + Mailing Address]

    style A fill:#e1f5fe
    style I fill:#c8e6c9
    style J fill:#ffcdd2
    style O fill:#4caf50
    style P fill:#ff9800
```

## Detailed Owner Object Structure

```mermaid
classDiagram
    class PropertyRecord {
        +string property_address
        +string mailing_address
        +string first_name
        +string last_name
        +string business_name
        +string estimated_value
    }

    class OwnerObject {
        +string individual_name
        +string business_name
        +string mailing_address
        +string property_address
        +bool is_individual_owner
        +bool is_business_owner
        +bool has_skip_trace_info
        +float total_property_value
        +int property_count
    }

    class SkipTraceInfo {
        +string target_name
        +string mailing_address
        +string property_address
        +string phone_numbers
        +string email_addresses
        +float confidence_score
    }

    PropertyRecord --> OwnerObject : creates
    OwnerObject --> SkipTraceInfo : generates
```

## LLC Detection & Individual Mapping Logic

```mermaid
flowchart LR
    A[Property Record] --> B{Business Name Contains LLC/Inc/Corp?}

    B -->|Yes| C[LLC Detected]
    B -->|No| D[Individual Owner]

    C --> E{Property Address = Mailing Address?}
    E -->|Yes| F[Potential Individual Owner]
    E -->|No| G[Pure Business Entity]

    F --> H{Individual Name in Property Record?}
    H -->|Yes| I[Owner Object: Individual + LLC]
    H -->|No| J[Owner Object: LLC Only]

    G --> K[Owner Object: LLC Only]
    D --> L[Owner Object: Individual Only]

    I --> M[High Skip Trace Confidence]
    J --> N[Medium Skip Trace Confidence]
    K --> O[Low Skip Trace Confidence]
    L --> P[High Skip Trace Confidence]

    style M fill:#4caf50
    style N fill:#ff9800
    style O fill:#f44336
    style P fill:#4caf50
```

## Data Processing Pipeline

```mermaid
sequenceDiagram
    participant CSV as CSV Data
    participant Analyzer as Owner Analyzer
    participant Mapper as Data Mapper
    participant Output as Pete Export

    CSV->>Analyzer: Load Property Records
    Analyzer->>Analyzer: Group by Mailing Address
    Analyzer->>Analyzer: Detect LLC vs Individual
    Analyzer->>Analyzer: Find Individual Behind LLC
    Analyzer->>Mapper: Owner Objects Created

    Mapper->>Mapper: Create Seller 1 Names
    Mapper->>Mapper: Generate Skip Trace Info
    Mapper->>Output: Export with Owner Objects

    Note over Analyzer: Key Logic:<br/>1. Same Property + Mailing Address<br/>2. Individual name present<br/>3. Business name present<br/>4. Combine for Seller 1
```

## Skip Trace Priority Matrix

```mermaid
graph TD
    A[Owner Object Created] --> B{Skip Trace Priority}

    B -->|Priority 1| C[Individual + Mailing Address]
    B -->|Priority 2| D[Individual + Business + Mailing]
    B -->|Priority 3| E[Business + Mailing Address]
    B -->|Priority 4| F[Business Only]

    C --> G[95% Skip Trace Success]
    D --> H[90% Skip Trace Success]
    E --> I[70% Skip Trace Success]
    F --> J[40% Skip Trace Success]

    style C fill:#4caf50
    style D fill:#8bc34a
    style E fill:#ff9800
    style F fill:#f44336
```

## Example Owner Object Mapping

### Scenario 1: Individual Behind LLC

```
Property Address: 123 Main St, Miami, FL
Mailing Address: 123 Main St, Miami, FL  ← SAME ADDRESS
First Name: John
Last Name: Smith
Business Name: ABC Properties LLC

→ Owner Object:
   Individual Name: "John Smith"
   Business Name: "ABC Properties LLC"
   Skip Trace Target: "John Smith" + "123 Main St, Miami, FL"
   Seller 1: "John Smith | ABC Properties LLC"
   Confidence: HIGH (95%)
```

### Scenario 2: Pure Business Entity

```
Property Address: 456 Oak Ave, Miami, FL
Mailing Address: 789 Business Blvd, Miami, FL  ← DIFFERENT ADDRESS
First Name: (empty)
Last Name: (empty)
Business Name: XYZ Holdings LLC

→ Owner Object:
   Individual Name: (empty)
   Business Name: "XYZ Holdings LLC"
   Skip Trace Target: "XYZ Holdings LLC" + "789 Business Blvd, Miami, FL"
   Seller 1: "XYZ Holdings LLC"
   Confidence: MEDIUM (70%)
```

### Scenario 3: Individual Owner

```
Property Address: 321 Pine St, Miami, FL
Mailing Address: 321 Pine St, Miami, FL  ← SAME ADDRESS
First Name: Mary
Last Name: Johnson
Business Name: (empty)

→ Owner Object:
   Individual Name: "Mary Johnson"
   Business Name: (empty)
   Skip Trace Target: "Mary Johnson" + "321 Pine St, Miami, FL"
   Seller 1: "Mary Johnson"
   Confidence: HIGH (95%)
```
