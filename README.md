# VB6-Graph: Enterprise Code Analysis for Legacy Visual Basic 6

VB6-Graph es una plataforma profesional para el análisis de arquitectura y deuda técnica en proyectos masivos de Visual Basic 6. Utiliza un motor de **Code Property Graph (CPG)** para visualizar dependencias y detectar "Code Smells" mediante algoritmos de grafos.

## 🚀 Características

- **Análisis de Deuda Técnica**: Detección automática de Código Muerto, God Objects y Ciclos de Dependencia.
- **Visualización WebGL**: Dashboard interactivo capaz de manejar miles de nodos mediante **Sigma.js**.
- **Motor de Grafo**: Basado en **NetworkX** para tracing de llamadas (`CALLS`), uso de variables (`USES`) y eventos UI (`TRIGGERS`).
- **MCP Integration**: Expone herramientas de análisis para modelos de IA (Claude, GPT).

## 🛠️ Stack Tecnológico

- **Backend**: Python 3.11+, Typer (CLI), FastAPI (API REST), NetworkX, SQLite.
- **Frontend**: React 18, TypeScript, Vite, Sigma.js, Prism.js.

## 📥 Instalación

1. **Clonar el repositorio**:

   ```bash
   git clone https://github.com/lordtiva/VB6-Graph.git
   cd VB6-Graph
   ```

2. **Backend Setup**:

   ```bash
   python -m venv backend/.venv
   # Windows:
   backend\.venv\Scripts\activate
   # Linux/MacOS:
   source backend/.venv/bin/activate

   pip install -r backend/requirements.txt
   ```

3. **Frontend Setup**:

   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

## 🎮 Guía de Uso

El proyecto se gestiona íntegramente a través de la CLI unificada en `backend/main.py`.

### Fase 1: Parseo del Código

Analiza un directorio de código VB6 y genera la base de datos y el grafo de arquitectura.

```bash
python backend/main.py parse <directorio_proyecto_vb6>
```

*Los archivos generados (`.db`, `.graphml`) se guardarán automáticamente en la carpeta `/output`.*

### Fase 2: Análisis de Deuda Técnica

Genera un informe detallado sobre la salud del código.

```bash
python backend/main.py analyze
```

*Muestra un resumen por consola y genera un reporte JSON detallado en `/output` (ej. `Proyecto_analysis.json`).*

### Fase 3: Dashboard Interactivo

Inicia el ecosistema completo (API + UI).

1. **Terminal 1 (API)**:

   ```bash
   python backend/main.py ui
   ```

2. **Terminal 2 (Frontend)**:

   ```bash
   cd frontend
   npm run dev
   ```

*Accede a `http://localhost:5173` para explorar el grafo de arquitectura y visualizar el código fuente.*

### Fase 4: Servidor MCP (Para IAs)

```bash
python backend/main.py mcp <directorio_proyecto_vb6>
```

## 📁 Estructura del Proyecto

- `backend/`: Código Python (CLI, API, Parser, Analyzer).
- `frontend/`: Aplicación React + Sigma.js para visualización.
- `output/`: Directorio de salida para bases de datos, grafos y reportes de análisis.

## 📄 Licencia

MIT
