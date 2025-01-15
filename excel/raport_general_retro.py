from openpyxl import load_workbook

prod = {
    1: {'prod':'Lumanari 100B', '$': 0, 'chr': 'D'},
    2: {'prod':'Lumanari C20', '$': 0, 'chr': 'E'},
    3: {'prod':'Candele tip 0', '$': 0, 'chr': 'F'},
    4: {'prod':'Candele tip 1', '$': 0, 'chr': 'G'},
    5: {'prod':'Candele tip 2', '$': 0, 'chr': 'H'},
    6: {'prod':'Candele tip 3', '$': 0, 'chr': 'I'},
    7: {'prod':'Candele tip 4', '$': 0, 'chr': 'J'}
}
rep_ndx = {'IAN': 9, 'FEB': 15, 'MAR': 21, 'APR': 27, 'MAI': 33, 'IUN': 39, 'IUL': 45, 'AUG': 51, 'SEP': 57, 'OCT': 63, 'NOV': 69, 'DEC': 75}
xxpath='REG.xlsx'
wb = load_workbook(xxpath)
report = wb.worksheets[1]

wb_ndx = 0
for ndx in enumerate(rep_ndx):
    while wb_ndx < len(wb.worksheets)-2:
        wk = wb.worksheets[2+wb_ndx]
        month = wk.title.split()[1]
        if month != ndx[1]:
            break
        else:
            wb_ndx+=1
            row = rep_ndx[month]
            for j in prod:
                chr = prod[j]['chr']
                # IN
                amount_in = 0
                quant_in = wk[f'B{j+9}'].value
                if quant_in is None:
                    quant_in = 0
                else:
                    amount_in = quant_in * wk[f'E{j+9}'].value
                # OUT
                quant_out = wk[f'G{j+9}'].value
                amount_out = wk[f'H{j+9}'].value
                if quant_out is None:
                    quant_out = 0
                if amount_out is None:
                    amount_out = 0        
                # STOCK
                quant_stock = wk[f'I{j+9}'].value
                amount_stock = wk[f'J{j+9}'].value
                if quant_stock is None:
                    quant_stock = 0
                if amount_stock is None:
                    amount_stock = 0    
                rep_mapping = {
                    'quant_in': [report[f'{chr}{row}'], quant_in],
                    'amount_in': [report[f'{chr}{row+1}'], amount_in],
                    'quant_out': [report[f'{chr}{row+2}'], quant_out],
                    'amount_out': [report[f'{chr}{row+3}'], amount_out],
                    'quant_stock': [report[f'{chr}{row+4}'], quant_stock],
                    'amount_stock': [report[f'{chr}{row+5}'], amount_stock],
                    'general_quant_in': [report[f'{chr}81'], quant_in],
                    'general_amount_in': [report[f'{chr}82'], amount_in],
                    'general_quant_out': [report[f'{chr}83'], quant_out],
                    'general_amount_out': [report[f'{chr}84'], amount_out]
                }
                for x in ['quant_in','amount_in','quant_out','amount_out','quant_stock','amount_stock']:
                    rep_mapping[x][0].value = rep_mapping[x][1]
                for x in ['general_quant_in', 'general_amount_in', 'general_quant_out', 'general_amount_out']:
                    rep_mapping[x][0].value += rep_mapping[x][1]


wb.save(xxpath)
