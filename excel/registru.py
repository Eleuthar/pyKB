import openpyxl
from openpyxl.styles import Alignment
import argparse


class CustomArgParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage()
        print('Fisierul Excel trebuie sa fie in acelasi director cu scriptul.\n' + \
        'Executati scriptul astfel: python REG.py <numele fisierului excel>')
        exit(2)

def menu_input(frame, prod, opt):
    print('Pret unitar curent\n')
    for x in range(1, 8):
        pret = frame['E'][x+9]
        prod[x]['$'] = pret
        print(f"{x}. {prod[x]['prod']} = {pret:.2f}")
    while True:
        menu = input('Introduceti numar articol de modificat: ')
        try:
            menu = int(menu)
            if menu in opt:
                return menu
            except:
                print(f'Optiunea introdusa >> {menu} << este invalida')
                continue

def in_out(mode, row):
    # mode == 'B'||'G'
    # row == 10:16 
    param = {'B': 'Intrari', 'G': 'Iesiri'}
    nir = input(param[mode] + " " + frame[f'A{row}'].value + ": ")
    if nir is None or nir == '':
        nir = 0
    frame[f'{mode}{row}'].value = nir

parser = CustomArgParser(description="Example script with custom error handling")
parser.add_argument("file", type=str)
argz = parser.parse_args()
xxpath = argz.file
workbook = openpyxl.load_workbook(xxpath)
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
    total_j = frame['J18']
    total_j.value = 0
    frame.title = f"Sheet{len(workbook.sheetnames)}"
    enter_year = input('An registru: ')
    enter_dm = input('Zi + luna registru: ')
    frame['F2'].value = f'DATA: {enter_dm} {enter_year}'
    # convert None or '' to 0
    for j in ['B', 'C', 'E', 'F', 'G', 'H', 'I', 'J']:
        for row in range(10, 17):
            tgt = frame[f'{j}{row}']
            if tgt.value == '' or tgt.value is None:
                tgt.value = 0
            elif j == 'E' and isinstance(tgt.value, str):
                tgt.value = float(tgt.value.replace(",", "."))
            # Importare sheet anterior I10:16
            if j == 'I':
                frame[f'C{row}'].value = tgt.value
                tgt.value = 0
            # Resetare valori iesire
            if j == 'J':
                tgt.value = 0
    # update pret unitar
    opt = [x for x in range(1, 8)]
    while True:
        unit = input('Modificati pret unitar?\nApasati "Enter" pentru "DA"\nApasati "Esc" urmat de "Enter" pt "NU" ')
        if unit == '':
            menu = menu_input(frame, prod, opt)
            if menu in opt:
                while True
                    pret = input('Introduceti pret unitar nou cu zecimale separate de ",": ')
                    try
                        pret = pret.replace(',','.')
                        frame['E'][x+menu] = pret
                        break
                    except
                        pret = input(f'Valoare invalida: {pret}.\n')
        else:
            break            
    # parser
    for x in range(10, 17):
        # B & G 10:16 intrari\iesiri

        """TRANSFER format fizic ONLY"""
        new_reg_quant = int(input('Cantitate registru nou > '))
        added = new_reg_quant - int(prev['I'][x].value)
        prev_quant = new_reg_quant - added
        frame['B'][x] = added
        frame['C'][x] = prev_quant
        print(f"Stoc anterior = {prev_quant}, Adaugari = {added}")
        
        """De decomentat dupa transfer registru fizic in care lipseste Adaugari"""
        # in_out('B', x)
        in_out('G', x)

        # F \\ Valoare totala intrari
        frame[f'F{x}'].value = (int(frame[f'B{x}'].value) + int(frame[f'C{x}'].value)) * int(frame[f'E{x}'].value)
        total_f.value += frame[f'F{x}'].value
        
        # H \\ Valoare totala iesiri
        frame[f'H{x}'].value = int(frame[f'E{x}'].value) * int(frame[f'G{x}'].value)
        
        # I \\ Cantitate stoc ramas
        frame[f'I{x}'].value = (int(frame[f'B{x}'].value) + int(frame[f'C{x}'].value)) - int(frame[f'G{x}'].value)
        
        # J \\ Valoare stoc ramas
        frame[f'J{x}'].value = int(frame[f'E{x}'].value) * int(frame[f'I{x}'].value)
        total_j.value += frame[f'J{x}'].value

    workbook.save(xxpath)
    nxt = input('Adaugati registru nou?\nApasati "Enter" pentru a continua\nApasati "Esc" urmat de "Enter" pt a iesi')
    if nxt != (''):
        break
