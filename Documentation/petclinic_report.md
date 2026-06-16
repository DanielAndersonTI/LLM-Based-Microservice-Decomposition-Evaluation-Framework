**Summary**

Report of the static analysis activities performed today on the Spring PetClinic project.

**Analyzed System Version**
- Project name: Spring PetClinic
- Repository URL used: https://github.com/DanielAndersonTI/HTML-com-Bootstrap.git
- Analyzed branch/commit: `main` / `9312c1b346ef0220ba2d2504d85f5d7e05e720cc`
- Analysis date: 2026-06-08
- Analyzed source code path: `project_descriptions/PetClinic/monolith/spring-petclinic-main/src/main/java`

**Work Performed**
- Listed and analyzed the Java files in `src/main/java` of the `spring-petclinic-main` module.
- Extracted class/interface declarations, inheritance relationships (`extends`), implementations (`implements`), typed fields, JPA annotations (`@OneToMany`, `@ManyToOne`, `@ManyToMany`), constructor injection, and `Repository` usages.
- Updated the existing graph in [project_descriptions/PetClinic/petclinic_dependency_graph.graphml](project_descriptions/PetClinic/petclinic_dependency_graph.graphml) with the detected edges.

**Main Results (Quick Summary)**
- Nodes (detected classes): **25**
- Edges (detected relationships in the graph): **40**

**Analyzed Java Classes (main classes in src/main/java)**
- BaseEntity ([project_descriptions/PetClinic/monolith/spring-petclinic-main/src/main/java/org/springframework/samples/petclinic/model/BaseEntity.java#L33])
- NamedEntity ([project_descriptions/PetClinic/monolith/spring-petclinic-main/src/main/java/org/springframework/samples/petclinic/model/NamedEntity.java#L31])
- Person ([project_descriptions/PetClinic/monolith/spring-petclinic-main/src/main/java/org/springframework/samples/petclinic/model/Person.java#L28])
- Owner ([project_descriptions/PetClinic/monolith/spring-petclinic-main/src/main/java/org/springframework/samples/petclinic/owner/Owner.java#L49])
- Pet ([project_descriptions/PetClinic/monolith/spring-petclinic-main/src/main/java/org/springframework/samples/petclinic/owner/Pet.java#L46])
- PetType ([project_descriptions/PetClinic/monolith/spring-petclinic-main/src/main/java/org/springframework/samples/petclinic/owner/PetType.java#L28])
- Visit ([project_descriptions/PetClinic/monolith/spring-petclinic-main/src/main/java/org/springframework/samples/petclinic/owner/Visit.java#L36])
- Vet ([project_descriptions/PetClinic/monolith/spring-petclinic-main/src/main/java/org/springframework/samples/petclinic/vet/Vet.java#L45])
- Specialty ([project_descriptions/PetClinic/monolith/spring-petclinic-main/src/main/java/org/springframework/samples/petclinic/vet/Specialty.java#L30])
- OwnerController, OwnerRepository, PetController, PetTypeRepository, PetTypeFormatter, PetValidator, VisitController, VetRepository, VetController, Vets, PetClinicApplication, PetClinicRuntimeHints, CacheConfiguration, CrashController, WebConfiguration, WelcomeController (all located in `src/main/java`).

**Updated Graph**
- File: [project_descriptions/PetClinic/petclinic_dependency_graph.graphml](project_descriptions/PetClinic/petclinic_dependency_graph.graphml)
- Note: The original graph was loaded and merged with detected edges (repositories, constructor injections, and JPA compositions).

**Final Graph Metrics**

| Metric | Value |
| --- | --- |
| Classes (nodes) | 25 |
| Dependencies (edges) | 40 |
| Isolated nodes | 4 |
| Nodes with degree 1 | 2 |
| Gaps identified during auditing | 1 |
| Corrected gap | Vet → Specialty (ManyToMany) |

**Corrections Performed After Auditing**

The final audit identified an omission in the initial extraction related to the JPA ManyToMany relationship between Vet and Specialty. After manual validation of the source code, the edge Vet → Specialty was incorporated into the final graph, increasing the total number of edges from 39 to 40.

**Detected Relationships (Types)**

- Inheritance (`extends`): NamedEntity→BaseEntity, Person→BaseEntity, Owner→Person, Pet→NamedEntity, PetType→NamedEntity, Visit→BaseEntity, Vet→Person, Specialty→NamedEntity.
- Implementations (`implements`): `PetValidator implements Validator`, `WebConfiguration implements WebMvcConfigurer`.
- Typed Attributes/Fields: `Owner.pets : List<Pet>`, `Pet.type : PetType`, `Pet.visits : Set<Visit>`, `Vet.specialties : Set<Specialty>`, `Vets.vets : List<Vet>`.
- Dependency Injection: constructor injection (e.g., `PetController(OwnerRepository, PetTypeRepository)`, `PetTypeFormatter(PetTypeRepository)`, `OwnerController(OwnerRepository)`, `VisitController(OwnerRepository)`, `VetController(VetRepository)`).
- JPA Relationships: @OneToMany (Owner→Pet, Pet→Visit), @ManyToOne (Pet→PetType), @ManyToMany (Vet↔Specialty).
- Repository Usage: OwnerRepository, PetTypeRepository, VetRepository — invoked by controllers/formatters (findById, save, findPetTypes, findAll, etc.).

This Spring PetClinic analysis constitutes a pilot study used to validate and refine the dependency graph extraction, auditing, and construction process. The procedures consolidated in this pilot will later be applied to the systems that compose the main experimental dataset of the research.

> The final audit identified an omission in the initial extraction related to the JPA ManyToMany relationship between Vet and Specialty, which was subsequently incorporated into the graph.

**Extraction Rules and Heuristics Used**

1. Class/interface declaration: extracted from the declaration line `class|interface` to identify `name`, `extends`, and `implements`.
2. Typed fields: recognized through field declarations `private|protected|public Type name` and generic collections `List<Type>` / `Set<Type>`.
3. JPA annotations: when `@OneToMany`, `@ManyToOne`, `@ManyToMany`, etc. appeared immediately above a field, an edge was generated from the owning class to the field type.
4. Dependency injection: public constructors with parameters were prioritized — each typed parameter was treated as a dependency (e.g., `public X(RepoA a, ServiceB b)` → X→RepoA, X→ServiceB). `@Autowired` annotations were also searched for (none found).
5. Repositories: any interface named `*Repository` extending `JpaRepository` or `Repository` was linked to its generic entity (e.g., `OwnerRepository extends JpaRepository<Owner, Integer>` → OwnerRepository→Owner).
6. Explicit calls: textual calls such as `.save(`, `.findById(`, `.findAll(` and direct field/method references were searched to create usage edges (caller→target).
7. Scope: only static code within `src/main/java` was analyzed (excluding dynamic analysis, runtime behavior, external configurations, and tests unless explicitly requested).

**Evidence — 20 Selected Edges**

1. NamedEntity → BaseEntity (extends)
2. Person → BaseEntity (extends)
3. Owner → Person (extends)
4. Pet → NamedEntity (extends)
5. PetType → NamedEntity (extends)
6. Visit → BaseEntity (extends)
7. Vet → Person (extends)
8. Specialty → NamedEntity (extends)
9. Owner → Pet (JPA @OneToMany / field)
10. Pet → PetType (JPA @ManyToOne / field)
11. Pet → Visit (JPA @OneToMany / field)
12. PetController → OwnerRepository (constructor injection)
13. PetController → PetTypeRepository (constructor injection)
14. PetController → OwnerRepository (`.save` method)
15. PetTypeFormatter → PetTypeRepository (constructor injection)
16. OwnerRepository → Owner (repository generic)
17. PetTypeRepository → PetType (repository generic)
18. VetRepository → Vet (repository generic)
19. VetController → VetRepository (constructor injection)
20. Vets → Vet (typed collection / composition)

**Observed Limitations (Impact on Graph Confidence)**

- Dependencies through reflection, dynamic factories, runtime-generated proxies, or beans registered through external configurations were not captured.
- Indirect framework calls (e.g., handlers, callbacks, methods invoked by name through properties) are not detected through simple textual analysis.
- Polymorphism (which concrete implementation will be used at runtime) was not resolved; the graph represents static types and structural relationships.
- Tests (`src/test/java`) were not included in this extraction and may reveal additional usages.

**Recommended Next Steps to Increase Confidence**

1. Include `src/test/java` and `@Configuration`/XML classes in a new extraction to identify additional beans.
2. Run AST analysis with a Java tool (JavaParser/PMD) to extract complete method calls and resolve imports.
3. Search for reflection patterns and dynamic factories to capture runtime dependencies.
4. Generate a timestamped GraphML copy and edge CSV for manual validation and import into visualization tools.
5. Optionally execute tests with coverage enabled to map actual runtime calls.

**Generated Artifacts**

- Timestamped GraphML copy: `project_descriptions/PetClinic/petclinic_dependency_graph.20260608183715.graphml`
- Edge CSV export: `project_descriptions/PetClinic/petclinic_dependency_graph_edges.csv`
- Connectivity audit: `project_descriptions/PetClinic/petclinic_dependency_graph_audit.txt`

**Connectivity Audit Results**

- Isolated nodes (degree 0): `CacheConfiguration`, `CrashController`, `WebConfiguration`, `WelcomeController`
- Nodes with only one connection (degree 1): `PetClinicApplication`, `Specialty`

These isolated and degree-1 nodes deserve additional manual review to validate whether they should be included in the graph or whether they represent infrastructure/configuration components disconnected from the main domain.