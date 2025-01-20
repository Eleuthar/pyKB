from openpyxl import load_workbook
import argparse


class CustomArgParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage()
        print('Fisierul Excel trebuie sa fie in acelasi director cu scriptul.\n' + \
        'Executati scriptul astfel: python REG.py <numele fisierului excel>')
        exit(2)


def in_out(frame, mode, row):
    # mode == 'B'||'G'
    # row == 10:16
    param = {'B': 'Intrari', 'G': 'Iesiri'}
    while True:
        nir = input("\n" + param[mode] + " " + frame[f'A{row}'].value + f": ")
        if nir == '':
            return 0
        while not nir.isnumeric():
            nir = input("Numar invalid! Introduceti din nou " + \
                param[mode] + " " + frame[f'A{row}'].value + f": "
            )
            if nir in [None, '']:
                frame[f'{mode}{row}'].value = 0
                return 0
        nir = int(nir)
        frame[f'{mode}{row}'].value = nir
        break


def enter_date():
    while True:
        day = None
        month = None
        enter_dm = input('Zi + luna registru (exemplu 12 DEC): ').upper()
        # '04DEC' to '4dec
        enter_dm = enter_dm.strip('0')
        try:
            day = int(''.join([h for h in enter_dm if h.isdigit()]))
            month = ''.join([h for h in enter_dm if h.isalpha()])[:3]
        
            if (
                not str(day).isnumeric()
                or (day < 1 and day > 31)
                or not month.isalpha() 
                or month not in month_mapping
            ):
                continue
            else:
                return day, month
        except:
            continue


def update_general_report(workbook, month_ndx):
    wb_ndx = 1
    try:
        for rep_month in month_ndx:
            for ndx in range(wb_ndx, max_ndx):
                wk = workbook.worksheets[ndx]
                month = wk.title.split()[1]
                row = rep_month[1]
                if rep_month[0] == month:
                    for j in prod:
                        prod_chr = prod[j]['chr']
                        # IN
                        quant_in = wk[f'B{j+9}'].value
                        amount_in = quant_in * wk[f'E{j+9}'].value
                        # OUT
                        quant_out = wk[f'G{j+9}'].value
                        amount_out = wk[f'H{j+9}'].value
                        # STOCK
                        quant_stock = wk[f'I{j+9}'].value
                        amount_stock = wk[f'J{j+9}'].value
                        report[f'{prod_chr}{row}'].value += quant_in
                        report[f'{prod_chr}{row+1}'].value += amount_in
                        report[f'{prod_chr}{row+2}'].value += quant_out
                        report[f'{prod_chr}{row+3}'].value += amount_out
                        # overwrite stock with last known value
                        report[f'{prod_chr}{row+4}'].value = quant_stock
                        report[f'{prod_chr}{row+5}'].value = amount_stock
                        report[f'{prod_chr}81'].value += quant_in
                        report[f'{prod_chr}82'].value += amount_in
                        report[f'{prod_chr}83'].value += quant_out
                        report[f'{prod_chr}84'].value += amount_out
                wb_ndx += 1
    except:
        pass


def insert_frame(workbook, day, month, enter_dm):
    for x in range(1, len(workbook.sheetnames)):
        prev_fm = workbook.sheetnames[x]
        if month in prev_fm:
            fm_day = int(prev_fm.split()[0])
            next_day = int(workbook.sheetnames[x+1].split()[0])
            if fm_day < day < next:
                frame = workbook.copy_worksheet(prev_fm)
                workbook._sheets.pop()
                workbook._sheets.insert(x+1, frame)
                frame.title = enter_dm
                return x, frame


parser = CustomArgParser(description="")
parser.add_argument("file", type=str)
argz = parser.parse_args()
xxpath = argz.file
workbook = load_workbook(xxpath)
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


def gen_sheet_names(wb, no):
    # naming all 
    for month in month_ndx:
        for x in range(1,5):
            prev = wb.worksheets[-1]
            frame = wb.copy_worksheet(prev)
            frame.title = f'{month[0]}{x}'
            # prev stock
            for z in range(10,17):
                frame[f'C{z}'].value = prev[f'I{z}'].value
    
# FIRST TIME initial stock initialization from general report
def init_sheet(wb, prod, year, wb_ndx=1):
    fm = wb.worksheets[x]
    for j in range(1,8):
        prod_row = j+ITEM_OFFSET
        prod_chr = prod[j]['chr']
        C = f'C{prod_row}'
        prev = wb.worksheets[x-1].title
        fm[C] = f"='{prev}'!I{prod_row}"


def put_formula(workbook, sheet_index):
    # usable for sheet[1], others will be copied
    # weekly sheet formulas
    df = workbook.worksheets[sheet_index]
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
        df[F].value = f"={E} *({B} + {C})"
        df[H].value = f"={G} * {E}"
        df[I].value = f"=({B} + {C}) - {G}"
        df[J].value = f"={I} * {E}"
    # weekly totals used by general report
    for z in ['F','H','J']:
        df[f'{z}17'].value = f'=SUM({z}10:{z}16)'


def main_menu():
    opt = ''
    while not opt.isnumeric():
        opt = input("""
            0. Initializare completa de registru
            1. Adaugati registru nou
            2. Inserati registru nou
            3. Ruleaza raport general
            4. Stergere registru
            5. Iesire\n"""
        )
        try:
            opt = int(opt)
            if opt == 5:
                exit()
            if opt in range(5):
                return opt
        except:
            continue

month_mapping = {q:v for q,v in month_ndx}
max_ndx = len(workbook.worksheets)-1
report = workbook.worksheets[0]
year = report.title.split()[-1]

while True:
    frame = None
    prev = None
    wb_ndx = -1
    day, month = enter_date()
    while month not in month_mapping.keys():
        day, month = enter_date()
    enter_dm = f'{day} {month}'
    prev = workbook.worksheets[wb_ndx]
    frame = workbook.copy_worksheet(prev)
    frame.title = enter_dm
    init_sheet(prod, year)
    wb_ndx = workbook.index(frame)
    put_formula(workbook, wb_ndx)
    for x in range(10, 17):
        in_out(frame, 'B', x)
        in_out(frame, 'G', x)    
    update_general_report(workbook, month_ndx)
    workbook.save(xxpath)
    nxt = input('Adaugati registru nou?\nApasati "Enter" pentru a continua\nApasati "N" urmat de "Enter" pt a iesi: ')
    if nxt != '':
        break
