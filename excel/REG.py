from openpyxl import load_workbook
from collections import namedtuple
from openpyxl import Workbook
from openpyxl.styles import Alignment
from pdb import set_trace


# Helper function to merge and align cells
def merge_and_write(sheet, start_row, end_row, start_col, end_col, value):
    sheet.merge_cells(start_row=start_row, start_column=start_col, end_row=end_row, end_column=end_col)
    cell = sheet.cell(row=start_row, column=start_col, value=value)
    cell.alignment = Alignment(horizontal="center", vertical="center")

def gen_week_sheet():
    workbook = Workbook()
    z = workbook.create_sheet(title=f"Foaie {len(workbook.sheetnames)+1}")
    merge_and_write(z, 1, 1, 1, 4, 'PAROHIA DOMUS - VOLUNTARI')
    merge_and_write(z, 2, 2, 1, 4, 'REGISTRU LUMANARI \ COLPORTAJ PANGAR')

    # Add headers
    merge_and_write(z, 5, 8, 1, 1, "TIP PRODUS")
    merge_and_write(z, 5, 5, 2, 6, "INTRARI")
    merge_and_write(z, 5, 5, 7, 8, "IESIRI")
    merge_and_write(z, 5, 5, 9, 10, "STOCURI")

    # INTRARI subheader
    merge_and_write(z, 6, 7, 2, 3, "Cantitate")
    merge_and_write(z, 7, 8, 2, 2, "Adaugat")
    merge_and_write(z, 7, 8, 3, 3, "Anterior")

    merge_and_write(z, 6, 8, 4, 4, "U.M.")

    merge_and_write(z, 6, 6, 5, 5, "Pret unitar")
    merge_and_write(z, 7, 7, 5, 5, "")
    merge_and_write(z, 8, 8, 5, 5, "~ LEI ~")

    merge_and_write(z, 6, 6, 6, 6, "Valoare totala")
    merge_and_write(z, 7, 7, 6, 6, "(col. 1 x (col. 2 + 3))")
    merge_and_write(z, 8, 8, 6, 6, "~ LEI ~")

    # IESIRI subheader
    merge_and_write(z, 6, 8, 7, 7, "Cantitate")
    merge_and_write(z, 6, 6, 8, 8, "Valoare totala")
    merge_and_write(z, 7, 7, 8, 8, "(col. 3 x col. 5)")
    merge_and_write(z, 8, 8, 8, 8, "~ LEI ~")

    # STOCURI subheader
    merge_and_write(z, 6, 6, 9, 9, "Cantitate")
    merge_and_write(z, 7, 7, 9, 9, "(col. 1 - col. 5)")
    merge_and_write(z, 8, 8, 9, 9, "")
    merge_and_write(z, 6, 6, 10, 10, "Valoare")
    merge_and_write(z, 7, 7, 10, 10, "(col. 3 x col. 7)")
    merge_and_write(z, 8, 8, 10, 10, "~ LEI ~")
    # product index
    ndx=0
    for x in range(ord('A'), ord('K')):
        z[f'{chr(x)}9'] = ndx
        ndx+=1
    # item
    z['A10'] = 'Lumanari 100B'
    z['A11'] = 'Lumanari C20'
    z['A12'] = 'Candele tip 0'
    z['A13'] = 'Candele tip 1'
    z['A14'] = 'Candele tip 2'
    z['A15'] = 'Candele tip 3'
    z['A16'] = 'Candele tip 4'
    z['A17'] = 'COLPORTAJ'
    z['A18'] = 'TOTAL'

def insert_frame(workbook, day, month, enter_dm):
    for x in range(1, len(workbook.sheetnames)):
        prev_fm = workbook.sheetnames[x]
        if month in prev_fm:
            fm_day = int(prev_fm.split()[0])
            next_frame_day = int(workbook.sheetnames[x+1].split()[0])
            if fm_day < day < next_frame_day:
                frame = workbook.copy_worksheet(prev_fm)
                workbook._sheets.pop()
                workbook._sheets.insert(x+1, frame)
                frame.title = enter_dm
                return x, frame

# todo generate for the entire year a sheet for each week's Monday date
def gen_sheet_names(workbook, no):
    ...

def put_formula_week(workbook, ndx):
    # sheet[1] col C exception: 
    # weekly sheet formulas
    df = workbook.worksheets[ndx]
    prev = workbook.sheetnames[ndx-1]
    for prod_row in range(10,17):
        B = f'B{prod_row}'
        C = f'C{prod_row}'
        E = f'E{prod_row}'
        G = f'G{prod_row}'
        I = f'I{prod_row}'
        F = f'F{prod_row}'
        H = f'H{prod_row}'
        I = f'I{prod_row}'
        J = f'J{prod_row}'
        # previous stock
        df[C].value = f"=='{prev}'!I{prod_row}"
        # unit price
        df[E].value = f"='{prev}'!E{prod_row}"
        # quantity and amount
        df[F].value = f"={E} *({B} + {C})"
        df[H].value = f"={G} * {E}"
        df[I].value = f"=({B} + {C}) - {G}"
        df[J].value = f"={I} * {E}"
    # weekly totals used by general report
    for z in ['F','H','J']:
        df[f'{z}17'].value = f'=SUM({z}10:{z}16)'
    # initial stock
    # set first week sheet C10-C16 as D8-J8
    rep_title = workbook.sheetnames[0]
    rep_ord = ord('C')
    df = workbook.worksheets[1]
    for prod_row in range(10,17):
        C = f'C{prod_row}'
        rep_ord += 1
        rep_chr = chr(rep_ord+1)
        df[C].value = f"=='{rep_title}'!{rep_chr}{8}"

def find_negative(workbook):
    for fm in workbook.worksheets[1:]:
        for prod in ['B','C','F','G','H','I','J']:
            for row in range(10,17):
                try:
                    tgt = fm[f'{prod}{row}']
                    if tgt.value < 0:
                        print(fm.title, prod, row, tgt.value)
                except:
                    try:
                        if tgt.value < 0:
                            print(fm.title, prod, row, tgt.value)
                    except:
                        set_trace()
# F2
def rename_title(workbook, date_cell):
    for frame in workbook.worksheets[1:]:
        dt = frame[date_cell]
        head = dt.value.split(":")
        part = head[1].lstrip(" 0").upper()
        head[1] = part
        dt.value = ': '.join(head)
        frame.title = ' '.join(part.split()[:-1])

# ensure the HEAD title matches the frame title
def match_form_with_prev_title(workbook, charz):
    # first week sheet gets the report sheet name, not subject for change
    for x in range(2, len(workbook.sheetnames)):
        prev = workbook.sheetnames[x-1]
        frame = workbook.worksheets[x]
        for char in charz:
            for row in range(10,17):
                head = frame[f'{char}{row}']
                try:
                    form = head.value.split("'")
                    if len(form) == 1:
                        form = input(f'FOUND {head.value}, {char}{row}, {prev} < ')
                        form = head.value.split("'")
                    form[1] = f"'{prev}'"
                    head.value = ''.join(form)
                except:
                    pass

def enrich_form(
        quant_in, amount_in, quant_out, amount_out, 
        quant_stock, amount_stock, name, prod_row, 
        begin=False, end=False
    ):
    pattern_quant_in = quant_in + f"'{name}'!{'B'}{prod_row}, "
    pattern_amount_in = amount_in + f"'{name}'!{'E'}{prod_row} * '{name}'!{'B'}{prod_row}, "
    pattern_quant_out = quant_out + f"'{name}'!{'G'}{prod_row}, "
    pattern_amount_out = amount_out + f"'{name}'!{'H'}{prod_row}, "
    pattern_quant_stock = quant_stock + f"'{name}'!{'I'}{prod_row}, "
    pattern_amount_stock = amount_stock + f"'{name}'!{'J'}{prod_row}, "
    if begin:
        init = "=SUM("
        pattern_quant_in = init + pattern_quant_in
        pattern_amount_in = init + pattern_amount_in
        pattern_quant_out = init + pattern_quant_out
        pattern_amount_out = init + pattern_amount_out
        pattern_quant_stock = init + pattern_quant_stock
        pattern_amount_stock = init + pattern_amount_stock
    elif end:
        pattern_quant_in += ')'
        pattern_amount_in += ')'
        pattern_quant_out += ')'
        pattern_amount_out += ')'
        pattern_quant_stock += ')'
        pattern_amount_stock += ')'
    return [
        pattern_quant_in,
        pattern_amount_in,
        pattern_quant_out,
        pattern_amount_out,
        pattern_quant_stock,
        pattern_amount_stock
    ]

def report_form(workbook, report, max_ndx, prod, month_mapping, enrich_form):
    
    # gather each month report row relevant to in\out quant\amount
    quant_in_rep_rowz = []
    amount_in_rep_rowz = []
    quant_out_rep_rowz = []
    amount_out_rep_rowz = []
    wb_ndx = 1
    for month_pair in month_mapping:
        month = month_pair[0]
        rep_row = month_pair[1]
        begin = True
        end = False
        quant_in_rep_rowz.append(rep_row)
        amount_in_rep_rowz.append(rep_row+1)
        quant_out_rep_rowz.append(rep_row+2)
        amount_out_rep_rowz.append(rep_row+3)
        prev = workbook.sheetnames[wb_ndx-1]
        frame = workbook.worksheets[wb_ndx] 
        next_frame = ''
        if x != max_ndx-1:
            next_frame = workbook.sheetnames[x+1]
        if month not in prev:
            begin = True
            end = False
        elif month in next_frame:
            begin = False
            end = False
        else:
            begin = False
            end = True        
        # report product iteration by rows iteration
        for j in prod:
            quant_in = ''
            amount_in = ''
            quant_out = ''
            amount_out = ''
            quant_stock = ''
            amount_stock = ''
            # map weekly row to report column
            # product starting on row 10 to 16 
            prod_row = j+9
            rep_chr = prod[j]['chr']
            [
                quant_in, amount_in, quant_out, amount_out,
                quant_stock, amount_stock
            ] = enrich_form(
                quant_in, amount_in, quant_out, amount_out, 
                quant_stock, amount_stock, 
                frame.title, prod_row, begin=begin, end=end
            )
            # concatenated weekly columns to matching report row 
            # place formula pattern in the matching report cell
            report[rep_chr][rep_row].value += quant_in
            report[rep_chr][rep_row+1].value += amount_in
            report[rep_chr][rep_row+2].value += quant_out
            report[rep_chr][rep_row+3].value += amount_out
            report[rep_chr][rep_row+4].value += quant_stock
            report[rep_chr][rep_row+5].value += amount_stock
        wb_ndx += 1
        if end:
            continue

    # GENERAL TOTALS
    # build formula pattern using the above gathered rows    
    for j in prod:
        prod_chr = prod[j]['chr']
        general_quant_in = "=SUM("
        general_amount_in = "=SUM("
        general_quant_out = "=SUM("
        general_amount_out = "=SUM("
        for x in range(12):
            general_quant_in += f'{prod_chr}{quant_in_rep_rowz[x]}, '
            general_amount_in += f'{prod_chr}{amount_in_rep_rowz[x]}, '
            general_quant_out += f'{prod_chr}{quant_out_rep_rowz[x]}, '
            general_amount_out += f'{prod_chr}{amount_out_rep_rowz[x]}, '
        # end pattern 
        report[f'{prod_chr}81'].value = general_quant_in + ')'
        report[f'{prod_chr}82'].value = general_amount_in + ')'
        report[f'{prod_chr}83'].value = general_quant_out + ')'
        report[f'{prod_chr}84'].value = general_amount_out + ')'


xxpath = 'REG.xlsx'
workbook = load_workbook(xxpath)
max_ndx = len(workbook.worksheets)
report = workbook.worksheets[0]
year = 2024
# intrare cantitate\total, iesire cantitate\total, stoc cantitate\total
prod = {
    1: {'prod':'Lumanari 100B', '$': 0, 'chr': 'D'},
    2: {'prod':'Lumanari C20', '$': 0, 'chr': 'E'},
    3: {'prod':'Candele tip 0', '$': 0, 'chr': 'F'},
    4: {'prod':'Candele tip 1', '$': 0, 'chr': 'G'},
    5: {'prod':'Candele tip 2', '$': 0, 'chr': 'H'},
    6: {'prod':'Candele tip 3', '$': 0, 'chr': 'I'},
    7: {'prod':'Candele tip 4', '$': 0, 'chr': 'J'}
}

# cantitate in, total in, cantitate out, total out, cantitate stoc, total stoc
# IAN: 8, etc
month_mapping = [
    ['IAN', 9], 
    ['FEB', 15], 
    ['MAR', 21], 
    ['APR', 27],
    ['MAI', 33], 
    ['IUN', 39], 
    ['IUL', 45], 
    ['AUG', 51], 
    ['SEPT', 57], 
    ['OCT', 63], 
    ['NOV', 69],
    ['DEC', 75]
]
# report_form(workbook, report, max_ndx, prod, month_mapping, enrich_form)
# workbook.save(xxpath)
# workbook.close()