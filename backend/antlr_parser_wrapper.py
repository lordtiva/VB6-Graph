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

    def _create_method_info(self, name, method_type, ctx):
        return {
            "name": name,
            "type": method_type,
            "start": ctx.start.line,
            "end": ctx.stop.line,
            "content": ctx.getText(),
            "calls": [],
            "locals": [],
            "parameters": []
        }

    def _visit_method(self, ctx, method_type):
        name = ctx.ambiguousIdentifier().getText()
        method_info = self._create_method_info(name, method_type, ctx)
        self.methods.append(method_info)
        
        old_method = self.current_method
        self.current_method = method_info
        
        # Track parameters if available
        if hasattr(ctx, 'argList') and ctx.argList():
            for arg in ctx.argList().arg():
                arg_name = arg.ambiguousIdentifier().getText()
                self.current_method["parameters"].append(arg_name)
        
        res = self.visitChildren(ctx)
        self.current_method = old_method
        return res

    def visitSubStmt(self, ctx: VisualBasic6Parser.SubStmtContext):
        return self._visit_method(ctx, "Sub")

    def visitFunctionStmt(self, ctx: VisualBasic6Parser.FunctionStmtContext):
        return self._visit_method(ctx, "Function")

    def visitPropertyGetStmt(self, ctx: VisualBasic6Parser.PropertyGetStmtContext):
        return self._visit_method(ctx, "Property Get")

    def visitPropertyLetStmt(self, ctx: VisualBasic6Parser.PropertyLetStmtContext):
        return self._visit_method(ctx, "Property Let")

    def visitPropertySetStmt(self, ctx: VisualBasic6Parser.PropertySetStmtContext):
        return self._visit_method(ctx, "Property Set")

    def visitVariableSubStmt(self, ctx: VisualBasic6Parser.VariableSubStmtContext):
        name = ctx.ambiguousIdentifier().getText()
        if self.current_method is None:
            # Module level variable
            self.variables.append({"name": name, "type": "Variable", "scope": "Module"})
        else:
            # Local variable
            self.current_method["locals"].append(name)
        return self.visitChildren(ctx)

    def _add_reference(self, name):
        if not name: return
        # Logic to avoid adding keywords or very short/invalid names if necessary
        if self.current_method:
            if name not in self.current_method["calls"]:
                self.current_method["calls"].append(name)
        else:
            if name not in self.calls:
                self.calls.append(name)

    def visitExplicitCallStmt(self, ctx: VisualBasic6Parser.ExplicitCallStmtContext):
        # Call Something(...)
        text = ctx.getText().replace("Call ", "").split("(")[0].strip()
        self._add_reference(text)
        return self.visitChildren(ctx)

    def visitICS_B_ProcedureCall(self, ctx: VisualBasic6Parser.ICS_B_ProcedureCallContext):
        self._add_reference(ctx.certainIdentifier().getText())
        return self.visitChildren(ctx)

    def visitICS_S_ProcedureOrArrayCall(self, ctx: VisualBasic6Parser.ICS_S_ProcedureOrArrayCallContext):
        self._add_reference(ctx.ambiguousIdentifier().getText())
        return self.visitChildren(ctx)

    def visitICS_S_VariableOrProcedureCall(self, ctx: VisualBasic6Parser.ICS_S_VariableOrProcedureCallContext):
        self._add_reference(ctx.ambiguousIdentifier().getText())
        return self.visitChildren(ctx)

    def visitICS_S_MemberCall(self, ctx: VisualBasic6Parser.ICS_S_MemberCallContext):
        # Obj.Member
        self._add_reference(ctx.getText().split("(")[0].strip())
        return self.visitChildren(ctx)

from antlr4.atn.PredictionMode import PredictionMode

class AntlrParserWrapper:
    def parse_file(self, file_path):
        input_stream = FileStream(file_path, encoding='latin-1')
        return self._parse_stream(input_stream)

    def parse_content(self, content):
        from antlr4 import InputStream
        input_stream = InputStream(content)
        return self._parse_stream(input_stream)

    def _parse_stream(self, input_stream):
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
                # If both fail, we return empty
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
