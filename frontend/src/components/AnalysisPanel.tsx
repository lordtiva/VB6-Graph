import React from 'react';
import { AnalysisResults } from '../types';
import { Ghost, ShieldAlert, GitBranch, Terminal, ExternalLink, AlertCircle, Activity, BarChart3 } from 'lucide-react';
import { twMerge } from 'tailwind-merge';
import { clsx, type ClassValue } from 'clsx';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface AnalysisPanelProps {
  results: AnalysisResults | null;
  onNodeClick: (nodeId: string) => void;
}

const AnalysisPanel: React.FC<AnalysisPanelProps> = ({ results, onNodeClick }) => {
  if (!results) return (
    <div className="flex flex-col items-center justify-center h-full text-[#8b949e] p-8 text-center italic">
      <AlertCircle className="w-12 h-12 mb-4 opacity-20" />
      <p className="text-sm">No analysis results available.<br/>Try parsing the project first.</p>
    </div>
  );

  return (
    <div className="flex flex-col h-full bg-[#0d1117] overflow-hidden">
      <div className="flex-1 overflow-y-auto p-4 space-y-6 custom-scrollbar">
        
        {/* Dead Code Section */}
        <section className="space-y-3 bg-[#161b22]/30 p-3 rounded-xl border border-[#30363d]/50">
          <div className="flex items-center">
            <div className="p-1.5 bg-[#ff7b72]/10 rounded-lg mr-2.5">
              <Ghost className="w-4 h-4 text-[#ff7b72]" />
            </div>
            <div>
              <h3 className="text-[12px] font-bold text-[#c9d1d9] tracking-tight">Dead Code Detected</h3>
              <p className="text-[11px] text-[#8b949e] uppercase font-semibold">Unreachable methods & variables</p>
            </div>
            <span className="ml-auto text-[11px] font-bold bg-[#ff7b72]/10 text-[#ff7b72] px-2 py-0.5 rounded-full border border-[#ff7b72]/20">
              {results.dead_code.length}
            </span>
          </div>
          
          <div className="grid gap-1.5 max-h-72 overflow-y-auto pr-1 custom-scrollbar">
            {results.dead_code.map((method) => (
              <button 
                key={method} 
                onClick={() => onNodeClick(method)}
                className="group flex items-center bg-[#0d1117] border border-[#30363d] rounded-lg px-2.5 py-2 hover:border-[#ff7b72]/40 transition-all text-left"
              >
                <Terminal className="w-3 h-3 mr-2 text-[#ff7b72] opacity-50 group-hover:opacity-100" />
                <span className="text-[12px] font-mono text-[#c9d1d9] truncate flex-1">{method}</span>
                <ExternalLink className="w-3 h-3 text-[#30363d] group-hover:text-[#ff7b72] transition-colors ml-2" />
              </button>
            ))}
          </div>
        </section>

        {/* God Objects Section */}
        <section className="space-y-3 bg-[#161b22]/30 p-3 rounded-xl border border-[#30363d]/50">
          <div className="flex items-center">
            <div className="p-1.5 bg-[#d2a8ff]/10 rounded-lg mr-2.5">
              <ShieldAlert className="w-4 h-4 text-[#d2a8ff]" />
            </div>
            <div>
              <h3 className="text-[12px] font-bold text-[#c9d1d9] tracking-tight">God Objects</h3>
              <p className="text-[11px] text-[#8b949e] uppercase font-semibold">Overly complex components</p>
            </div>
          </div>

          <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1 custom-scrollbar">
            {results.god_objects.map((obj) => (
              <button 
                key={obj.node} 
                onClick={() => onNodeClick(obj.node)}
                className="w-full bg-[#0d1117] rounded-xl border border-[#30363d] overflow-hidden group hover:border-[#d2a8ff]/50 transition-all text-left"
              >
                <div className="p-3 flex items-start justify-between bg-gradient-to-br from-transparent to-[#d2a8ff]/5">
                  <div className="flex-1 min-w-0 pr-4">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="px-1.5 py-0.5 bg-[#30363d] text-[11px] font-bold text-[#8b949e] rounded uppercase">
                        {obj.type}
                      </span>
                    </div>
                    <p className="text-[12px] font-bold text-[#c9d1d9] truncate group-hover:text-white transition-colors">
                      {obj.node}
                    </p>
                  </div>
                  <div className="flex flex-col items-end">
                    <span className="text-[11px] font-bold text-[#8b949e] uppercase tracking-tighter mb-0.5">Complexity</span>
                    <span className="text-[12px] font-black text-[#d2a8ff] tabular-nums">{obj.score}</span>
                  </div>
                </div>
                <div className="px-3 py-1.5 bg-black/20 flex items-center justify-between">
                   <div className="flex gap-1">
                      {Array.from({length: 5}).map((_, i) => (
                        <div key={i} className={cn("w-1 h-1 rounded-full", i < (obj.score * 50) ? "bg-[#d2a8ff]" : "bg-[#30363d]")} />
                      ))}
                   </div>
                   <ExternalLink className="w-2.5 h-2.5 text-[#30363d] group-hover:text-[#d2a8ff] transition-colors" />
                </div>
              </button>
            ))}
          </div>
        </section>

        {/* Circular Dependencies Section */}
        <section className="space-y-3 bg-[#161b22]/30 p-3 rounded-xl border border-[#30363d]/50">
          <div className="flex items-center">
            <div className="p-1.5 bg-[#ffa657]/10 rounded-lg mr-2.5">
              <GitBranch className="w-4 h-4 text-[#ffa657]" />
            </div>
            <div>
              <h3 className="text-[12px] font-bold text-[#c9d1d9] tracking-tight">Architectural Cycles</h3>
              <p className="text-[11px] text-[#8b949e] uppercase font-semibold">Strongly coupled components</p>
            </div>
          </div>

          <div className="space-y-3 max-h-80 overflow-y-auto pr-1 custom-scrollbar">
            {results.circular_dependencies.map((cycle, i) => (
              <div 
                key={i} 
                className="relative bg-[#0d1117] p-3 rounded-xl border border-[#ffa657]/20 bg-gradient-to-tr from-[#0d1117] to-[#ffa65705] group"
              >
                <div className="flex flex-wrap gap-1.5 items-center">
                  {cycle.map((node, j) => (
                    <React.Fragment key={node}>
                      <button 
                        onClick={() => onNodeClick(node)}
                        className="flex items-center hover:translate-y-[-1px] transition-transform"
                      >
                        <span className="text-[9px] font-bold font-mono text-[#ffa657] bg-[#ffa657]/10 px-1.5 py-0.5 rounded shadow-sm border border-[#ffa657]/20 hover:bg-[#ffa657]/20 hover:border-[#ffa657]/40">
                          {node}
                        </span>
                      </button>
                      {j < cycle.length - 1 && (
                        <div className="mx-0.5 h-px w-2 bg-[#ffa657]/30" />
                      )}
                    </React.Fragment>
                  ))}
                </div>
                <div className="mt-2.5 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] text-[#8b949e] font-bold uppercase tracking-widest">
                      Cycle {i + 1}
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-[11px] font-black text-[#ffa657] bg-[#ffa657]/10 px-1.5 py-0.5 rounded-full border border-[#ffa657]/20">
                      {cycle.length} NODES
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
        
        {/* Architectural Stability Section */}
        {results.metrics && (
          <section className="space-y-3 bg-[#161b22]/30 p-3 rounded-xl border border-[#30363d]/50">
            <div className="flex items-center">
              <div className="p-1.5 bg-[#58a6ff]/10 rounded-lg mr-2.5">
                <BarChart3 className="w-4 h-4 text-[#58a6ff]" />
              </div>
              <div>
                <h3 className="text-[12px] font-bold text-[#c9d1d9] tracking-tight">Architectural Stability</h3>
                <p className="text-[11px] text-[#8b949e] uppercase font-semibold">Stability metrics (Ca, Ce, I)</p>
              </div>
            </div>

            <div className="space-y-3 max-h-96 overflow-y-auto pr-1 custom-scrollbar">
              {Object.entries(results.metrics)
                .sort((a, b) => b[1].instability - a[1].instability)
                .slice(0, 15)
                .map(([nodeId, metric]) => (
                <button 
                  key={nodeId} 
                  onClick={() => onNodeClick(nodeId)}
                  className="w-full bg-[#0d1117] rounded-xl border border-[#30363d] p-3 group hover:border-[#58a6ff]/50 transition-all text-left"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[12px] font-mono text-[#c9d1d9] truncate flex-1">{nodeId}</span>
                    <span className={cn(
                      "text-[11px] font-black px-1.5 py-0.5 rounded border ml-2",
                      metric.instability > 0.7 ? "text-[#ff7b72] bg-[#ff7b72]/10 border-[#ff7b72]/20" : 
                      metric.instability < 0.3 ? "text-[#7ee787] bg-[#7ee787]/10 border-[#7ee787]/20" :
                      "text-[#ffa657] bg-[#ffa657]/10 border-[#ffa657]/20"
                    )}>
                      I={metric.instability}
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 mt-2">
                    <div className="space-y-1">
                      <div className="flex justify-between text-[11px] font-bold text-[#8b949e] uppercase tracking-tighter">
                        <span>Afferent (Ca)</span>
                        <span className="text-[#c9d1d9]">{metric.afferent}</span>
                      </div>
                      <div className="h-1.5 w-full bg-[#30363d] rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-[#7ee787] transition-all duration-500" 
                          style={{ width: `${Math.min(100, (metric.afferent / 20) * 100)}%` }}
                        />
                      </div>
                    </div>
                    <div className="space-y-1">
                      <div className="flex justify-between text-[11px] font-bold text-[#8b949e] uppercase tracking-tighter">
                        <span>Efferent (Ce)</span>
                        <span className="text-[#c9d1d9]">{metric.efferent}</span>
                      </div>
                      <div className="h-1.5 w-full bg-[#30363d] rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-[#ff7b72] transition-all duration-500" 
                          style={{ width: `${Math.min(100, (metric.efferent / 20) * 100)}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
};

export default AnalysisPanel;
