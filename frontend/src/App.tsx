import React, { useState, useMemo, useCallback } from 'react';
import GraphView, { TYPE_COLORS } from './components/GraphView';
import CodeViewer from './components/CodeViewer';
import AnalysisPanel from './components/AnalysisPanel';
import { useDashboard } from './hooks/useDashboard';
import { Layout, Code2, ShieldAlert, RefreshCw, Layers, Filter, Eye, EyeOff, ChevronDown, ChevronUp } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const App: React.FC = () => {
  const { graphData, analysis, selectedNodeId, code, loading, fetchCode, refreshGraph } = useDashboard();
  const [activeTab, setActiveTab] = useState<'code' | 'analysis'>('code');
  const [legendOpen, setLegendOpen] = useState(true);
  const [hiddenTypes, setHiddenTypes] = useState<Set<string>>(new Set());

  // Derive unique node types from graph data
  const availableTypes = useMemo(() => {
    if (!graphData) return [];
    const types = new Set<string>();
    graphData.nodes.forEach(n => types.add(n.attributes.type || 'Unknown'));
    return Array.from(types).sort();
  }, [graphData]);

  const toggleTypeVisibility = (type: string) => {
    setHiddenTypes(prev => {
      const next = new Set(prev);
      if (next.has(type)) next.delete(type);
      else next.add(type);
      return next;
    });
  };

  const handleNodeClick = useCallback((id: string) => {
    fetchCode(id);
    setActiveTab('code');
  }, [fetchCode]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full space-y-4">
        <RefreshCw className="w-8 h-8 animate-spin text-[#58a6ff]" />
        <p className="text-sm font-medium animate-pulse">Loading Architecture Graph...</p>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-[#0d1117] text-[#c9d1d9] overflow-hidden">
      {/* Main Sidebar/Header Area */}
      <div className="flex flex-col w-12 border-r border-[#30363d] bg-[#161b22] items-center py-4 space-y-4">
        <div className="py-2">
          <Layout className="w-6 h-6 text-[#58a6ff]" />
        </div>
        <div className="h-px w-6 bg-[#30363d]" />
        
        <button 
          onClick={() => setLegendOpen(!legendOpen)} 
          className={cn(
            "p-2 rounded-lg transition-all duration-200",
            legendOpen ? "bg-[#58a6ff]/10 text-[#58a6ff]" : "hover:bg-[#30363d] text-[#8b949e] hover:text-[#c9d1d9]"
          )}
          title="Toggle Filters"
        >
          <Filter className="w-5 h-5" />
        </button>

        <button 
          onClick={() => refreshGraph()} 
          className="p-2 hover:bg-[#30363d] rounded-lg transition-colors text-[#8b949e] hover:text-[#c9d1d9]"
          title="Refresh Graph"
        >
          <RefreshCw className="w-5 h-5" />
        </button>
      </div>

      {/* Filter Sidebar (Collapsible) */}
      <div 
        className={cn(
          "border-r border-[#30363d] bg-[#0d1117] transition-all duration-300 ease-in-out flex flex-col overflow-hidden",
          legendOpen ? "w-64 opacity-100" : "w-0 opacity-0 border-none"
        )}
      >
        <div className="p-4 border-b border-[#30363d] bg-[#161b22]/50 flex items-center justify-between">
          <h2 className="text-xs font-bold uppercase tracking-widest text-[#8b949e]">Filters</h2>
          <span className="bg-[#58a6ff]/10 text-[#58a6ff] text-[10px] px-1.5 py-0.5 rounded font-bold">
            {availableTypes.length} TYPES
          </span>
        </div>
        
        <div className="flex-1 overflow-y-auto p-2 space-y-1 custom-scrollbar">
          {availableTypes.length === 0 && (
            <div className="p-8 text-center">
              <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-[#30363d]" />
              <p className="text-xs text-[#8b949e]">Loading types...</p>
            </div>
          )}
          
          {availableTypes.map((type) => {
            const color = TYPE_COLORS[type] || TYPE_COLORS.Unknown;
            const isHidden = hiddenTypes.has(type);
            
            return (
              <button
                key={type}
                onClick={() => toggleTypeVisibility(type)}
                className={cn(
                  "w-full flex items-center justify-between group px-3 py-2.5 rounded-lg transition-all border border-transparent",
                  isHidden 
                    ? "opacity-30 grayscale hover:opacity-60 hover:grayscale-0" 
                    : "hover:bg-[#161b22] hover:border-[#30363d] active:bg-[#21262d]"
                )}
              >
                <div className="flex items-center gap-3">
                  <div 
                    className="w-3 h-3 rounded-full shadow-[0_0_8px_rgba(0,0,0,0.4)]" 
                    style={{ backgroundColor: color }}
                  />
                  <span className="text-xs font-medium text-[#c9d1d9] truncate max-w-[140px]">{type}</span>
                </div>
                <div className="flex items-center">
                  {isHidden ? (
                    <EyeOff className="w-3.5 h-3.5 text-[#8b949e]" />
                  ) : (
                    <Eye className="w-3.5 h-3.5 text-[#58a6ff] opacity-0 group-hover:opacity-100 transition-opacity" />
                  )}
                </div>
              </button>
            );
          })}
        </div>

        {graphData && (
          <div className="p-4 border-t border-[#30363d] bg-[#161b22]/30 space-y-2">
            <div className="flex justify-between text-[10px] font-bold uppercase tracking-tighter text-[#8b949e]">
              <span>Nodes</span>
              <span className="text-[#c9d1d9]">{graphData.nodes.length}</span>
            </div>
            <div className="flex justify-between text-[10px] font-bold uppercase tracking-tighter text-[#8b949e]">
              <span>Edges</span>
              <span className="text-[#c9d1d9]">{graphData.edges.length}</span>
            </div>
          </div>
        )}
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Middle Panel: Graph */}
        <div className="relative flex-1 h-full min-w-0 border-r border-[#30363d] bg-black/20">
          {/* Title overlay */}
          <div className="absolute top-4 left-4 z-50 glass px-4 py-2 rounded-lg pointer-events-none">
            <h1 className="text-sm font-bold tracking-tight flex items-center">
              <Layers className="w-4 h-4 mr-2" />
              VB6-Graph <span className="text-[#8b949e] font-normal ml-2">Argentum Online Server</span>
            </h1>
          </div>
          
          {graphData && (
            <div className="w-full h-full">
              <GraphView 
                data={graphData} 
                hiddenTypes={hiddenTypes}
                onNodeClick={handleNodeClick} 
              />
            </div>
          )}
        </div>

        {/* Right Panel: Split Side (30%) */}
        <div className="w-[30%] h-full min-w-0 flex flex-col bg-[#0d1117]">
          {/* Tabs */}
          <div className="flex border-b border-[#30363d] bg-[#161b22]">
            <button 
              onClick={() => setActiveTab('code')}
              className={cn(
                "flex-1 flex items-center justify-center py-3 text-xs font-bold uppercase tracking-widest transition-all",
                activeTab === 'code' ? "text-[#58a6ff] border-b-2 border-[#58a6ff]" : "text-[#8b949e] hover:text-[#c9d1d9]"
              )}
            >
              <Code2 className="w-4 h-4 mr-2" />
              Source Code
            </button>
            <button 
              onClick={() => setActiveTab('analysis')}
              className={cn(
                "flex-1 flex items-center justify-center py-3 text-xs font-bold uppercase tracking-widest transition-all",
                activeTab === 'analysis' ? "text-[#ffa657] border-b-2 border-[#ffa657]" : "text-[#8b949e] hover:text-[#c9d1d9]"
              )}
            >
              <ShieldAlert className="w-4 h-4 mr-2" />
              Code Smells
            </button>
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-hidden">
            {activeTab === 'code' ? (
              <CodeViewer code={code} nodeId={selectedNodeId} />
            ) : (
              <AnalysisPanel results={analysis} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
