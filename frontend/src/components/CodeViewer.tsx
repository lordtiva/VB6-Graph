import React, { useEffect, useRef } from 'react';
import Prism from 'prismjs';
import 'prismjs/components/prism-visual-basic';
import 'prismjs/themes/prism-tomorrow.css';
import { FileCode, ShieldAlert, Cpu, AlertTriangle } from 'lucide-react';
import axios from 'axios';

interface CodeViewerProps {
  code: string | null;
  nodeId: string | null;
}

const CodeViewer: React.FC<CodeViewerProps> = ({ code, nodeId }) => {
  const codeRef = useRef<HTMLElement>(null);
  const [impact, setImpact] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(false);

  useEffect(() => {
    if (codeRef.current && code) {
      Prism.highlightElement(codeRef.current);
    }
  }, [code]);

  useEffect(() => {
    // Reset state when node changes
    setImpact(null);
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
          <button 
            onClick={analyzeImpact}
            disabled={loading}
            className="p-1.5 hover:bg-[#30363d] rounded-lg text-[#ffa657] transition-colors"
            title="Impact Analysis (Blast Radius)"
          >
            <AlertTriangle className={`w-4 h-4 ${loading ? 'animate-pulse' : ''}`} />
          </button>
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
        <pre className="!m-0 !bg-transparent p-4">
          <code ref={codeRef} className="language-visual-basic text-sm font-mono leading-relaxed">
            {code || 'Loading...'}
          </code>
        </pre>
      </div>
    </div>
  );
};

export default CodeViewer;
