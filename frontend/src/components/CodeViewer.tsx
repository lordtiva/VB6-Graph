import React, { useEffect, useRef } from 'react';
import Prism from 'prismjs';
import 'prismjs/components/prism-visual-basic';
import 'prismjs/themes/prism-tomorrow.css';
import { FileCode, ShieldAlert, Cpu, AlertTriangle, Zap, Split, ArrowLeft } from 'lucide-react';
import axios from 'axios';

interface CodeViewerProps {
  code: string | null;
  nodeId: string | null;
}

const CodeViewer: React.FC<CodeViewerProps> = ({ code, nodeId }) => {
  const codeRef = useRef<HTMLElement>(null);
  const refactorRef = useRef<HTMLElement>(null);
  const [impact, setImpact] = React.useState<any>(null);
  const [refactoredCode, setRefactoredCode] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [isDiffView, setIsDiffView] = React.useState(false);

  useEffect(() => {
    if (codeRef.current && code) {
      Prism.highlightElement(codeRef.current);
    }
    if (refactorRef.current && refactoredCode) {
      Prism.highlightElement(refactorRef.current);
    }
  }, [code, refactoredCode, isDiffView]);

  useEffect(() => {
    // Reset state when node changes
    setImpact(null);
    setRefactoredCode(null);
    setIsDiffView(false);
  }, [nodeId]);

  const analyzeImpact = async () => {
    if (!nodeId) return;
    setLoading(true);
    try {
      const res = await axios.get(`http://localhost:8000/api/impact/${encodeURIComponent(nodeId)}`);
      setImpact(res.data);
    } finally {
      setLoading(false);
    }
  };

  const refactorCode = async () => {
    if (!nodeId || !code) return;
    setLoading(true);
    try {
      const res = await axios.post(`http://localhost:8000/api/refactor`, { 
        node_id: nodeId, 
        code 
      });
      setRefactoredCode(res.data.refactored);
      setIsDiffView(true);
    } finally {
      setLoading(false);
    }
  };

  if (!nodeId) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-[#8b949e]">
        <Cpu className="w-12 h-12 mb-4 opacity-20" />
        <p>Select a node in the graph to view source code</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-[#0d1117]">
      <div className="flex items-center justify-between px-4 py-2 border-b border-[#30363d] bg-[#161b22]">
        <div className="flex items-center min-w-0">
          <FileCode className="w-4 h-4 mr-2 text-[#58a6ff] shrink-0" />
          <span className="text-xs font-mono truncate">{nodeId}</span>
        </div>
        <div className="flex gap-2">
          {!isDiffView ? (
            <>
              <button 
                onClick={analyzeImpact}
                disabled={loading}
                className="p-1.5 hover:bg-[#30363d] rounded-lg text-[#ffa657] transition-colors"
                title="Impact Analysis (Blast Radius)"
              >
                <AlertTriangle className={`w-4 h-4 ${loading ? 'animate-pulse' : ''}`} />
              </button>
              <button 
                onClick={refactorCode}
                disabled={loading || !code}
                className="p-1.5 hover:bg-[#30363d] rounded-lg text-[#7ee787] transition-colors"
                title="AI Refactor"
              >
                <Zap className={`w-4 h-4 ${loading ? 'animate-pulse' : ''}`} />
              </button>
            </>
          ) : (
            <button 
              onClick={() => setIsDiffView(false)}
              className="p-1.5 hover:bg-[#30363d] rounded-lg text-[#8b949e] transition-colors"
              title="Back to Code"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {impact && (
        <div className="bg-[#ffa657]/10 border-b border-[#30363d] p-3 animate-in slide-in-from-top duration-200">
          <div className="flex items-center gap-2 mb-1">
            <AlertTriangle className="w-4 h-4 text-[#ffa657]" />
            <span className="text-xs font-bold text-[#ffa657]">Blast Radius Analysis</span>
          </div>
          <p className="text-[11px] text-[#c9d1d9]">
            Modifying this will affect <span className="font-bold">{impact.impact_count}</span> entities:
            <br />
            {impact.files.length} files, {impact.methods.length} methods, {impact.ui_controls.length} UI controls.
          </p>
        </div>
      )}

      <div className="flex-1 overflow-auto custom-scrollbar relative">
        {!isDiffView ? (
          <pre className="!m-0 !bg-transparent p-4">
            <code ref={codeRef} className="language-visual-basic text-sm font-mono leading-relaxed">
              {code || 'Loading...'}
            </code>
          </pre>
        ) : (
          <div className="flex h-full divide-x divide-[#30363d]">
            <div className="flex-1 overflow-auto p-4 bg-red-950/20">
              <div className="text-[10px] font-bold text-red-400 mb-2 uppercase tracking-widest">Original</div>
              <pre className="!m-0 !bg-transparent">
                <code ref={codeRef} className="language-visual-basic text-xs opacity-80">
                  {code}
                </code>
              </pre>
            </div>
            <div className="flex-1 overflow-auto p-4 bg-green-950/20">
              <div className="text-[10px] font-bold text-green-400 mb-2 uppercase tracking-widest">AI Proposal</div>
              <pre className="!m-0 !bg-transparent">
                <code ref={refactorRef} className="language-visual-basic text-xs">
                  {refactoredCode}
                </code>
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CodeViewer;
