import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import Prism from 'prismjs';
import 'prismjs/components/prism-visual-basic';
import 'prismjs/themes/prism-tomorrow.css';
import { GraphData, AnalysisResults } from '../types';

export const useDashboard = () => {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResults | null>(null);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [code, setCode] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchGraph = useCallback(async () => {
    try {
      setLoading(true);
      const res = await axios.get('/api/graph');
      setGraphData(res.data);
      setLoading(false);
    } catch (err) {
      setError('Error charging graph');
      setLoading(false);
    }
  }, []);

  const fetchAnalysis = useCallback(async () => {
    try {
      const res = await axios.get('/api/analysis');
      console.log('[Dashboard] Received analysis results:', res.data);
      setAnalysis(res.data);
    } catch (err) {
      console.error('[Dashboard] Error fetching analysis', err);
    }
  }, []);

  const fetchCode = useCallback(async (nodeId: string) => {
    try {
      setSelectedNodeId(nodeId);
      const res = await axios.get(`/api/code/${encodeURIComponent(nodeId)}`);
      setCode(res.data.code);
    } catch (err) {
      setCode('-- Code not found --');
    }
  }, []);

  useEffect(() => {
    fetchGraph();
    fetchAnalysis();
  }, [fetchGraph, fetchAnalysis]);

  useEffect(() => {
    if (code) {
      Prism.highlightAll();
    }
  }, [code]);

  return {
    graphData,
    analysis,
    selectedNodeId,
    code,
    loading,
    error,
    fetchCode,
    refreshGraph: fetchGraph
  };
};
