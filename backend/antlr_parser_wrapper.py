import sys
import os
import antlr4
from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker

# Add antlr directory to path for imports
antlr_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "antlr")
sys.path.append(antlr_dir)

from VisualBasic6Lexer import VisualBasic6Lexer
from VisualBasic6Parser import VisualBasic6Parser
from VisualBasic6ParserVisitor import VisualBasic6ParserVisitor
from antlr4.error.ErrorListener import ErrorListener

class SilentErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        # Do nothing - suppresses console output
        pass

class VB6AntlrVisitor(VisualBasic6ParserVisitor):
    def __init__(self):
        self.methods = []
        self.variables = []
        self.calls = []
        self.current_method = None

    def visitSubStmt(self, ctx: VisualBasic6Parser.SubStmtContext):
        name = ctx.ambiguousIdentifier().getText()
        method_info = {
            "name": name,
            "type": "Sub",
            "start": ctx.start.line,
            "end": ctx.stop.line,
            "content": ctx.getText(),
            "calls": []
        }
        self.methods.append(method_info)
        
        old_method = self.current_method
        self.current_method = method_info
        res = self.visitChildren(ctx)
        self.current_method = old_method
        return res

    def visitFunctionStmt(self, ctx: VisualBasic6Parser.FunctionStmtContext):
        name = ctx.ambiguousIdentifier().getText()
        method_info = {
            "name": name,
            "type": "Function",
            "start": ctx.start.line,
            "end": ctx.stop.line,
            "content": ctx.getText(),
            "calls": []
        }
        self.methods.append(method_info)
        
        old_method = self.current_method
        self.current_method = method_info
        res = self.visitChildren(ctx)
        self.current_method = old_method
        return res

    def visitPropertyGetStmt(self, ctx: VisualBasic6Parser.PropertyGetStmtContext):
        name = ctx.ambiguousIdentifier().getText()
        method_info = {
            "name": name,
            "type": "Property Get",
            "start": ctx.start.line,
            "end": ctx.stop.line,
            "content": ctx.getText(),
            "calls": []
        }
        self.methods.append(method_info)
        
        old_method = self.current_method
        self.current_method = method_info
        res = self.visitChildren(ctx)
        self.current_method = old_method
        return res

    def visitPropertyLetStmt(self, ctx: VisualBasic6Parser.PropertyLetStmtContext):
        name = ctx.ambiguousIdentifier().getText()
        method_info = {
            "name": name,
            "type": "Property Let",
            "start": ctx.start.line,
            "end": ctx.stop.line,
            "content": ctx.getText(),
            "calls": []
        }
        self.methods.append(method_info)
        
        old_method = self.current_method
        self.current_method = method_info
        res = self.visitChildren(ctx)
        self.current_method = old_method
        return res

    def visitPropertySetStmt(self, ctx: VisualBasic6Parser.PropertySetStmtContext):
        name = ctx.ambiguousIdentifier().getText()
        method_info = {
            "name": name,
            "type": "Property Set",
            "start": ctx.start.line,
            "end": ctx.stop.line,
            "content": ctx.getText(),
            "calls": []
        }
        self.methods.append(method_info)
        
        old_method = self.current_method
        self.current_method = method_info
        res = self.visitChildren(ctx)
        self.current_method = old_method
        return res

    def visitVariableSubStmt(self, ctx: VisualBasic6Parser.VariableSubStmtContext):
        name = ctx.ambiguousIdentifier().getText()
        if self.current_method is None:
            # Module level variable
            self.variables.append({"name": name, "type": "Variable", "scope": "Module"})
        return self.visitChildren(ctx)

    def _add_call(self, name):
        if self.current_method:
            self.current_method["calls"].append(name)
        else:
            self.calls.append(name)

    def visitExplicitCallStmt(self, ctx: VisualBasic6Parser.ExplicitCallStmtContext):
        self._add_call(ctx.getText().replace("Call ", "").split("(")[0].strip())
        return self.visitChildren(ctx)

    def visitICS_B_ProcedureCall(self, ctx: VisualBasic6Parser.ICS_B_ProcedureCallContext):
        self._add_call(ctx.certainIdentifier().getText())
        return self.visitChildren(ctx)

    def visitICS_S_ProcedureOrArrayCall(self, ctx: VisualBasic6Parser.ICS_S_ProcedureOrArrayCallContext):
        self._add_call(ctx.ambiguousIdentifier().getText())
        return self.visitChildren(ctx)

    def visitICS_S_VariableOrProcedureCall(self, ctx: VisualBasic6Parser.ICS_S_VariableOrProcedureCallContext):
        self._add_call(ctx.ambiguousIdentifier().getText())
        return self.visitChildren(ctx)

    def visitICS_S_MemberCall(self, ctx: VisualBasic6Parser.ICS_S_MemberCallContext):
        self._add_call(ctx.getText().split("(")[0].strip())
        return self.visitChildren(ctx)

from antlr4.atn.PredictionMode import PredictionMode

class AntlrParserWrapper:
    def parse_file(self, file_path):
        input_stream = FileStream(file_path, encoding='latin-1')
        lexer = VisualBasic6Lexer(input_stream)
        lexer.removeErrorListeners()
        lexer.addErrorListener(SilentErrorListener())
        
        stream = CommonTokenStream(lexer)
        parser = VisualBasic6Parser(stream)
        parser.removeErrorListeners()
        parser.addErrorListener(SilentErrorListener())
        
        # Priority 1: LL mode for maximum precision
        parser._interp.predictionMode = PredictionMode.LL
        try:
            tree = parser.startRule()
        except Exception:
            # Priority 2: Fallback to SLL if LL fails immediately
            stream.reset()
            parser.reset()
            parser._interp.predictionMode = PredictionMode.SLL
            try:
                tree = parser.startRule()
            except Exception:
                # If both fail, we return empty so Parser.py can trigger Regex fallback
                return {"methods": [], "variables": [], "calls": []}
        
        visitor = VB6AntlrVisitor()
        visitor.visit(tree)
        
        return {
            "methods": visitor.methods,
            "variables": visitor.variables,
            "calls": visitor.calls
        }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        wrapper = AntlrParserWrapper()
        result = wrapper.parse_file(sys.argv[1])
        print(result)
