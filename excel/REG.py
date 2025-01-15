from openpyxl import load_workbook
import argparse
from pdb import set_trace

ITEM_OFFSET = 9

class CustomArgParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage()
        print('Fisierul Excel trebuie sa fie in acelasi director cu scriptul.\n' + \
        'Executati scriptul astfel: python REG.py <numele fisierului excel>')
        exit(2)


def prompt_unit_price(frame, prod, opt):
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


def edit_price(frame, prod):
    opt = [x for x in range(1,8)]
    while True:
        unit = input('Modificati pret unitar?\nApasati "Enter" pentru "DA"\nApasati "N" urmat de "Enter" pt "NU" ')
        if unit == '':
            item = prompt_unit_price(frame, prod, opt)
            while True:
                pret = input('"N" urmat de "Enter" pentru a reveni la meniu.\nIntroduceti pret unitar nou cu zecimale separate de ",": ')
                if pret == '\x1b':
                    break
                # expected xxx,xx
                if ',' not in pret or ('.' in pret and (pret.index('.') > pret.index(','))):
                    print('Preturile unitare nu sunt formatate corespunzator')
                    continue
                elif '.' in pret and (pret.index('.') < pret.index(',')):
                    pret = pret.replace('.', '').replace(',','.')
                else:
                    prod[item]['$'] = float(pret.replace(',','.'))
                    frame[f'E{ITEM_OFFSET+item}'].value = prod[item]['$']
                    break
        else:
            break


# metoda temporara pt TRANSFER format fizic
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
    nir = input(param[mode] + " " + frame[f'A{row}'].value + f": ")
    if nir in [None, '']:
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
    return nir

    
def initialize(frame):
    for x in range(10,17):
        for q in ('B','C','E','F','G','H','I','J'):
            tgt = frame[f'{q}{x}']
            # Reset to 0
            if q in ('B','C','F','G','H','J'):
                tgt.value = 0                
            # move I quantity to C & reset I
            if q == 'I':
                if tgt.value in (None, ''):
                    tgt.value = 0
                frame[f'C{x}'].value = tgt.value
                tgt.value = 0


 # clear all 0 cells before saving the worksheet
def zero_to_none_or_float(frame):
    for x in range(10,17):
        for q in ('B', 'C', 'E', 'F', 'G', 'H', 'I', 'J'):
            tgt = frame[f'{q}{x}']
            if tgt.value in (0, '0'):
                tgt.value = None
            # elif q in ('E','F','H','J'):
            #     if tgt.value is not None:
            #         tgt.data_type='n'
            #         tgt.number_format='#,##0.00'
            #         tgt.value = float(tgt.value.replace(',','.'))


parser = CustomArgParser(description="Example script with custom error handling")
parser.add_argument("file", type=str)
argz = parser.parse_args()
xxpath = argz.file
# xxpath='REG.xlsx'
workbook = load_workbook(xxpath, data_only=True)
# IAN-DEC = 8-79
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
enter_year = input('An registru: ')
while True:
    prev = workbook.worksheets[-1]
    frame = workbook.copy_worksheet(prev)
    amount_before = frame['F17']
    amount_before.value = 0
    month_total_out = frame['H17']
    month_total_out.value = 0
    amount_after = frame['J17']
    amount_after.value = 0
    enter_dm = 'x z'
    while enter_dm.split()[1] not in rep_ndx.keys():
        enter_dm = input('Zi + luna registru (ex. 12 DEC): ').upper()
    frame['F2'].value = f'DATA: {enter_dm} {enter_year}'
    frame.title = enter_dm
    initialize(frame)
    edit_price(frame, prod)
    
    # general report
    report = workbook.worksheets[0]
    month = frame.title.split()[1]
    frame['F17'].value = 0
    frame['H17'].value = 0
    frame['J17'].value = 0
    # B & G 10:16 in\out parser
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
        
        # general report
        row = rep_ndx[month]
        prod_chr = prod[x-ITEM_OFFSET]['chr']
        rep_mapping = {
            'quant_in': [report[f'{prod_chr}{row}'], quant_in],
            'amount_in': [report[f'{prod_chr}{row+1}'], amount_in],
            'quant_out': [report[f'{prod_chr}{row+2}'], quant_out],
            'amount_out': [report[f'{prod_chr}{row+3}'], amount_out],
            'quant_stock': [report[f'{prod_chr}{row+4}'], quant_stock],
            'amount_stock': [report[f'{prod_chr}{row+5}'], amount_stock],
            'general_quant_in': [report[f'{prod_chr}81'], quant_in],
            'general_amount_in': [report[f'{prod_chr}82'], amount_in],
            'general_quant_out': [report[f'{prod_chr}83'], quant_out],
            'general_amount_out': [report[f'{prod_chr}84'], amount_out]
        }
        # set_trace()
        for rep_cell in rep_mapping.values():
            if rep_cell[0].value is None:
                rep_cell[0].value = 0
            rep_cell[0].value += rep_cell[1]
    
    zero_to_none_or_float(frame)
    workbook.save(xxpath)
    nxt = input('Adaugati registru nou?\nApasati "Enter" pentru a continua\nApasati "N" urmat de "Enter" pt a iesi: ')
    if nxt not in ('', None):
        break
    