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
  communityView?: boolean;
}

export const TYPE_COLORS: Record<string, string> = {
  Project: '#ff7b72',
  File: '#79c0ff',
  Method: '#7ee787',
  Variable: '#ffa657',
  UIControl: '#d2a8ff',
  External: '#6e7681',
  Unknown: '#8b949e',
};

// Vibrant color palette for communities
const COMMUNITY_COLORS = [
  '#ff7b72', '#79c0ff', '#7ee787', '#ffa657', '#d2a8ff', '#a5d6ff', '#ffa198', '#ffab70',
  '#f2cc60', '#58a6ff', '#3fb950', '#d29922', '#bc8cff', '#1f6feb', '#238636', '#9e6a03',
  '#8e1519', '#216e39', '#055d9c', '#76448a', '#117864', '#943126', '#1a5276', '#1d8348'
];

const getCommunityColor = (community: number) => {
  return COMMUNITY_COLORS[community % COMMUNITY_COLORS.length];
};

const GraphView: React.FC<GraphViewProps> = ({ data, onNodeClick, hiddenTypes, focusedNodeId, layout = 'forceAtlas2', communityView = false }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<Sigma | null>(null);

  useEffect(() => {
    if (!containerRef.current || !data.nodes.length) return;

    const graph = new Graph();

    // Add nodes
    data.nodes.forEach((node) => {
      const { type, loc, x, y, community, ...restAttributes } = node.attributes;
      const color = TYPE_COLORS[type] || TYPE_COLORS.Unknown;

      // Calculate size based on LOC using a log scale to handle Argentum's massive files
      const baseSize = loc ? Math.max(4, 3 + Math.log2(loc) * 1.5) : 5;

      graph.addNode(node.key, {
        ...restAttributes,
        nodeType: type,
        community,
        color, // Default to type color
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
  }, [data, onNodeClick]); // REMOVED communityView dependency to avoid rebuilding graph

  // Handle Layout switching
  useEffect(() => {
    if (!rendererRef.current) return;
    const graph = rendererRef.current.getGraph();

    if (layout === 'circular') {
      circular.assign(graph);
      rendererRef.current.refresh();
    } else {
      // Small timeout to allow the browser to paint the initial graph before the heavy math
      setTimeout(() => {
        if (!rendererRef.current) return;
        const g = rendererRef.current.getGraph();

        forceAtlas2.assign(g, {
          iterations: 20, // Reduced for performance
          settings: {
            scalingRatio: 12, // Slightly more separation 
            gravity: 1,
            strongGravityMode: true
          }
        });
        rendererRef.current.refresh();
      }, 100);
    }
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

      // 1. Color Logic (Community View vs Type Color)
      if (communityView && res.community !== undefined && res.community !== -1) {
        res.color = getCommunityColor(res.community);
      } else {
        res.color = TYPE_COLORS[res.nodeType] || TYPE_COLORS.Unknown;
      }

      // 2. Focused Node Logic
      if (focusedNodeId && graph.hasNode(focusedNodeId)) {
        const isNeighbor = graph.areNeighbors(node, focusedNodeId);
        const isFocus = node === focusedNodeId;

        if (isFocus) {
          res.highlighted = true;
          res.size = (res.size || 5) * 2.5;
          res.zIndex = 1000;
        } else if (isNeighbor) {
          res.label = res.label || node;
          res.alpha = 1;
          res.size = (res.size || 5) * 1.5;
          res.zIndex = 500;
        } else {
          res.label = '';
          res.color = '#1f2937'; // Slightly lighter than pure black to be sure it's not a bug
          res.opacity = 0.05;
          res.size = 2;
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
  }, [hiddenTypes, focusedNodeId, communityView]);

  return <div ref={containerRef} style={{ width: '100%', height: '100%' }} />;
};

export default GraphView;
