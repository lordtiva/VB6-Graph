# VB6-Graph: Code Property Graph for Legacy Visual Basic 6

VB6-Graph is a tool designed to parse legacy Visual Basic 6 projects, generate a **Code Property Graph (CPG)**, and expose it via the **Model Context Protocol (MCP)** for AI-assisted analysis and an interactive HTML visualization for humans.

## 🚀 Features

- **Deep Parsing**: Extracts Projects, Files, Methods (Sub, Function, Property), Global Variables, and UI Controls using advanced Regex.

- **Relationship Mapping**:
  - `CONTAINS`: Structural hierarchy.
  - `CALLS`: Method-to-method invocation tracing.
  - `USES`: Global variable usage.
  - `TRIGGERS`: UI Control to event handler mapping (e.g., `CommandButton` -> `_Click`).
- **Dual Exposure**:
  - **LLM Ready**: Official MCP SDK server to provide tools to AI models.
  - **Human Friendly**: Interactive 2D/3D graph visualization using PyVis.
- **Hybrid Storage**: Fast in-memory relationships (NetworkX) and persistent source code storage (SQLite).

## 🛠️ Tech Stack

- **Language**: Python 3.11+
- **Graph Engine**: [NetworkX](https://networkx.org/)
- **Storage**: SQLite3
- **MCP Framework**: [Model Context Protocol Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- **Visualization**: [PyVis](https://pyvis.readthedocs.io/)

## 📥 Installation & Setup

1. **Clone the repository**:

    ```bash
    git clone <repository-url>
    cd VB6-Graph
    ```

2. **Create and activate a Virtual Environment**:

    ```bash
    python -m venv .venv
    # Windows:
    .venv\Scripts\activate
    # Linux/MacOS:
    source .venv/bin/activate
    ```

3. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

## 🎮 Usage

### 1. Parse and Visualize

To generate the graph and the interactive HTML visualization:

```bash
python visualizer.py <path_to_vb6_project_directory>
```

*Result: Generates `visualizacion.html` which you can open in any browser.*

### 2. Run the MCP Server

To expose the graph tools to an MCP-compatible client (like Claude Desktop or another LLM agent):

```bash
python mcp_server.py
```

#### Available MCP Tools

- `get_project_structure()`: Lists files and their contents.
- `get_method_dependencies(method_name)`: Traces who calls a method and what it calls.
- `get_source_code(node_id)`: Retrieves the literal code for any node.
- `trace_ui_event(form_name, control_name)`: Maps a UI element to its logic.

## 📁 Project Structure

- `parser.py`: The core engine that reads VB6 files and builds the NetworkX graph.
- `db.py`: SQLite interface for storing and retrieving source code blocks.
- `mcp_server.py`: FastMCP implementation for AI tool exposure.
- `visualizer.py`: PyVis exporter for the interactive HTML graph.
- `sample_project/`: A minimal VB6 project for testing purposes.

## 📄 License

MIT
