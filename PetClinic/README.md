# PetClinic - Análise Estática e Grafo de Dependências

Este repositório contém as ferramentas e scripts utilizados para realizar análise estática, construção de grafo de dependências e detecção de violações estruturais no projeto **Spring PetClinic**. O trabalho faz parte de um experimento piloto sobre decomposição de monolítos em microsserviços com auxílio de LLMs.

## Scripts

| Arquivo | Descrição |
|---|---|
| `petclinic_static_analysis.py` | Script principal. Faz parsing AST com Tree-sitter, constrói o grafo com NetworkX e calcula métricas de aderência. |
| `graph_audit.py` | Auditoria do grafo: backup timestamped, exportação CSV, cálculo de grau, identificação de nós isolados. |
| `violation_detection.py` | Detecta violações estruturais cruzando o grafo real com decomposições geradas por LLMs (fewshot/zeroshot). |
| `analysis_methodology.md` | Documentação completa da metodologia, ferramentas e processo executado. |

## Pré-requisitos

- Python 3.8+
- [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) com a gramática Java
- [NetworkX](https://networkx.org/)
- [Pandas](https://pandas.pydata.org/)

### Instalação das Dependências

```bash
pip install tree-sitter tree-sitter-java networkx pandas
```

Caso `tree-sitter-java` não esteja disponível, instale o pacote alternativo:

```bash
pip install tree-sitter-languages
```

## Como Usar

### 1. Análise Estática e Construção do Grafo

Execute o script principal apontando para o diretório do código-fonte Java:

```bash
python petclinic_static_analysis.py
```

O script irá:
- Percorrer todos os arquivos `.java` no diretório configurado
- Fazer parsing AST com Tree-sitter para extrair classes, heranças, implementações, campos tipados e invocações
- Construir um grafo direcionado (DiGraph) com NetworkX
- Exportar o grafo para `petclinic_dependency_graph.graphml`
- Exibir métricas no terminal (arestas, violações, TVD, TPD, granularidade)

### 2. Auditoria do Grafo

```bash
python graph_audit.py
```

O script irá:
- Fazer uma cópia timestamped do GraphML (`petclinic_dependency_graph.YYYYMMDDHHMMSS.graphml`)
- Exportar todas as arestas para CSV (`petclinic_dependency_graph_edges.csv`)
- Calcular o grau de cada nó
- Identificar nós isolados (grau 0) e nós com grau 1
- Gerar relatório de auditoria (`petclinic_dependency_graph_audit.txt`)

### 3. Detecção de Violações Estruturais

```bash
python violation_detection.py
```

O script irá:
- Carregar o CSV de arestas do grafo real
- Carregar decomposições LLM de CSVs (fewshot e zeroshot) da pasta `csv/`
- Detectar violações (arestas que cruzam serviços diferentes)
- Calcular métricas: TVD, CB (Coesão Básica) e Granularidade
- Gerar relatório comparativo em `petclinic_violations_report.md`
- Exportar dados brutos para `petclinic_violations_analysis.json`

## Como Adaptar para Outros Projetos

### 1. Configurar o Caminho do Código-Fonte

No arquivo `petclinic_static_analysis.py`, localize e altere a variável `PETCLINIC_ROOT` (linhas 33-44) para apontar para o diretório raiz do código-fonte do **seu** projeto:

```python
PETCLINIC_ROOT = (
    BASE_DIR
    / "caminho"
    / "para"
    / "seu"
    / "projeto"
    / "src"
    / "main"
    / "java"
)
```

### 2. (Opcional) Personalizar o Mapeamento de Serviços

Se você quiser atribuir classes a microsserviços para detecção de violações, edite os dicionários:

- `PACKAGE_SERVICE_MAP` (linha 49) — mapeia nomes de pacotes para serviços
- `CLASS_SERVICE_MAP` (linha 57) — mapeia nomes de classes individuais para serviços

Ou forneça um CSV na pasta `csv/` com as colunas `class` e `service`.

### 3. (Opcional) Ajustar para Outra Linguagem

O script usa Tree-sitter com gramática Java. Para analisar projetos em **outras linguagens**:

1. Instale a gramática correspondente, por exemplo:
   - Python: `pip install tree-sitter-python`
   - JavaScript/TypeScript: `pip install tree-sitter-javascript tree-sitter-typescript`
   - C#: `pip install tree-sitter-c-sharp`
   - Go: `pip install tree-sitter-go`
2. Altere a linha de inicialização do parser no script:

```python
# Para Python:
from tree_sitter import Language
import tree_sitter_python
LANGUAGE = Language(tree_sitter_python.language())

# Para JavaScript:
from tree_sitter import Language
import tree_sitter_javascript
LANGUAGE = Language(tree_sitter_javascript.language())
```

3. Ajuste as funções de extração (`extract_top_level_classes`, `collect_dependencies`) conforme a AST da linguagem alvo — os nomes dos nós variam entre gramáticas.

### 4. Executar em Lote para Múltiplos Projetos

Para aplicar os scripts a vários projetos, crie um script wrapper que:

1. Copie os arquivos para cada diretório de projeto
2. Altere `PETCLINIC_ROOT` dinamicamente
3. Execute `petclinic_static_analysis.py` e `graph_audit.py` para cada um
4. Consolide os resultados

Exemplo conceitual:

```python
projetos = ["projeto-a", "projeto-b", "projeto-c"]
for proj in projetos:
    configurar_caminho(proj)
    exec(open("petclinic_static_analysis.py").read())
    exec(open("graph_audit.py").read())
```

## Estrutura de Diretórios Esperada

```
project_descriptions/PetClinic/
├── petclinic_static_analysis.py    # Script principal
├── graph_audit.py                   # Auditoria
├── violation_detection.py           # Detecção de violações
├── analysis_methodology.md          # Documentação
├── csv/                             # CSVs de decomposição LLM
│   ├── petclinic-fewshot-results.csv
│   └── petclinic-zeroshot-results.csv
├── monolito/                        # Código-fonte do monolito
│   └── spring-petclinic-main/
│       └── src/main/java/...
├── petclinic_dependency_graph.graphml
├── petclinic_dependency_graph_edges.csv
├── petclinic_dependency_graph_audit.txt
├── petclinic_report.md
├── petclinic_violations_report.md
└── petclinic_violations_analysis.json
```

## Artefatos Gerados

| Artefato | Formato | Descrição |
|---|---|---|
| `petclinic_dependency_graph.graphml` | GraphML | Grafo de dependências completo |
| `petclinic_dependency_graph_edges.csv` | CSV | Arestas do grafo (source, target, type) |
| `petclinic_dependency_graph_audit.txt` | Texto | Auditoria: nós, arestas, isolados, grau 1 |
| `petclinic_report.md` | Markdown | Relatório consolidado da análise |
| `petclinic_violations_report.md` | Markdown | Relatório de violações estruturais |
| `petclinic_violations_analysis.json` | JSON | Dados brutos da análise de violações |

## Limitações

- A análise é estática e limitada ao código-fonte em `src/main/java`
- Dependências runtime, reflexão, beans dinâmicos e código de teste não são capturados
- O grafo modela relações estruturais estáticas, não fluxo de execução
- Para outras linguagens, é necessário ajustar as funções de extração conforme a AST específica
- A função `collect_dependencies()` usa correspondência textual por substring, o que pode gerar falsos positivos em nomes de classes similares

## Licença

Este projeto faz parte de pesquisa acadêmica. Consulte o repositório principal para termos de uso.