from openpyxl import load_workbook
import argparse

"""
1. none_to_zero
2. enter_date
reset_to_zero
3. import_prev_stock
4. edit_price
    4.1 prompt_unit_price
    4.2 prompt_price_menu
"""

ITEM_OFFSET = 9

class CustomArgParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage()
        print('Fisierul Excel trebuie sa fie in acelasi director cu scriptul.\n' + \
        'Executati scriptul astfel: python REG.py <numele fisierului excel>')
        exit(2)


def prompt_price_menu(frame, prod, opt):
    print('\nPret unitar curent')    
    while True:
        for x in opt:
            pret = '%.2f' % frame[f'E{x+ITEM_OFFSET}'].value
            print(f"{x}. {prod[x]['prod']} = {pret.replace('.', ',')}")
        item = input('Introduceti numar articol de modificat: ')
        try:
            item = int(item)
            if item in opt:
                return item
        except:
            print(f'Optiunea introdusa >> {item} << este invalida\n')


def prompt_unit_price(frame, prod, opt, null_counter):    
    unit = input('\nModificati pret unitar?\nApasati "Enter" pentru "DA"\nApasati "N" urmat de "Enter" pt "NU" ')
    if unit == '':
        item = prompt_price_menu(frame, prod, opt)
        if item in null_counter:
            null_counter.remove(item)
        while True:
            pret = input('Apasati "N" urmat de "Enter" pentru a reveni la meniu.\nIntroduceti pret unitar nou cu zecimale separate de ",": ')
            if pret.isalpha():
                break
            # expected xxx,xx
            if ',' not in pret or ('.' in pret and (pret.index('.') > pret.index(','))):
                print('Preturile unitare nu sunt formatate corespunzator')
                continue
            elif '.' in pret and (pret.index('.') < pret.index(',')):
                pret = pret.replace('.', '').replace(',','.')
            else:
                prod[item]['$'] = float(pret.replace(',','.'))
                frame[f'E{ITEM_OFFSET + item}'].value = prod[item]['$']
                break


def edit_price(frame, prod):
    null_counter = set()
    opt = [x for x in range(1,8)]
    for x in opt:
        tgt = frame[f'E{ITEM_OFFSET + x}']
        if tgt.value in (None, 0, '0', ''):
            null_counter.add(x)
            print(f'Atentie! Pretul pentru {frame[f"A{ITEM_OFFSET + x}"].value} este nul!')
    if null_counter > 0:
        while len(null_counter) > 0:
            prompt_unit_price(frame, prod, opt, null_counter)
    else:
        prompt_unit_price(frame, prod, opt, null_counter)
    

# metoda temporara pt TRANSFER format fizic ce include totalul pt stoc anterior + intrari
def determine_input(x, prod, frame, prev):
    added = 0
    quant = 0
    prod_name = prod[x-ITEM_OFFSET]['prod']
    prod_quant =  prod[x-ITEM_OFFSET]['$']
    prev_quant = prev[f'I{x}'].value
    if prev_quant is None:
        prev_quant = 0
    else:
        prev_quant = int(prev_quant)
    while True:
        quant = input(f'\nCantitate {prod_name} registru vechi (stoc anterior = {prev_quant}) >> ')
        if quant == '':
            quant = prev_quant
            break
        elif quant.isnumeric():
            quant = int(quant)
            if quant < prev_quant:
                print('Cantitatea este mai mica decat stocul anterior')
                continue
            else:
                added = int(quant)-prev_quant
                break
    frame[f'B{x}'] = added
    frame[f'C{x}'] = prev_quant
    print(f"Stoc anterior = {prev_quant}, Adaugari = {added}")


def in_out(mode, row):
    # mode == 'B'||'G'
    # row == 10:16
    param = {'B': 'Intrari', 'G': 'Iesiri'}
    prev_quant = prev[f'I{x}'].value
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
        confirm = input('Valoarea introdus este corecta?\nApasati "Enter" pentru "DA"\nApasati "N" urmat de "Enter" pt "NU" ')
        if confirm.isalpha():
            continue
        frame[f'{mode}{row}'].value = nir
        return nir


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
                not day.isnumeric() 
                or (day < 1 and day > 31)
                or not month.isalpha() 
                or month not in month_mapping
            ):
                continue
            else:
                return day, month
        except:
            continue


# move I, J to C & F
# reset B, I, J
def import_prev_stock(frame, prev=None):
    if prev is None:
        prev = frame
    for x in range(10,17):
        # stock quant
        frame[f'C{x}'].value = prev['I{x}'].value
        # stock total
        frame[f'F{x}'].value = prev['J{x}'].value
        for q in ['B','I','J']:
            frame[f'{q}{x}'].value = 0


# get the current week's product totals for general report
def extract_sheet_product(frame, prod_row):
    # IN
    amount_in = 0
    quant_in = wk[f'B{prod_row+ITEM_OFFSET}'].value
    if quant_in is None:
        quant_in = 0
    else:
        amount_in = quant_in * wk[f'E{prod_row+ITEM_OFFSET}'].value
    # OUT
    quant_out = wk[f'G{prod_row+ITEM_OFFSET}'].value
    amount_out = wk[f'H{prod_row+ITEM_OFFSET}'].value
    if quant_out is None:
        quant_out = 0
    if amount_out is None:
        amount_out = 0        
    # STOCK
    quant_stock = wk[f'I{prod_row+ITEM_OFFSET}'].value
    amount_stock = wk[f'J{prod_row+ITEM_OFFSET}'].value
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


# incremental report monthly & general totals by product
def product_week_total(report_row, frame, prod_chr, prod_row, prev=None):
    [quant_in, amount_in, quant_out, amount_out, quant_stock, amount_stock] = extract_sheet_product(frame, prod_row)
    report[f'{prod_chr}{report_row}'].value += quant_in
    report[f'{prod_chr}{report_row+1}'].value += amount_in
    report[f'{prod_chr}{report_row+2}'].value += quant_out
    report[f'{prod_chr}{report_row+3}'].value += amount_out
    # overwrite stock with last known value
    report[f'{prod_chr}{report_row+4}'].value = quant_stock
    report[f'{prod_chr}{report_row+5}'].value = amount_stock
    report[f'{prod_chr}81'].value += quant_in
    report[f'{prod_chr}82'].value += amount_in
    report[f'{prod_chr}83'].value += quant_out
    report[f'{prod_chr}84'].value += amount_out


# fresh start general total from the last unedited weekly report
# set all report months values to 0, including the general total
def reset_to_zero(report, begin_report_row):
    for row in range(begin_report_row, 85):
        for prod_chr in range(ord('D'), ord('K')):
            report[f'{chr(prod_chr)}{row}'].value = 0

def run_past_report(workbook, report, month, begin_report_row, wb_ndx, prod):
    # past general report should be reviewed starting with at least February, 
    # since the current month would be recalculated by default
    if begin_report_row > ITEM_OFFSET:
        for row in range(ITEM_OFFSET, begin_report_row, 6):
            for prod_chr in range(ord('D'), ord('K')):
                report[f'{chr}81'].value += report[f'{chr(prod_chr)}{row}'].value
                report[f'{chr}82'].value += report[f'{chr(prod_chr)}{row+1}'].value
                report[f'{chr}83'].value += report[f'{chr(prod_chr)}{row+2}'].value
                report[f'{chr}84'].value += report[f'{chr(prod_chr)}{row+3}'].value  
    # determine the previous sheets belonging to the same month
    begin_month_ndx = None
    for z in range(wb_ndx-1, 0, -1):
        if month in workbook.sheetnames[x]:
            begin_month_ndx = z
        else:
            break
    # add previous related weeks registry totals to general report
    if begin_month_ndx is not None:
        for report_row in range(begin_month_ndx, wb_ndx):
            for prod_row in prod:
                prod_chr = prod[prod_row]['chr']
                product_week_total(report_row, frame, prod_chr, prod_row)


# recalculate modified week with updated previous stock quant & amount
def review_week(frame):



def review_next(workbook, report, wb_ndx, max_ndx, extract_sheet_product):
    wb_ndx+=1
    if wb_ndx <= max_ndx:
        # read each sheet
        for ndx in range(wb_ndx, max_ndx):
            frame = workbook.worksheets[wb_ndx]
            month = frame.title.split()[1]
            # determine the report row
            report_row = month_mapping[month]
            # use the previous sheet to get the stock quantity and amount
            prev = workbook.worksheets[wb_ndx-1]
            import_prev_stock(frame, prev=prev)
            review_week(frame)
            for prod_chr in range(ord('D'), ord('K')):
                for prod_row in prod:
                    product_week_total(report_row, frame, prod_chr, prod_row, prev=prev)


def main_menu():
    menu = ''
    while True:
        menu = input('\n1. Adaugare registru\n2. Modificare registru\n3. Stergere registru\n4. Iesire\n'\
        '\nIntroduceti cifra aferenta urmata de "Enter" pentru a continua: ')
        try: 
            menu = int(menu)
            if menu == 4:
                exit()
            elif menu not in (1,2,3):
                continue
            else:
                return menu
        except:
            continue


def insert_frame(workbook, day, month, enter_dm):
    new_frame = None
    for x in range in len(workbook.sheetnames):
        prev_fm = workbook.sheetnames
        if month in prev_fm:
            fm_day = int(prev_fm.split()[0])
            next_day = int(workbook.sheetnames[x+1].split()[0])
            if int(fm_day) < day < next:
                frame = workbook.copy_worksheet(prev_fm)
                workbook._sheets.pop()
                workbook._sheets.insert(x, frame)
                frame.title = enter_dm
                return frame

parser = CustomArgParser(description="Example script with custom error handling")
parser.add_argument("file", type=str)
argz = parser.parse_args()
xxpath = argz.file
workbook = load_workbook(xxpath, data_only=True)
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
# row number starting inventory

# cantitate in, total in, cantitate out, total out, cantitate stoc, total stoc
# IAN: 8, etc
month_ndx = [
    ['IAN', ITEM_OFFSET], 
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
month_mapping = {q:v for q,v in month_ndx}
max_ndx = len(workbook.worksheets)-1
report = workbook.worksheets[0]
year = report.title.split()[-1]
 # ensure entire worksheet has no None
for wk in workbook:
    for x in range(10,17):
        for q in ('B','C','E','F','G','H','I','J'):
            tgt = wk[f'{q}{x}']
            if tgt.value in (None, ''):
                tgt.value = 0
while True:
    retro = False
    wb_ndx = -1
    frame = None
    prev = None
    menu = main_menu()
    day, month = enter_date()
    enter_dm = f'{day} {month}'
    begin_report_row = month_mapping[month]
    month_start = month_ndx.index([month, begin_report_row])
    # determine the position of the active sheet
    final_day, final_month = workbook.worksheets[wb_ndx].title.split()    
    if (
        month_mapping[final_month] < month_mapping[month]
        or (
            month_mapping[final_month] == month_mapping[month] 
            and day < int(final_day)
        )
    ):
        retro = True
        # consider making a new sheet among older
        frame = insert_frame(workbook, day, month, enter_dm)
        wb_ndx = workbook.index(frame)
        prev = workbook.worksheets[wb_ndx-1]
    # exception triggered on `frame = workbook[enter_dm]`
    # if the frame doesn't exist, it's considered to be a new one
    else:
        prev = workbook.worksheets[wb_ndx]
        frame = workbook.copy_worksheet(prev)
        frame.title = enter_dm
        frame['F2'].value = f'DATA: {enter_dm} {year}'
    # 1=add, 2=modify, 3=remove
    if menu == 1:
        import_prev_stock(frame, prev=prev)
    else:
        if menu == 3:
            del workbook[enter_dm]
            max_ndx -= 1
            import_prev_stock(frame, prev=prev)
        else:
            import_prev_stock(frame)
        # reset general report values starting from current month
        reset_to_zero(report, begin_report_row)
        run_past_report(workbook, report, month, begin_report_row, wb_ndx, prod)
        review_next(prev)
        if menu == 3:
            continue
    edit_price(frame, prod)
    # x is product row for B & G 10:16 in\out parser
    for x in range(10, 17):
        # alternative to in_out() if entered amount is to be determined
        # determine_input (x, prod, frame, prev)
        # valoare totala stoc nou intrat
        quant_in = in_out('B', x)
        amount_in = quant_in * frame[f'E{x}'].value
        quant_out = in_out('G', x)
        amount_out = quant_out * frame[f'E{x}'].value
        # F \\ Valoare totala intrari + stoc curent
        amount_stock = (frame[f'B{x}'].value + frame[f'C{x}'].value) * frame[f'E{x}'].value
        frame[f'F{x}'].value = amount_stock
        frame['F17'].value += amount_stock        
        # H \\ Valoare totala iesiri
        frame[f'H{x}'].value = amount_out
        frame['H17'].value += amount_out
        # I \\ Cantitate stoc ramas
        quant_stock = (frame[f'B{x}'].value + frame[f'C{x}'].value) - frame[f'G{x}'].value
        frame[f'I{x}'].value = quant_stock        
        # J \\ Valoare stoc ramas
        amount_stock -= amount_out
        frame[f'J{x}'].value = amount_stock
        frame['J17'].value += amount_stock        
        # add current week totals to general report
        report_row = month_mapping[month]
        prod_chr = prod[x-ITEM_OFFSET]['chr']
        product_week_total(report_row, frame, prod_chr, x)
    if retro:
        # propagate the changes to all subsequent sheets following the current week
        review_next(workbook, report, wb_ndx, max_ndx, extract_sheet_product, menu)
    workbook.save(xxpath)
    nxt = input('Adaugati registru nou?\nApasati "Enter" pentru a continua\nApasati "N" urmat de "Enter" pt a iesi: ')
    if nxt != '':
        break
    