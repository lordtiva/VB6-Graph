import React from 'react';
import { AnalysisResults } from '../types';
import { Ghost, ShieldAlert, GitBranch, Terminal, ExternalLink, AlertCircle } from 'lucide-react';
import { twMerge } from 'tailwind-merge';
import { clsx, type ClassValue } from 'clsx';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface AnalysisPanelProps {
  results: AnalysisResults | null;
}

const AnalysisPanel: React.FC<AnalysisPanelProps> = ({ results }) => {
  if (!results) return (
    <div className="flex flex-col items-center justify-center h-full text-[#8b949e] p-8 text-center italic">
      <AlertCircle className="w-12 h-12 mb-4 opacity-20" />
      <p className="text-sm">No analysis results available.<br/>Try parsing the project first.</p>
    </div>
  );

  return (
    <div className="flex flex-col h-full bg-[#0d1117]">
      <div className="flex-1 overflow-y-auto p-5 space-y-8 custom-scrollbar">
        
        {/* Dead Code Section */}
        <section className="space-y-4">
          <div className="flex items-center group">
            <div className="p-2 bg-[#ff7b72]/10 rounded-lg mr-3 group-hover:bg-[#ff7b72]/20 transition-colors">
              <Ghost className="w-5 h-5 text-[#ff7b72]" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-[#c9d1d9] tracking-tight">Dead Code Detected</h3>
              <p className="text-[10px] text-[#8b949e] uppercase font-semibold">Unreachable methods & variables</p>
            </div>
            <span className="ml-auto text-[10px] font-bold bg-[#ff7b72]/10 text-[#ff7b72] px-2 py-0.5 rounded-full border border-[#ff7b72]/20 shadow-sm">
              {results.dead_code.length}
            </span>
          </div>
          
          <div className="grid gap-2">
            {results.dead_code.slice(0, 15).map((method) => (
              <div 
                key={method} 
                className="group flex items-center bg-[#161b22] border border-[#30363d] rounded-lg px-3 py-2.5 hover:border-[#ff7b72]/40 transition-all hover:translate-x-1"
              >
                <Terminal className="w-3.5 h-3.5 mr-3 text-[#ff7b72] opacity-50 group-hover:opacity-100" />
                <span className="text-[11px] font-mono text-[#c9d1d9] truncate flex-1">{method}</span>
              </div>
            ))}
            {results.dead_code.length > 15 && (
              <div className="text-center py-2 bg-[#161b22]/50 rounded-lg border border-dashed border-[#30363d]">
                <p className="text-[#8b949e] text-[10px] font-medium tracking-wide">
                  + {results.dead_code.length - 15} ADDITIONAL ITEMS HIDDEN
                </p>
              </div>
            )}
          </div>
        </section>

        {/* God Objects Section */}
        <section className="space-y-4">
          <div className="flex items-center group">
            <div className="p-2 bg-[#d2a8ff]/10 rounded-lg mr-3 group-hover:bg-[#d2a8ff]/20 transition-colors">
              <ShieldAlert className="w-5 h-5 text-[#d2a8ff]" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-[#c9d1d9] tracking-tight">God Objects</h3>
              <p className="text-[10px] text-[#8b949e] uppercase font-semibold">Overly complex components</p>
            </div>
          </div>

          <div className="space-y-3">
            {results.god_objects.map((obj) => (
              <div 
                key={obj.node} 
                className="bg-[#161b22] rounded-xl border border-[#30363d] overflow-hidden group hover:border-[#d2a8ff]/50 transition-all"
              >
                <div className="p-4 flex items-start justify-between bg-gradient-to-br from-transparent to-[#d2a8ff]/5">
                  <div className="flex-1 min-w-0 pr-4">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="px-1.5 py-0.5 bg-[#30363d] text-[9px] font-bold text-[#8b949e] rounded uppercase">
                        {obj.type}
                      </span>
                    </div>
                    <p className="text-xs font-bold text-[#c9d1d9] truncate group-hover:text-white transition-colors">
                      {obj.node}
                    </p>
                  </div>
                  <div className="flex flex-col items-end">
                    <span className="text-[9px] font-bold text-[#8b949e] uppercase tracking-tighter mb-1">Complexity</span>
                    <span className="text-sm font-black text-[#d2a8ff] tabular-nums">{obj.score}</span>
                  </div>
                </div>
                <div className="px-4 py-2 bg-black/20 flex items-center justify-between">
                   <div className="flex gap-1">
                      {Array.from({length: 5}).map((_, i) => (
                        <div key={i} className={cn("w-1.5 h-1.5 rounded-full", i < (obj.score * 50) ? "bg-[#d2a8ff]" : "bg-[#30363d]")} />
                      ))}
                   </div>
                   <ExternalLink className="w-3 h-3 text-[#8b949e] group-hover:text-[#d2a8ff] transition-colors" />
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Circular Dependencies Section */}
        <section className="space-y-4">
          <div className="flex items-center group">
            <div className="p-2 bg-[#ffa657]/10 rounded-lg mr-3 group-hover:bg-[#ffa657]/20 transition-colors">
              <GitBranch className="w-5 h-5 text-[#ffa657]" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-[#c9d1d9] tracking-tight">Architectural Cycles</h3>
              <p className="text-[10px] text-[#8b949e] uppercase font-semibold">Strongly coupled components</p>
            </div>
          </div>

          <div className="space-y-4">
            {results.circular_dependencies.slice(0, 8).map((cycle, i) => (
              <div 
                key={i} 
                className="relative bg-[#161b22] p-4 rounded-xl border border-[#ffa657]/20 bg-gradient-to-tr from-[#161b22] to-[#ffa65710] group"
              >
                <div className="flex flex-wrap gap-2 items-center">
                  {cycle.map((node, j) => (
                    <React.Fragment key={node}>
                      <div className="flex items-center">
                        <span className="text-[10px] font-bold font-mono text-[#ffa657] bg-[#ffa657]/10 px-2 py-1 rounded shadow-sm border border-[#ffa657]/20">
                          {node}
                        </span>
                        {j < cycle.length - 1 && (
                          <div className="mx-1 h-px w-3 bg-[#ffa657]/30" />
                        )}
                      </div>
                    </React.Fragment>
                  ))}
                </div>
                <div className="mt-3 flex items-center justify-between">
                  <span className="text-[9px] text-[#8b949e] font-bold uppercase tracking-widest">
                    Cycle {i + 1}
                  </span>
                  <div className="text-[9px] text-[#8b949e] italic">
                    Points: {cycle.length}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
};

export default AnalysisPanel;
