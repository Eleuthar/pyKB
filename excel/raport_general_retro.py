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
rep_ndx = {
    'IAN': 8,
    'FEB': 14,
    'MAR': 20,
    'APR': 26,
    'MAI': 32,
    'IUN': 38,
    'IUL': 44,
    'AUG': 50,
    'SEP': 56,
    'OCT': 62,
    'NOV': 68,
    'DEC': 74
}
xxpath='REG.xlsx'
wb = load_workbook(xxpath)
report = wb.worksheets[1]

for month in rep_ndx:
    for wk in wb.worksheets[2:]:
        if month in wk.title:
            row = rep_ndx[month]
            for j in prod:
                chr = prod[j]['chr']
                quant_in = wk[f'B{j+9}'].value
                quant_in = quant_in if quant_in is not None else 0
                amount_in = quant_in * wk[f'E{j+9}'].value
                
                quant_out = wk[f'G{j+9}'].value
                quant_out = quant_out if quant_out is not None else 0
                amount_out = quant_out * wk[f'E{j+9}'].value
                
                quant_stock = wk[f'I{j+9}'].value
                quant_stock = quant_stock if quant_stock is not None else 0
                
                amount_stock = wk[f'J{j+9}'].value
                amount_stock = amount_stock if amount_stock is not None else 0
                
                rep_mapping = {
                    'quant_in': [report[f'{chr}{row}'], quant_in],
                    'amount_in': [report[f'{chr}{row+1}'], amount_in],
                    'quant_out': [report[f'{chr}{row+2}'], quant_out],
                    'amount_out': [report[f'{chr}{row+3}'], amount_out],
                    'quant_stock': [report[f'{chr}{row+4}'], quant_stock],
                    'amount_stock': [report[f'{chr}{row+5}'], amount_stock],
                    'general_quant_in': [report[f'{chr}80'], quant_in],
                    'general_amount_in': [report[f'{chr}81'], amount_in],
                    'general_quant_out': [report[f'{chr}82'], quant_out],
                    'general_amount_out': [report[f'{chr}83'], amount_out]
                }
                for x in range(6):
                    rep = report[f'{chr}{row+x}']
                    if rep.value is None:
                        rep.value = 0
                for x in range(80, 84):
                    rep = report[f'{chr}{x}']
                    if rep.value is None:
                        rep.value = 0     
                for q, v in rep_mapping.items():
                    v[0].value += v[1]
wb.save(xxpath)