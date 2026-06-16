from pathlib import Path
from datetime import datetime
import csv
import re
import collections

base = Path('project_descriptions/PetClinic/petclinic_dependency_graph.graphml')
text = base.read_text(encoding='utf-8')
node_re = re.compile(r'<node id="([^"]+)" */>')
edge_re = re.compile(r'<edge source="([^"]+)" target="([^"]+)" */>')
nodes = node_re.findall(text)
edges = edge_re.findall(text)

stamp = datetime.now().strftime('%Y%m%d%H%M%S')
copy_path = base.with_name(f'petclinic_dependency_graph.{stamp}.graphml')
copy_path.write_text(text, encoding='utf-8')

csv_path = base.with_name('petclinic_dependency_graph_edges.csv')
with csv_path.open('w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['source', 'target', 'type'])
    for source, target in edges:
        typ = 'unknown'
        if source in ('NamedEntity', 'Person', 'Owner', 'Pet', 'PetType', 'Visit', 'Vet', 'Specialty') and target in ('BaseEntity', 'Person', 'NamedEntity'):
            typ = 'extends'
        elif source in ('PetValidator', 'WebConfiguration') and target in ('Validator', 'WebMvcConfigurer'):
            typ = 'implements'
        elif source in ('OwnerRepository', 'PetTypeRepository', 'VetRepository') and target in ('Owner', 'PetType', 'Vet'):
            typ = 'repository'
        elif source in ('PetController', 'OwnerController', 'VisitController', 'VetController', 'PetTypeFormatter') and target.endswith('Repository'):
            typ = 'injection'
        elif source == 'Vets' and target == 'Vet':
            typ = 'composition'
        elif source in ('Owner', 'Pet', 'Vet') and target in ('Pet', 'Visit', 'PetType', 'Specialty'):
            typ = 'jpa'
        writer.writerow([source, target, typ])

deg = collections.Counter()
for s, t in edges:
    deg[s] += 1
    deg[t] += 1
isolated = [n for n in nodes if deg[n] == 0]
degree1 = [n for n in nodes if deg[n] == 1]

report = (
    f'copy_path={copy_path}\n'
    f'csv_path={csv_path}\n'
    f'nodes={len(nodes)}\n'
    f'edges={len(edges)}\n'
    f'isolated={"|".join(isolated)}\n'
    f'degree1={"|".join(degree1)}'
)
Path('project_descriptions/PetClinic/petclinic_dependency_graph_audit.txt').write_text(report, encoding='utf-8')
print('copy_path', copy_path)
print('csv_path', csv_path)
print('isolated', isolated)
print('degree1', degree1)
