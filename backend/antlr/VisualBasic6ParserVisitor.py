# Generated from VisualBasic6Parser.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .VisualBasic6Parser import VisualBasic6Parser
else:
    from VisualBasic6Parser import VisualBasic6Parser

# This class defines a complete generic visitor for a parse tree produced by VisualBasic6Parser.

class VisualBasic6ParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by VisualBasic6Parser#startRule.
    def visitStartRule(self, ctx:VisualBasic6Parser.StartRuleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#module.
    def visitModule(self, ctx:VisualBasic6Parser.ModuleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#moduleReferences.
    def visitModuleReferences(self, ctx:VisualBasic6Parser.ModuleReferencesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#moduleReference.
    def visitModuleReference(self, ctx:VisualBasic6Parser.ModuleReferenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#moduleReferenceValue.
    def visitModuleReferenceValue(self, ctx:VisualBasic6Parser.ModuleReferenceValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#moduleReferenceComponent.
    def visitModuleReferenceComponent(self, ctx:VisualBasic6Parser.ModuleReferenceComponentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#moduleHeader.
    def visitModuleHeader(self, ctx:VisualBasic6Parser.ModuleHeaderContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#moduleConfig.
    def visitModuleConfig(self, ctx:VisualBasic6Parser.ModuleConfigContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#moduleConfigElement.
    def visitModuleConfigElement(self, ctx:VisualBasic6Parser.ModuleConfigElementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#moduleAttributes.
    def visitModuleAttributes(self, ctx:VisualBasic6Parser.ModuleAttributesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#moduleOptions.
    def visitModuleOptions(self, ctx:VisualBasic6Parser.ModuleOptionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#optionBaseStmt.
    def visitOptionBaseStmt(self, ctx:VisualBasic6Parser.OptionBaseStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#optionCompareStmt.
    def visitOptionCompareStmt(self, ctx:VisualBasic6Parser.OptionCompareStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#optionExplicitStmt.
    def visitOptionExplicitStmt(self, ctx:VisualBasic6Parser.OptionExplicitStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#optionPrivateModuleStmt.
    def visitOptionPrivateModuleStmt(self, ctx:VisualBasic6Parser.OptionPrivateModuleStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#moduleBody.
    def visitModuleBody(self, ctx:VisualBasic6Parser.ModuleBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#moduleBodyElement.
    def visitModuleBodyElement(self, ctx:VisualBasic6Parser.ModuleBodyElementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#controlProperties.
    def visitControlProperties(self, ctx:VisualBasic6Parser.ControlPropertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#cp_Properties.
    def visitCp_Properties(self, ctx:VisualBasic6Parser.Cp_PropertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#cp_SingleProperty.
    def visitCp_SingleProperty(self, ctx:VisualBasic6Parser.Cp_SinglePropertyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#cp_PropertyName.
    def visitCp_PropertyName(self, ctx:VisualBasic6Parser.Cp_PropertyNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#cp_PropertyValue.
    def visitCp_PropertyValue(self, ctx:VisualBasic6Parser.Cp_PropertyValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#cp_NestedProperty.
    def visitCp_NestedProperty(self, ctx:VisualBasic6Parser.Cp_NestedPropertyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#cp_ControlType.
    def visitCp_ControlType(self, ctx:VisualBasic6Parser.Cp_ControlTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#cp_ControlIdentifier.
    def visitCp_ControlIdentifier(self, ctx:VisualBasic6Parser.Cp_ControlIdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#moduleBlock.
    def visitModuleBlock(self, ctx:VisualBasic6Parser.ModuleBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#attributeStmt.
    def visitAttributeStmt(self, ctx:VisualBasic6Parser.AttributeStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#block.
    def visitBlock(self, ctx:VisualBasic6Parser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#blockStmt.
    def visitBlockStmt(self, ctx:VisualBasic6Parser.BlockStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#appActivateStmt.
    def visitAppActivateStmt(self, ctx:VisualBasic6Parser.AppActivateStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#beepStmt.
    def visitBeepStmt(self, ctx:VisualBasic6Parser.BeepStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#chDirStmt.
    def visitChDirStmt(self, ctx:VisualBasic6Parser.ChDirStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#chDriveStmt.
    def visitChDriveStmt(self, ctx:VisualBasic6Parser.ChDriveStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#closeStmt.
    def visitCloseStmt(self, ctx:VisualBasic6Parser.CloseStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#constStmt.
    def visitConstStmt(self, ctx:VisualBasic6Parser.ConstStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#constSubStmt.
    def visitConstSubStmt(self, ctx:VisualBasic6Parser.ConstSubStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#dateStmt.
    def visitDateStmt(self, ctx:VisualBasic6Parser.DateStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#declareStmt.
    def visitDeclareStmt(self, ctx:VisualBasic6Parser.DeclareStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#deftypeStmt.
    def visitDeftypeStmt(self, ctx:VisualBasic6Parser.DeftypeStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#deleteSettingStmt.
    def visitDeleteSettingStmt(self, ctx:VisualBasic6Parser.DeleteSettingStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#doLoopStmt.
    def visitDoLoopStmt(self, ctx:VisualBasic6Parser.DoLoopStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#endStmt.
    def visitEndStmt(self, ctx:VisualBasic6Parser.EndStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#enumerationStmt.
    def visitEnumerationStmt(self, ctx:VisualBasic6Parser.EnumerationStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#enumerationStmt_Constant.
    def visitEnumerationStmt_Constant(self, ctx:VisualBasic6Parser.EnumerationStmt_ConstantContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#eraseStmt.
    def visitEraseStmt(self, ctx:VisualBasic6Parser.EraseStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#errorStmt.
    def visitErrorStmt(self, ctx:VisualBasic6Parser.ErrorStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#eventStmt.
    def visitEventStmt(self, ctx:VisualBasic6Parser.EventStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#exitStmt.
    def visitExitStmt(self, ctx:VisualBasic6Parser.ExitStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#filecopyStmt.
    def visitFilecopyStmt(self, ctx:VisualBasic6Parser.FilecopyStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#forEachStmt.
    def visitForEachStmt(self, ctx:VisualBasic6Parser.ForEachStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#forNextStmt.
    def visitForNextStmt(self, ctx:VisualBasic6Parser.ForNextStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#functionStmt.
    def visitFunctionStmt(self, ctx:VisualBasic6Parser.FunctionStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#getStmt.
    def visitGetStmt(self, ctx:VisualBasic6Parser.GetStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#goSubStmt.
    def visitGoSubStmt(self, ctx:VisualBasic6Parser.GoSubStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#goToStmt.
    def visitGoToStmt(self, ctx:VisualBasic6Parser.GoToStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#inlineIfThenElse.
    def visitInlineIfThenElse(self, ctx:VisualBasic6Parser.InlineIfThenElseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#blockIfThenElse.
    def visitBlockIfThenElse(self, ctx:VisualBasic6Parser.BlockIfThenElseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#ifBlockStmt.
    def visitIfBlockStmt(self, ctx:VisualBasic6Parser.IfBlockStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#ifConditionStmt.
    def visitIfConditionStmt(self, ctx:VisualBasic6Parser.IfConditionStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#ifElseIfBlockStmt.
    def visitIfElseIfBlockStmt(self, ctx:VisualBasic6Parser.IfElseIfBlockStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#ifElseBlockStmt.
    def visitIfElseBlockStmt(self, ctx:VisualBasic6Parser.IfElseBlockStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#implementsStmt.
    def visitImplementsStmt(self, ctx:VisualBasic6Parser.ImplementsStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#inputStmt.
    def visitInputStmt(self, ctx:VisualBasic6Parser.InputStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#killStmt.
    def visitKillStmt(self, ctx:VisualBasic6Parser.KillStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#letStmt.
    def visitLetStmt(self, ctx:VisualBasic6Parser.LetStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#lineInputStmt.
    def visitLineInputStmt(self, ctx:VisualBasic6Parser.LineInputStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#loadStmt.
    def visitLoadStmt(self, ctx:VisualBasic6Parser.LoadStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#lockStmt.
    def visitLockStmt(self, ctx:VisualBasic6Parser.LockStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#lsetStmt.
    def visitLsetStmt(self, ctx:VisualBasic6Parser.LsetStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#macroIfThenElseStmt.
    def visitMacroIfThenElseStmt(self, ctx:VisualBasic6Parser.MacroIfThenElseStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#macroIfBlockStmt.
    def visitMacroIfBlockStmt(self, ctx:VisualBasic6Parser.MacroIfBlockStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#macroElseIfBlockStmt.
    def visitMacroElseIfBlockStmt(self, ctx:VisualBasic6Parser.MacroElseIfBlockStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#macroElseBlockStmt.
    def visitMacroElseBlockStmt(self, ctx:VisualBasic6Parser.MacroElseBlockStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#midStmt.
    def visitMidStmt(self, ctx:VisualBasic6Parser.MidStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#mkdirStmt.
    def visitMkdirStmt(self, ctx:VisualBasic6Parser.MkdirStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#nameStmt.
    def visitNameStmt(self, ctx:VisualBasic6Parser.NameStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#onErrorStmt.
    def visitOnErrorStmt(self, ctx:VisualBasic6Parser.OnErrorStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#onGoToStmt.
    def visitOnGoToStmt(self, ctx:VisualBasic6Parser.OnGoToStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#onGoSubStmt.
    def visitOnGoSubStmt(self, ctx:VisualBasic6Parser.OnGoSubStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#openStmt.
    def visitOpenStmt(self, ctx:VisualBasic6Parser.OpenStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#outputList.
    def visitOutputList(self, ctx:VisualBasic6Parser.OutputListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#outputList_Expression.
    def visitOutputList_Expression(self, ctx:VisualBasic6Parser.OutputList_ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#printStmt.
    def visitPrintStmt(self, ctx:VisualBasic6Parser.PrintStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#propertyGetStmt.
    def visitPropertyGetStmt(self, ctx:VisualBasic6Parser.PropertyGetStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#propertySetStmt.
    def visitPropertySetStmt(self, ctx:VisualBasic6Parser.PropertySetStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#propertyLetStmt.
    def visitPropertyLetStmt(self, ctx:VisualBasic6Parser.PropertyLetStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#putStmt.
    def visitPutStmt(self, ctx:VisualBasic6Parser.PutStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#raiseEventStmt.
    def visitRaiseEventStmt(self, ctx:VisualBasic6Parser.RaiseEventStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#randomizeStmt.
    def visitRandomizeStmt(self, ctx:VisualBasic6Parser.RandomizeStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#redimStmt.
    def visitRedimStmt(self, ctx:VisualBasic6Parser.RedimStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#redimSubStmt.
    def visitRedimSubStmt(self, ctx:VisualBasic6Parser.RedimSubStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#resetStmt.
    def visitResetStmt(self, ctx:VisualBasic6Parser.ResetStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#resumeStmt.
    def visitResumeStmt(self, ctx:VisualBasic6Parser.ResumeStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#returnStmt.
    def visitReturnStmt(self, ctx:VisualBasic6Parser.ReturnStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#rmdirStmt.
    def visitRmdirStmt(self, ctx:VisualBasic6Parser.RmdirStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#rsetStmt.
    def visitRsetStmt(self, ctx:VisualBasic6Parser.RsetStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#savepictureStmt.
    def visitSavepictureStmt(self, ctx:VisualBasic6Parser.SavepictureStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#saveSettingStmt.
    def visitSaveSettingStmt(self, ctx:VisualBasic6Parser.SaveSettingStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#seekStmt.
    def visitSeekStmt(self, ctx:VisualBasic6Parser.SeekStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#selectCaseStmt.
    def visitSelectCaseStmt(self, ctx:VisualBasic6Parser.SelectCaseStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#sC_Case.
    def visitSC_Case(self, ctx:VisualBasic6Parser.SC_CaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#caseCondElse.
    def visitCaseCondElse(self, ctx:VisualBasic6Parser.CaseCondElseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#caseCondExpr.
    def visitCaseCondExpr(self, ctx:VisualBasic6Parser.CaseCondExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#caseCondExprIs.
    def visitCaseCondExprIs(self, ctx:VisualBasic6Parser.CaseCondExprIsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#caseCondExprValue.
    def visitCaseCondExprValue(self, ctx:VisualBasic6Parser.CaseCondExprValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#caseCondExprTo.
    def visitCaseCondExprTo(self, ctx:VisualBasic6Parser.CaseCondExprToContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#sendkeysStmt.
    def visitSendkeysStmt(self, ctx:VisualBasic6Parser.SendkeysStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#setattrStmt.
    def visitSetattrStmt(self, ctx:VisualBasic6Parser.SetattrStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#setStmt.
    def visitSetStmt(self, ctx:VisualBasic6Parser.SetStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#stopStmt.
    def visitStopStmt(self, ctx:VisualBasic6Parser.StopStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#subStmt.
    def visitSubStmt(self, ctx:VisualBasic6Parser.SubStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#timeStmt.
    def visitTimeStmt(self, ctx:VisualBasic6Parser.TimeStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#typeStmt.
    def visitTypeStmt(self, ctx:VisualBasic6Parser.TypeStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#typeStmt_Element.
    def visitTypeStmt_Element(self, ctx:VisualBasic6Parser.TypeStmt_ElementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#typeOfStmt.
    def visitTypeOfStmt(self, ctx:VisualBasic6Parser.TypeOfStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#unloadStmt.
    def visitUnloadStmt(self, ctx:VisualBasic6Parser.UnloadStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#unlockStmt.
    def visitUnlockStmt(self, ctx:VisualBasic6Parser.UnlockStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#vsAssign.
    def visitVsAssign(self, ctx:VisualBasic6Parser.VsAssignContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#vsNot.
    def visitVsNot(self, ctx:VisualBasic6Parser.VsNotContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#vsStruct.
    def visitVsStruct(self, ctx:VisualBasic6Parser.VsStructContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#vsMultDiv.
    def visitVsMultDiv(self, ctx:VisualBasic6Parser.VsMultDivContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#vsTypeOf.
    def visitVsTypeOf(self, ctx:VisualBasic6Parser.VsTypeOfContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#vsICS.
    def visitVsICS(self, ctx:VisualBasic6Parser.VsICSContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#vsXor.
    def visitVsXor(self, ctx:VisualBasic6Parser.VsXorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#vsAddSub.
    def visitVsAddSub(self, ctx:VisualBasic6Parser.VsAddSubContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#vsAnd.
    def visitVsAnd(self, ctx:VisualBasic6Parser.VsAndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#vsPow.
    def visitVsPow(self, ctx:VisualBasic6Parser.VsPowContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#vsMod.
    def visitVsMod(self, ctx:VisualBasic6Parser.VsModContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#vsAmp.
    def visitVsAmp(self, ctx:VisualBasic6Parser.VsAmpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#vsAddressOf.
    def visitVsAddressOf(self, ctx:VisualBasic6Parser.VsAddressOfContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#vsNew.
    def visitVsNew(self, ctx:VisualBasic6Parser.VsNewContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#vsPlusMinus.
    def visitVsPlusMinus(self, ctx:VisualBasic6Parser.VsPlusMinusContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#vsIDiv.
    def visitVsIDiv(self, ctx:VisualBasic6Parser.VsIDivContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#vsOr.
    def visitVsOr(self, ctx:VisualBasic6Parser.VsOrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#vsLiteral.
    def visitVsLiteral(self, ctx:VisualBasic6Parser.VsLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#vsEqv.
    def visitVsEqv(self, ctx:VisualBasic6Parser.VsEqvContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#vsImp.
    def visitVsImp(self, ctx:VisualBasic6Parser.VsImpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#vsComp.
    def visitVsComp(self, ctx:VisualBasic6Parser.VsCompContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#vsMid.
    def visitVsMid(self, ctx:VisualBasic6Parser.VsMidContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#variableStmt.
    def visitVariableStmt(self, ctx:VisualBasic6Parser.VariableStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#variableListStmt.
    def visitVariableListStmt(self, ctx:VisualBasic6Parser.VariableListStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#variableSubStmt.
    def visitVariableSubStmt(self, ctx:VisualBasic6Parser.VariableSubStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#whileWendStmt.
    def visitWhileWendStmt(self, ctx:VisualBasic6Parser.WhileWendStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#widthStmt.
    def visitWidthStmt(self, ctx:VisualBasic6Parser.WidthStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#withStmt.
    def visitWithStmt(self, ctx:VisualBasic6Parser.WithStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#writeStmt.
    def visitWriteStmt(self, ctx:VisualBasic6Parser.WriteStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#explicitCallStmt.
    def visitExplicitCallStmt(self, ctx:VisualBasic6Parser.ExplicitCallStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#eCS_ProcedureCall.
    def visitECS_ProcedureCall(self, ctx:VisualBasic6Parser.ECS_ProcedureCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#eCS_MemberProcedureCall.
    def visitECS_MemberProcedureCall(self, ctx:VisualBasic6Parser.ECS_MemberProcedureCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#implicitCallStmt_InBlock.
    def visitImplicitCallStmt_InBlock(self, ctx:VisualBasic6Parser.ImplicitCallStmt_InBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#iCS_B_ProcedureCall.
    def visitICS_B_ProcedureCall(self, ctx:VisualBasic6Parser.ICS_B_ProcedureCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#iCS_B_MemberProcedureCall.
    def visitICS_B_MemberProcedureCall(self, ctx:VisualBasic6Parser.ICS_B_MemberProcedureCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#implicitCallStmt_InStmt.
    def visitImplicitCallStmt_InStmt(self, ctx:VisualBasic6Parser.ImplicitCallStmt_InStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#iCS_S_VariableOrProcedureCall.
    def visitICS_S_VariableOrProcedureCall(self, ctx:VisualBasic6Parser.ICS_S_VariableOrProcedureCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#iCS_S_ProcedureOrArrayCall.
    def visitICS_S_ProcedureOrArrayCall(self, ctx:VisualBasic6Parser.ICS_S_ProcedureOrArrayCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#iCS_S_NestedProcedureCall.
    def visitICS_S_NestedProcedureCall(self, ctx:VisualBasic6Parser.ICS_S_NestedProcedureCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#iCS_S_MembersCall.
    def visitICS_S_MembersCall(self, ctx:VisualBasic6Parser.ICS_S_MembersCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#iCS_S_MemberCall.
    def visitICS_S_MemberCall(self, ctx:VisualBasic6Parser.ICS_S_MemberCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#iCS_S_DictionaryCall.
    def visitICS_S_DictionaryCall(self, ctx:VisualBasic6Parser.ICS_S_DictionaryCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#argsCall.
    def visitArgsCall(self, ctx:VisualBasic6Parser.ArgsCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#argCall.
    def visitArgCall(self, ctx:VisualBasic6Parser.ArgCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#dictionaryCallStmt.
    def visitDictionaryCallStmt(self, ctx:VisualBasic6Parser.DictionaryCallStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#argList.
    def visitArgList(self, ctx:VisualBasic6Parser.ArgListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#arg.
    def visitArg(self, ctx:VisualBasic6Parser.ArgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#argDefaultValue.
    def visitArgDefaultValue(self, ctx:VisualBasic6Parser.ArgDefaultValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#subscripts.
    def visitSubscripts(self, ctx:VisualBasic6Parser.SubscriptsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#subscript_.
    def visitSubscript_(self, ctx:VisualBasic6Parser.Subscript_Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#ambiguousIdentifier.
    def visitAmbiguousIdentifier(self, ctx:VisualBasic6Parser.AmbiguousIdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#asTypeClause.
    def visitAsTypeClause(self, ctx:VisualBasic6Parser.AsTypeClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#baseType.
    def visitBaseType(self, ctx:VisualBasic6Parser.BaseTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#certainIdentifier.
    def visitCertainIdentifier(self, ctx:VisualBasic6Parser.CertainIdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#comparisonOperator.
    def visitComparisonOperator(self, ctx:VisualBasic6Parser.ComparisonOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#complexType.
    def visitComplexType(self, ctx:VisualBasic6Parser.ComplexTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#fieldLength.
    def visitFieldLength(self, ctx:VisualBasic6Parser.FieldLengthContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#letterrange.
    def visitLetterrange(self, ctx:VisualBasic6Parser.LetterrangeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#lineLabel.
    def visitLineLabel(self, ctx:VisualBasic6Parser.LineLabelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#literal.
    def visitLiteral(self, ctx:VisualBasic6Parser.LiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#publicPrivateVisibility.
    def visitPublicPrivateVisibility(self, ctx:VisualBasic6Parser.PublicPrivateVisibilityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#publicPrivateGlobalVisibility.
    def visitPublicPrivateGlobalVisibility(self, ctx:VisualBasic6Parser.PublicPrivateGlobalVisibilityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#type_.
    def visitType_(self, ctx:VisualBasic6Parser.Type_Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#typeHint.
    def visitTypeHint(self, ctx:VisualBasic6Parser.TypeHintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#visibility.
    def visitVisibility(self, ctx:VisualBasic6Parser.VisibilityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#ambiguousKeyword.
    def visitAmbiguousKeyword(self, ctx:VisualBasic6Parser.AmbiguousKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#integerLiteral.
    def visitIntegerLiteral(self, ctx:VisualBasic6Parser.IntegerLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#octalLiteral.
    def visitOctalLiteral(self, ctx:VisualBasic6Parser.OctalLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualBasic6Parser#doubleLiteral.
    def visitDoubleLiteral(self, ctx:VisualBasic6Parser.DoubleLiteralContext):
        return self.visitChildren(ctx)



del VisualBasic6Parser