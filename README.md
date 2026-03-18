# VB6-Graph: Enterprise Code Analysis for Legacy Visual Basic 6

VB6-Graph es una plataforma profesional para el análisis de arquitectura y deuda técnica en proyectos masivos de Visual Basic 6. Utiliza un motor de **Abstract Semantic Graph (ASG)** para visualizar dependencias exactas y detectar "Code Smells" mediante algoritmos avanzados de grafos.

## 🚀 Características Principales

- **Motor ASG de Alta Precisión**: Resolución de dependencias con conciencia de *Scope* (locales vs globales), manejo de *shadowing* y nombres calificados (`Objeto.Metodo`).
- **Visualización 3D con WebGPU**: Dashboard inmersivo en 3D utilizando **Three.js** y la API **WebGPU** (con fallback a WebGL) para una fluidez total en grafos de miles de nodos.
- **Métricas Arquitectónicas**: Cálculo automático de acoplamiento aferente/eferente (**Ca/Ce**) e **Inestabilidad (I)** por archivo para identificar puntos críticos de mantenimiento.
- **Análisis de Deuda Técnica**: Detección de Código Muerto (reachability analysis), God Objects (centralidad de PageRank) y Ciclos de Dependencia.
- **Reconstrucción Paralelizada**: Script de reconstrucción ultra-rápido que reconstruye el grafo desde SQLite usando todos los núcleos de la CPU.
- **MCP Integration**: Expone herramientas de análisis para modelos de IA (Claude, GPT, Antigravity).

## 🛠️ Stack Tecnológico

- **Backend**: Python 3.11+, FastAPI, NetworkX, **python-igraph** (para layouts 3D rápidos), ANTLR4, SQLite.
- **Frontend**: React 18, TypeScript, Vite, **Three.js (WebGPU)**, Sigma.js (para vista 2D), TailwindCSS.

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
   # Instalar dependencias:
   pip install -r backend/requirements.txt
   pip install python-igraph fastapi uvicorn
   ```

3. **Frontend Setup**:

   ```bash
   cd frontend
   npm install
   ```

## 🎮 Guía de Uso Actualizada

### 1. Parseo Inicial (Fase 1)

Analiza el código fuente y genera la base de datos de conocimiento.

```bash
python backend/main.py parse <directorio_proyecto_vb6>
```

### 2. Análisis Offline (Fase 2)

Genera un reporte detallado de métricas (Inestabilidad, Ca/Ce) y "smells" directamente en tu consola y un archivo JSON.

```bash
python backend/main.py analyze
```

### 3. Reconstrucción y Layout (Opcional/Rápido)

Si ya tienes la DB, puedes reconstruir el grafo y calcular el layout 3D sin volver a leer los archivos de disco:

```bash
python backend/reconstruct_graph.py output/tu_proyecto.db
```

### 4. Iniciar Dashboard (API + Web)

1. **Terminal 1 (Backend API)**:

   ```bash
   python backend/api.py
   ```

2. **Terminal 2 (Frontend React)**:

   ```bash
   cd frontend
   npm run dev
   ```

*Accede a `http://localhost:5173` (o el puerto indicado por Vite). Usa el botón **3D (Box)** en la barra lateral para cambiar de dimensión.*

## 🤖 Configuración del Agente (MCP)

Configura tu archivo `mcp_config.json` para dar superpoderes a tu IA:

```json
{
  "mcpServers": {
    "vb6-graph": {
      "command": "C:/Ruta/A/Tu/Proyecto/backend/.venv/Scripts/python.exe",
      "args": ["C:/Ruta/A/Tu/Proyecto/backend/mcp_server.py"],
      "env": { "PYTHONPATH": "C:/Ruta/A/Tu/Proyecto/backend" }
    }
  }
}
```

## 📁 Estructura del Proyecto

- `backend/`: Motor ASG, Analizador de métricas, API FastAPI y script de reconstrucción.
- `frontend/`: Aplicación React con visualizadores Sigma.js (2D) y Three.js (3D).
- `output/`: Directorio de salida para bases de datos (`.db`) y archivos de grafos (`.graphml`) generados.

## 📄 Licencia

MIT
