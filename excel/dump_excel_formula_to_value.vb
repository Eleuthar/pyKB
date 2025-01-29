
'Open the workbook, press Alt + F11 to open the VBA editor.
'Insert > Module, Run the macro (Alt + F8 > Select ConvertToValuesAllSheets > Run).


Sub ConvertToValuesAllSheets()
    Dim ws As Worksheet
    
    ' Loop through each worksheet in the active workbook
    For Each ws In ThisWorkbook.Worksheets
        ws.Cells.Copy
        ws.Cells.PasteSpecial Paste:=xlPasteValues
    Next ws
    
    ' Save the workbook
    ThisWorkbook.SaveAs Filename:="C:\Users\bujorean\Registru Parohia DOMUS 2024-fara_formule.xlsm", FileFormat:=xlOpenXMLWorkbookMacroEnabled
End Sub


