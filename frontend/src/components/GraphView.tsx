import React, { useEffect, useRef } from 'react';
import Sigma from 'sigma';
import Graph from 'graphology';
import forceAtlas2 from 'graphology-layout-forceatlas2';
import { GraphData, NodeAttributes } from '../types';

interface GraphViewProps {
  data: GraphData;
  onNodeClick: (nodeId: string) => void;
  hiddenTypes: Set<string>;
}

export const TYPE_COLORS: Record<string, string> = {
  Project: '#ff7b72',
  File: '#79c0ff',
  Method: '#7ee787',
  Variable: '#ffa657',
  UIControl: '#d2a8ff',
  Unknown: '#8b949e',
};

const GraphView: React.FC<GraphViewProps> = ({ data, onNodeClick, hiddenTypes }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<Sigma | null>(null);

  useEffect(() => {
    if (!containerRef.current || !data.nodes.length) return;

    const graph = new Graph();

    // Add nodes
    data.nodes.forEach((node) => {
      const { type, ...restAttributes } = node.attributes;
      const color = TYPE_COLORS[type] || TYPE_COLORS.Unknown;
      graph.addNode(node.key, {
        ...restAttributes,
        nodeType: type,
        color,
        size: restAttributes.size || 5,
        x: Math.random() * 100,
        y: Math.random() * 100,
      });
    });

    // Add edges
    data.edges.forEach((edge) => {
      if (graph.hasNode(edge.source) && graph.hasNode(edge.target)) {
        const { type: edgeType, ...restEdgeAttr } = edge.attributes;
        graph.addEdge(edge.source, edge.target, {
          ...restEdgeAttr,
          edgeType,
          color: '#30363d',
          size: 1,
        });
      }
    });

    // Run layout
    forceAtlas2.assign(graph, { iterations: 100, settings: { gravity: 1 } });

    // Initialize Sigma
    const renderer = new Sigma(graph, containerRef.current, {
      renderLabels: true,
      labelFont: 'Inter',
      labelColor: { color: '#8b949e' },
      defaultNodeType: 'circle',
      defaultEdgeType: 'arrow',
    });

    renderer.on('clickNode', ({ node }) => {
      onNodeClick(node);
    });

    rendererRef.current = renderer;

    return () => {
      if (rendererRef.current) {
        rendererRef.current.kill();
        rendererRef.current = null;
      }
    };
  }, [data, onNodeClick]);

  // Handle visibility filtering without recreating graph
  useEffect(() => {
    if (!rendererRef.current) return;
    const renderer = rendererRef.current;

    renderer.setSetting('nodeReducer', (node: string, nodeData: any) => {
      const res = { ...nodeData };
      if (hiddenTypes.has(res.nodeType)) {
        res.hidden = true;
      }
      return res;
    });

    renderer.setSetting('edgeReducer', (edge: string, edgeData: any) => {
      const res = { ...edgeData };
      const graph = renderer.getGraph();
      if (!graph.hasEdge(edge)) return res;

      const source = graph.source(edge);
      const target = graph.target(edge);

      if (graph.hasNode(source) && graph.hasNode(target)) {
        const sourceType = graph.getNodeAttribute(source, 'nodeType');
        const targetType = graph.getNodeAttribute(target, 'nodeType');

        if (hiddenTypes.has(sourceType) || hiddenTypes.has(targetType)) {
          res.hidden = true;
        }
      }
      return res;
    });

    renderer.refresh();
  }, [hiddenTypes]);

  return <div ref={containerRef} style={{ width: '100%', height: '100%' }} />;
};

export default GraphView;
