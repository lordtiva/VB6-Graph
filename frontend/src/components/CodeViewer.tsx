import React, { useEffect, useRef } from 'react';
import Prism from 'prismjs';
import 'prismjs/components/prism-visual-basic';
import 'prismjs/themes/prism-tomorrow.css';
import { FileCode, ShieldAlert, Cpu } from 'lucide-react';

interface CodeViewerProps {
  code: string | null;
  nodeId: string | null;
}

const CodeViewer: React.FC<CodeViewerProps> = ({ code, nodeId }) => {
  const codeRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (codeRef.current && code) {
      Prism.highlightElement(codeRef.current);
    }
  }, [code]);

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
      <div className="flex items-center px-4 py-3 border-b border-[#30363d] bg-[#161b22]">
        <FileCode className="w-4 h-4 mr-2 text-[#58a6ff]" />
        <span className="text-xs font-mono truncate">{nodeId}</span>
      </div>
      <div className="flex-1 overflow-auto p-4 custom-scrollbar">
        <pre className="!m-0 !bg-transparent !p-0">
          <code ref={codeRef} className="language-visual-basic text-sm font-mono leading-relaxed">
            {code || 'Loading...'}
          </code>
        </pre>
      </div>
    </div>
  );
};

export default CodeViewer;
