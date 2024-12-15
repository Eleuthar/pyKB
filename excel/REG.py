from openpyxl import load_workbook
import argparse


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
            pret = '%.2f' % frame[f'E{x+9}'].value
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
        unit = input('Modificati pret unitar?\nApasati "Enter" pentru "DA"\nApasati "Esc" urmat de "Enter" pt "NU" ')
        if unit == '':
            item = prompt_unit_price(frame, prod, opt)
            while True:
                pret = input('Introduceti pret unitar nou cu zecimale separate de ",": ')
                # expected xxx,xx
                if ',' not in pret or ('.' in pret and (pret.index('.') > pret.index(','))):
                    print('Preturile unitare nu sunt formatate corespunzator')
                    continue
                elif '.' in pret and (pret.index('.') < pret.index(',')):
                    pret = pret.replace('.', '').replace(',','.')
                else:
                    prod[item]['$'] = float(pret.replace(',','.'))
                    frame[f'E{9+item}'].value = prod[item]['$']
                    break
        else:
            break


# metoda temporara pt TRANSFER format fizic
def paper_format_transfer(x, prod, frame, prev):
    added = 0
    quant = 0
    prod_name = prod[x-9]['prod']
    prod_quant =  prod[x-9]['$']
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
    nir = 'None'
    while not nir.isnumeric():
        nir = input(param[mode] + " " + frame[f'A{row}'].value + f": ")
        if nir is None or nir == '':
            nir = '0'
    frame[f'{mode}{row}'].value = int(nir)

    
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

prod = {
    1: {'prod':'Lumanari 100B', '$': 0},
    2: {'prod':'Lumanari C20', '$': 0},
    3: {'prod':'Candele tip 0', '$': 0},
    4: {'prod':'Candele tip 1', '$': 0},
    5: {'prod':'Candele tip 2', '$': 0},
    6: {'prod':'Candele tip 3', '$': 0},
    7: {'prod':'Candele, tip 4', '$': 0}
}

while True:
    prev = workbook.worksheets[-1]
    frame = workbook.copy_worksheet(prev)
    total_f = frame['F18']
    total_f.value = 0
    total_h = frame['H18']
    total_h.value = 0
    total_j = frame['J18']
    total_j.value = 0
    enter_year = input('An registru: ')
    enter_dm = input('Zi + luna registru (ex. 12 DEC): ').upper()
    frame['F2'].value = f'DATA: {enter_dm} {enter_year}'
    frame.title = enter_dm
    initialize(frame)
    prompt_unit_price(frame, prod)

    # B & G 10:16 in\out parser
    for x in range(10, 17):
        # comment below after migration from paper
        paper_format_transfer(x, prod, frame, prev)
        
        # regular flow
        # uncomment below after migration from paper where "Adaugari" is missing
        # in_out('B', x)
        in_out('G', x)

        # F \\ Valoare totala intrari
        frame[f'F{x}'].value = (float(frame[f'B{x}'].value) + float(frame[f'C{x}'].value)) * float(frame[f'E{x}'].value)
        total_f.value += frame[f'F{x}'].value
        
        # H \\ Valoare totala iesiri
        frame[f'H{x}'].value = float(frame[f'E{x}'].value) * float(frame[f'G{x}'].value)
        total_h.value += frame[f'H{x}'].value
        # I \\ Cantitate stoc ramas
        frame[f'I{x}'].value = (int(frame[f'B{x}'].value) + int(frame[f'C{x}'].value)) - int(frame[f'G{x}'].value)
        
        # J \\ Valoare stoc ramas
        frame[f'J{x}'].value = float(frame[f'E{x}'].value) * float(frame[f'I{x}'].value)
        total_j.value += frame[f'J{x}'].value
    
    zero_to_none_or_float(frame)
    workbook.save(xxpath)
    nxt = input('Adaugati registru nou?\nApasati "Enter" pentru a continua\nApasati "Esc" urmat de "Enter" pt a iesi')
    if nxt != '':
        break