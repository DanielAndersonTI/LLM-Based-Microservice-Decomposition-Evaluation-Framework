import csv
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

try:
    from tree_sitter import Language, Parser
    import tree_sitter_java
    JAVA_LANGUAGE = Language(tree_sitter_java.language())
except ImportError:
    try:
        from tree_sitter import Language, Parser
        from tree_sitter_languages import get_language
        JAVA_LANGUAGE = get_language("java")
    except ImportError as exc:
        raise ImportError(
            "Unable to import a Java Tree-sitter grammar. "
            "Install either 'tree-sitter-java' or 'tree_sitter_languages' and try again."
        ) from exc

try:
    import networkx as nx
except ImportError as exc:
    raise ImportError("Install networkx to run this script: pip install networkx") from exc

try:
    import pandas as pd
except ImportError as exc:
    raise ImportError("Install pandas to run this script: pip install pandas") from exc


BASE_DIR = Path(__file__).resolve().parent
PETCLINIC_ROOT = (
    BASE_DIR
    / "monolito"
    / "spring-petclinic-main"
    / "src"
    / "main"
    / "java"
    / "org"
    / "springframework"
    / "samples"
    / "petclinic"
)
CSV_DIR = BASE_DIR / "csv"
GRAPHML_OUTPUT = BASE_DIR / "petclinic_dependency_graph.graphml"
SERVICE_PRIORITY_CSV = "petclinic-fewshot-results.csv"

PACKAGE_SERVICE_MAP = {
    "owner": "Client Service",
    "vet": "Vet Service",
    "visit": "Visit Service",
    "model": "Pet Service",
    "system": "Gateway Service",
}

CLASS_SERVICE_MAP = {
    "Owner": "Client Service",
    "OwnerController": "Client Service",
    "OwnerRepository": "Client Service",
    "OwnerValidator": "Client Service",
    "Pet": "Pet Service",
    "PetController": "Pet Service",
    "PetRepository": "Pet Service",
    "PetType": "Pet Service",
    "PetTypeRepository": "Pet Service",
    "Visit": "Visit Service",
    "VisitController": "Visit Service",
    "Vet": "Vet Service",
    "VetController": "Vet Service",
    "VetRepository": "Vet Service",
    "Vets": "Vet Service",
    "Specialty": "Vet Service",
    "PetClinicApplication": "Gateway Service",
    "PetClinicRuntimeHints": "Gateway Service",
    "WelcomeController": "Gateway Service",
    "WebConfiguration": "Gateway Service",
    "CrashController": "Gateway Service",
    "CacheConfiguration": "Gateway Service",
}


def read_csv_service_mapping(csv_path: Path) -> Dict[str, str]:
    if not csv_path.exists():
        return {}

    df = pd.read_csv(csv_path)
    headers = [h.lower() for h in df.columns]
    if "class" in headers and "service" in headers:
        return {
            str(row[headers.index("class")]).strip(): str(row[headers.index("service")]).strip()
            for row in df.values
            if str(row[headers.index("class")]).strip()
        }
    return {}


def try_parse_csv_to_service_map(csv_dir: Path) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for csv_file in csv_dir.glob("*.csv"):
        try:
            candidate = read_csv_service_mapping(csv_file)
            if candidate:
                mapping.update(candidate)
        except Exception:
            continue
    return mapping


def java_files(root: Path) -> List[Path]:
    return sorted(root.rglob("*.java"))


def get_node_text(node, src_bytes: bytes) -> str:
    return src_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


def find_nodes(root, type_names: Set[str]) -> List:
    results = []
    stack = [root]
    while stack:
        node = stack.pop()
        if node.type in type_names:
            results.append(node)
        stack.extend(reversed(node.children))
    return results


def extract_package(root, src_bytes: bytes) -> str:
    for child in root.children:
        if child.type == "package_declaration":
            name_node = child.child_by_field_name("name")
            if name_node is not None:
                return get_node_text(name_node, src_bytes)
    return ""


def extract_top_level_classes(root, src_bytes: bytes) -> List[Tuple[str, str, List[str], List[str]]]:
    classes = []
    for node in find_nodes(root, {"class_declaration", "interface_declaration", "enum_declaration"}):
        name_node = node.child_by_field_name("name")
        if name_node is None:
            continue
        class_name = get_node_text(name_node, src_bytes)
        extends = []
        implements = []
        for field_name in ["superclass", "superinterfaces", "implements"]:
            field_node = node.child_by_field_name(field_name)
            if field_node is not None:
                type_names = extract_type_names(field_node, src_bytes)
                if field_name == "superclass":
                    extends.extend(type_names)
                else:
                    implements.extend(type_names)
        classes.append((class_name, node.type, extends, implements))
    return classes


def iter_descendants(node):
    stack = [node]
    while stack:
        current = stack.pop()
        yield current
        stack.extend(reversed(current.children))


def extract_type_names(node, src_bytes: bytes) -> List[str]:
    type_names: List[str] = []
    for child in iter_descendants(node):
        if child.type in {"identifier", "type_identifier", "scoped_identifier"}:
            text = get_node_text(child, src_bytes)
            if text and text[0].isupper():
                type_names.append(text)
    if not type_names:
        text = get_node_text(node, src_bytes).strip()
        if text and text[0].isupper():
            type_names.append(text)
    return type_names


def collect_dependencies(class_name: str, root, src_bytes: bytes, project_types: Set[str]) -> Set[str]:
    deps: Set[str] = set()
    for node in find_nodes(root, {"method_invocation", "object_creation_expression", "field_access", "member_reference", "class_or_interface_type", "scoped_identifier"}):
        text = get_node_text(node, src_bytes)
        if not text:
            continue
        for candidate in project_types:
            if candidate == class_name:
                continue
            if candidate in text:
                deps.add(candidate)
    return deps


def build_graph(java_root: Path) -> Tuple[nx.DiGraph, Dict[str, str], Dict[str, str]]:
    parser = Parser()
    parser.language = JAVA_LANGUAGE

    files = java_files(java_root)
    class_package: Dict[str, str] = {}
    class_fqns: Dict[str, str] = {}
    class_nodes: Dict[str, object] = {}
    class_defs: Dict[str, str] = {}

    for path in files:
        source = path.read_text(encoding="utf-8", errors="ignore")
        src_bytes = source.encode("utf-8")
        tree = parser.parse(src_bytes)
        root = tree.root_node
        package = extract_package(root, src_bytes)
        for class_name, _, _, _ in extract_top_level_classes(root, src_bytes):
            fq_name = f"{package}.{class_name}" if package else class_name
            class_package[class_name] = package
            class_fqns[class_name] = fq_name
            class_defs[fq_name] = path.as_posix()
            class_nodes[fq_name] = root

    project_types = set(class_package.keys())
    graph = nx.DiGraph()
    for fq_name in class_defs.keys():
        graph.add_node(fq_name)

    for path in files:
        source = path.read_text(encoding="utf-8", errors="ignore")
        src_bytes = source.encode("utf-8")
        tree = parser.parse(src_bytes)
        root = tree.root_node
        package = extract_package(root, src_bytes)
        classes = extract_top_level_classes(root, src_bytes)
        for class_name, _, extends, implements in classes:
            current_fqn = f"{package}.{class_name}" if package else class_name
            for parent in extends + implements:
                if parent in class_fqns:
                    graph.add_edge(current_fqn, class_fqns[parent])
            deps = collect_dependencies(class_name, root, src_bytes, project_types)
            for dep in deps:
                if dep in class_fqns and dep != class_name:
                    graph.add_edge(current_fqn, class_fqns[dep])

    return graph, class_fqns, class_defs


def assign_service(class_name: str, fq_name: str, service_map: Dict[str, str]) -> str:
    if fq_name in service_map:
        return service_map[fq_name]
    if class_name in service_map:
        return service_map[class_name]
    lower = fq_name.lower()
    for pkg_segment, service in PACKAGE_SERVICE_MAP.items():
        if f".{pkg_segment}." in lower or lower.endswith(f".{pkg_segment}"):
            return service
    if class_name in CLASS_SERVICE_MAP:
        return CLASS_SERVICE_MAP[class_name]
    return "Unknown Service"


def compute_metrics(graph: nx.DiGraph, service_assignment: Dict[str, str]) -> Tuple[int, int, float, float, int]:
    total = graph.number_of_edges()
    violations = 0
    for source, target in graph.edges():
        if service_assignment.get(source) != service_assignment.get(target):
            violations += 1
    tvd = violations / total if total else 0.0
    tpd = 1.0 - tvd
    distinct_services = len({service_assignment.get(node, "Unknown Service") for node in graph.nodes()})
    return total, violations, tvd, tpd, distinct_services


def main():
    if not PETCLINIC_ROOT.exists():
        print(f"ERRO: não foi possível localizar o diretório Java do PetClinic em {PETCLINIC_ROOT}")
        sys.exit(1)

    csv_path = CSV_DIR / SERVICE_PRIORITY_CSV
    service_map = try_parse_csv_to_service_map(CSV_DIR)
    if not service_map:
        # fallback para mapeamento heurístico de pacote/classe
        print("Aviso: nenhum mapeamento classe->serviço encontrado no CSV. Usando heurísticas internas.")

    graph, class_fqns, class_defs = build_graph(PETCLINIC_ROOT)
    service_assignment = {
        fq_name: assign_service(class_name=fq_name.split('.')[-1], fq_name=fq_name, service_map=service_map)
        for fq_name in graph.nodes()
    }

    total, violations, tvd, tpd, granularity = compute_metrics(graph, service_assignment)
    print("--- PetClinic Static Analysis ---")
    print(f"Arquivos Java analisados: {len(class_defs)}")
    print(f"Total de arestas no grafo: {total}")
    print(f"Violação de serviço (aresta entre serviços diferentes): {violations}")
    print(f"TVD (Violação de Dependência de Serviço): {tvd:.4f}")
    print(f"TPD (Taxa de Pureza de Serviço): {tpd:.4f}")
    print(f"Granularidade (serviços distintos): {granularity}")
    print()
    print("Atribuição de serviço por classe:")
    for fq_name, service in sorted(service_assignment.items()):
        print(f"  {fq_name}: {service}")

    graphml_path = GRAPHML_OUTPUT
    nx.write_graphml(graph, graphml_path)
    print(f"Grafo exportado para: {graphml_path}")

    sample_edges = list(graph.edges())[:5]
    print("\n5 arestas para validação manual:")
    for source, target in sample_edges:
        print(
            f"  {source} -> {target} | {service_assignment.get(source)} -> {service_assignment.get(target)}"
        )


if __name__ == "__main__":
    main()
