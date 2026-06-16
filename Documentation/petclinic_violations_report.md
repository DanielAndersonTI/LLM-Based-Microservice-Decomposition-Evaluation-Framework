# Structural Violations Analysis - Spring PetClinic

**Pilot Study: Experiment 3 - Mapping and Violation Detection**

## Executive Summary

| Metric | Few-shot | Zero-shot |
|---------|---------|----------|
| Total Edges | 40 | 40 |
| Detected Violations | 8 | 9 |
| Consistent Edges | 17 | 17 |
| **TVD (Violation Rate)** | **20.00%** | **22.50%** |
| **BC (Basic Cohesion)** | **80.00%** | **77.50%** |
| Granularity (# Services) | 8 | 8 |

## Interpretation of Metrics

- **TVD (Dependency Violation Rate):** Proportion of dependencies that cross service boundaries.
  - Lower values are better (indicating a better decomposition).
- **BC (Basic Cohesion):** Proportion of dependencies that remain **internal** to services (BC = 1 - TVD).
  - Higher values are better (indicating better encapsulation).
- **Granularity:** Number of services in the decomposition.

---

## Detailed Analysis - FEW-SHOT

### Metrics - FEW-SHOT

- **Total Analyzed Edges:** 40
- **Structural Violations:** 8
- **Consistent Edges:** 17
- **Violation Rate (TVD):** 20.00%
- **Basic Cohesion (BC):** 80.00%
- **Number of Services:** 8

### Identified Services

**Client Service**
- Classes: Owner, OwnerController, OwnerRepository
- Expected communications: Pet Service; Visit Service

**Pet Service**
- Classes: Pet, PetController, PetType, PetTypeFormatter, PetTypeRepository, PetValidator
- Expected communications: Client Service; Visit Service

**Visit Service**
- Classes: Visit, VisitController
- Expected communications: Pet Service; Client Service

**Vet Service**
- Classes: Specialty, Vet, VetController, VetRepository
- Expected communications:

**Discovery Service (Eureka)**
- Classes: (none)
- Expected communications: Client Service; Pet Service; Visit Service; Vet Service; Config Service; API Gateway; Admin Server

**Config Service**
- Classes: (none)
- Expected communications: Client Service; Pet Service; Visit Service; Vet Service; API Gateway; Discovery Service; Admin Server

**API Gateway**
- Classes: (none)
- Expected communications: Client Service; Pet Service; Visit Service; Vet Service; Discovery Service

**Admin Server**
- Classes: (none)
- Expected communications: Client Service; Pet Service; Visit Service; Vet Service; Discovery Service; Config Service; API Gateway

### Detected Violations (8)

| Source | Target | Type | Source Service | Target Service |
|----------|----------|----------|----------|----------|
| Owner | Pet | jpa | Client Service | Pet Service |
| Owner | Visit | jpa | Client Service | Visit Service |
| Pet | Visit | jpa | Pet Service | Visit Service |
| PetController | Owner | unknown | Pet Service | Client Service |
| VisitController | Pet | unknown | Visit Service | Pet Service |
| VisitController | Owner | unknown | Visit Service | Client Service |
| PetController | OwnerRepository | injection | Pet Service | Client Service |
| VisitController | OwnerRepository | injection | Visit Service | Client Service |

---

## Detailed Analysis - ZERO-SHOT

### Metrics - ZERO-SHOT

- **Total Analyzed Edges:** 40
- **Structural Violations:** 9
- **Consistent Edges:** 17
- **Violation Rate (TVD):** 22.50%
- **Basic Cohesion (BC):** 77.50%
- **Number of Services:** 8

### Identified Services

**Client Service**
- Classes: Owner, OwnerController, OwnerRepository
- Expected communications: Pet Service; Discovery Service; Config Service; Gateway Service; Admin Service

**Pet Service**
- Classes: Pet, PetController, PetType, PetTypeFormatter, PetTypeRepository, PetValidator
- Expected communications: Client Service; Visit Service; Discovery Service; Config Service; Gateway Service; Admin Service

**Visit Service**
- Classes: Visit, VisitController
- Expected communications: Pet Service; Discovery Service; Config Service; Gateway Service; Admin Service

**Vet Service**
- Classes: Specialty, Vet, VetController, VetRepository
- Expected communications: Discovery Service; Config Service; Gateway Service; Admin Service

**Discovery Service**
- Classes: PetClinicApplication
- Expected communications: Client Service; Pet Service; Visit Service; Vet Service; Config Service; Gateway Service; Admin Service

**Config Service**
- Classes: (none)
- Expected communications: Client Service; Pet Service; Visit Service; Vet Service; Discovery Service; Gateway Service; Admin Service

**Gateway Service**
- Classes: (none)
- Expected communications: Client Service; Pet Service; Visit Service; Vet Service; Discovery Service; Config Service; Admin Service

**Admin Service**
- Classes: (none)
- Expected communications: Client Service; Pet Service; Visit Service; Vet Service; Discovery Service; Config Service; Gateway Service

### Detected Violations (9)

| Source | Target | Type | Source Service | Target Service |
|----------|----------|----------|----------|----------|
| Owner | Pet | jpa | Client Service | Pet Service |
| Owner | Visit | jpa | Client Service | Visit Service |
| Pet | Visit | jpa | Pet Service | Visit Service |
| PetController | Owner | unknown | Pet Service | Client Service |
| VisitController | Pet | unknown | Visit Service | Pet Service |
| VisitController | Owner | unknown | Visit Service | Client Service |
| PetClinicApplication | Pet | unknown | Discovery Service | Pet Service |
| PetController | OwnerRepository | injection | Pet Service | Client Service |
| VisitController | OwnerRepository | injection | Visit Service | Client Service |

---

## Comparison Between Strategies

- **TVD Difference (Zero-shot - Few-shot):** +2.50%
  → **Few-shot shows better adherence** (fewer violations)

- **BC Difference (Zero-shot - Few-shot):** -2.50%
  → **Few-shot shows better cohesion** (more internal dependencies)

- **Granularity:** Both strategies generated 8 services.

## Pilot Study Conclusions

**Best-performing Strategy: Few-shot**

This pilot study validated:

1. ✓ Reliable dependency graph extraction (Stage 1)
2. ✓ Class-to-service mapping (Stage 2)
3. ✓ Automatic structural violation detection (Stage 3)
4. ✓ Adherence metric calculation (Stage 4)

The procedures consolidated during this pilot are ready to be applied to the remaining systems.