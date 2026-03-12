import React, { useEffect, useRef } from 'react';
import Sigma from 'sigma';
import Graph from 'graphology';
import forceAtlas2 from 'graphology-layout-forceatlas2';
import circular from 'graphology-layout/circular';
import { GraphData, NodeAttributes } from '../types';

export type LayoutType = 'forceAtlas2' | 'circular';

interface GraphViewProps {
  data: GraphData;
  onNodeClick: (nodeId: string) => void;
  hiddenTypes: Set<string>;
  focusedNodeId?: string | null;
  layout?: LayoutType;
}

export const TYPE_COLORS: Record<string, string> = {
  Project: '#ff7b72',
  File: '#79c0ff',
  Method: '#7ee787',
  Variable: '#ffa657',
  UIControl: '#d2a8ff',
  Unknown: '#8b949e',
};

const GraphView: React.FC<GraphViewProps> = ({ data, onNodeClick, hiddenTypes, focusedNodeId, layout = 'forceAtlas2' }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<Sigma | null>(null);

  useEffect(() => {
    if (!containerRef.current || !data.nodes.length) return;

    const graph = new Graph();

    // Add nodes
    data.nodes.forEach((node) => {
      const { type, loc, x, y, ...restAttributes } = node.attributes;
      const color = TYPE_COLORS[type] || TYPE_COLORS.Unknown;
      
      // Calculate size based on LOC using a log scale to handle Argentum's massive files
      const baseSize = loc ? Math.max(4, 3 + Math.log2(loc) * 1.5) : 5;

      graph.addNode(node.key, {
        ...restAttributes,
        nodeType: type,
        color,
        size: baseSize,
        x: x || Math.random() * 100,
        y: y || Math.random() * 100,
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

  // Handle Layout switching
  useEffect(() => {
    if (!rendererRef.current) return;
    const graph = rendererRef.current.getGraph();

    if (layout === 'circular') {
      circular.assign(graph);
    } else {
      // Backend already calculated layout, we only run a few iterations to refine or animate
      forceAtlas2.assign(graph, { iterations: 5, settings: { gravity: 1 } });
    }
    
    rendererRef.current.refresh();
  }, [layout, data]); // Also run on data change to ensure layout is applied to new nodes

  // Handle camera focus on search
  useEffect(() => {
    if (!rendererRef.current || !focusedNodeId) return;
    const renderer = rendererRef.current;
    const graph = renderer.getGraph();

    if (graph.hasNode(focusedNodeId)) {
      const nodeDisplayData = renderer.getNodeDisplayData(focusedNodeId);
      if (nodeDisplayData) {
        renderer.getCamera().animate(
          { x: nodeDisplayData.x, y: nodeDisplayData.y, ratio: 0.15 },
          { duration: 600 }
        );
      }
    }
  }, [focusedNodeId]);

  // Handle visibility filtering and highlighting
  useEffect(() => {
    if (!rendererRef.current) return;
    const renderer = rendererRef.current;

    renderer.setSetting('nodeReducer', (node: string, nodeData: any) => {
      const res = { ...nodeData };
      const graph = renderer.getGraph();

      if (hiddenTypes.has(res.nodeType)) {
        res.hidden = true;
      }
      
      // If there is a focused node, dim others but keep neighbors visible
      if (focusedNodeId && graph.hasNode(focusedNodeId)) {
        const isNeighbor = graph.areNeighbors(node, focusedNodeId);
        const isFocus = node === focusedNodeId;

        if (isFocus) {
          res.highlighted = true;
          res.size = (res.size || 5) * 2.0; // Make focus node even larger
          res.zIndex = 1000;
        } else if (isNeighbor) {
          res.label = res.label || node;
          res.alpha = 1;
          res.size = (res.size || 5) * 1.5;
          res.zIndex = 500;
        } else {
          res.label = '';
          res.color = '#161b22';
          res.opacity = 0.05;
          res.size = 2; // DRASTICALLY SHRINK inactive nodes to prevent overlap
          res.zIndex = -1;
        }
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

        if (focusedNodeId) {
          const isRelated = source === focusedNodeId || target === focusedNodeId;
          if (!isRelated) {
            res.hidden = true;
          } else {
            res.color = source === focusedNodeId ? '#58a6ff' : '#ffa657';
            res.size = 2;
            res.zIndex = 2000; // Edges even higher to be sure they are visible
          }
        }
      }
      return res;
    });

    renderer.refresh();
  }, [hiddenTypes, focusedNodeId]);

  return <div ref={containerRef} style={{ width: '100%', height: '100%' }} />;
};

export default GraphView;
