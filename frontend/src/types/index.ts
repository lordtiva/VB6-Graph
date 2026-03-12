export type NodeType = 'Project' | 'File' | 'Method' | 'Variable' | 'UIControl' | 'Unknown';

export interface NodeAttributes {
  label: string;
  type: NodeType;
  size: number;
  x: number;
  y: number;
  color?: string;
  loc?: number;
}

export interface GraphNode {
  key: string;
  attributes: NodeAttributes;
}

export interface GraphEdge {
  source: string;
  target: string;
  attributes: {
    type: string;
    color?: string;
  };
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface AnalysisResults {
  dead_code: string[];
  god_objects: Array<{
    node: string;
    type: string;
    score: number;
  }>;
  circular_dependencies: string[][];
}
