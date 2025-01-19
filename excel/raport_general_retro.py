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
month_ndx = [
    ['IAN', 9], 
    ['FEB', 15], 
    ['MAR', 21], 
    ['APR', 27],
    ['MAI', 33], 
    ['IUN', 39], 
    ['IUL', 45], 
    ['AUG', 51], 
    ['SEP', 57], 
    ['OCT', 63], 
    ['NOV', 69],
    ['DEC', 75]
]
xxpath='REG.xlsx'


def extract_sheet(wk, j):
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
    return [
        quant_in,
        amount_in,
        quant_out,
        amount_out,
        quant_stock,
        amount_stock
    ]


def retro_calculate(wb_ndx):
    try:
        for rep_month in month_ndx:
            wk = wb.worksheets[wb_ndx]
            month = wk.title.split()[1]
            row = rep_month[1]
            while rep_month[0] == month:
                for j in prod:
                    chr = prod[j]['chr']
                    [quant_in, amount_in, quant_out, amount_out, quant_stock, amount_stock] = extract_sheet(wk, j)
                    report[f'{chr}{row}'].value += quant_in
                    report[f'{chr}{row+1}'].value += amount_in
                    report[f'{chr}{row+2}'].value += quant_out
                    report[f'{chr}{row+3}'].value += amount_out
                    # overwrite stock with last known value
                    report[f'{chr}{row+4}'].value = quant_stock
                    report[f'{chr}{row+5}'].value = amount_stock
                    report[f'{chr}81'].value += quant_in
                    report[f'{chr}82'].value += amount_in
                    report[f'{chr}83'].value += quant_out
                    report[f'{chr}84'].value += amount_out
                wb_ndx += 1
                wk = wb.worksheets[wb_ndx]
                month = wk.title.split()[1]
    except:
        pass

# from pdb import set_trace
wb = load_workbook(xxpath)
report = wb.worksheets[0]
wb_ndx = 1
retro_calculate(wb_ndx)
wb.save(xxpath)
wb.close()