from openpyxl import load_workbook, Workbook
from openpyxl.styles import Alignment
from random import choice
from datetime import date
from os import listdir
from collections import namedtuple


"""
welcome
get_or_create(excel)
enter gamer 3 ~ 6
remove cards \\ keep 8x per gamer
build score table, rowz = 12+(gamer count * 3)
while bidding: no round bid sum == gamer card amount
    prompt gamer bid
bid == fact ? 5 + bid : rez = bid-fact if bid < fact else fact-bid

"""

def gen_frame(fm, group, roundz):
    # deck in hand per round
    for q in range(len(roundz)):
        fm[f'A{q+2}'].value = roundz[q]
    # win count under name row
    for g in group:
        fm[f'{g.chr}1'].value = g.nm
        fm[f'{g.chr}2'].value = g.winz


def get_tabz():
    tabz = []
    for q in listdir():
        if 'xlsx' in q:
            tabz.append(q)
    return tabz
        

def prompt_bet(board, ndx):
    bet = ''
    while not bet.isdigit():
        bet = input(f'Pariu {board[ndx][0]} = ')
    return int(bet)


def prompt_menu(menu_opt):
    err = 'Optiune invalida. Alegeti din nou: '
    while True:
        for z in menu_opt:
            print(z)
        menu = input('')
        try:
            menu = int(menu)
            while menu not in range(1, len(menu_opt)+1):
                menu = input(err)
            return menu
        except:
            menu = input(err)


ROUND = 1
group = []
Member = namedtuple('Member', ['nm','bid','chr','winz']) 
# add members
gmrz = ''
while not gmrz.isdigit():
    gmrz = input('Numar jucatori: ')

gmrz = int(gmrz)

# initialize each player with 
# scoring tracker and sheet column
for q in range(gmrz):
    who = input('Nume jucator: ')
    group.append(Member(who, 0, chr(q+66), 0))

# build rounds
roundz = [1 for z in range(gmrz)] + \
    [x for x in range(2,8)] + \
        [8 for z in range(gmrz)] + \
            [x for x in range(8,1,-1)] + \
                [1 for z in range(gmrz)]
wb = None
# find score workbook, multiple files can be made
tabz = get_tabz()
wb = None
dt = date.today().strftime('%d-%m-%Y')
# make new workbook if none found
if len(tabz) == 0:
    wb = Workbook('wzt.xlsx')
    wb.create_sheet(dt)
else:
    mzg = ''
    # enrich prompt menu for singular or plural
    for z in tabz:
        print(z)
    if len(tabz) > 1:
        mzg = 'mai multe tabele'
    else:
        mzg = 'un tabel'
    # score workbooks menu
    print(f'Am gasit {mzg}')
    menu_opt = ['\n1.Alegeti tabel', '2.Creati tabel nou', '3. EXIT']
    menu = prompt_menu(menu_opt)
    if menu == 3:
        exit()
    # pick existing scoring file
    if menu == 1:
        print('Alegeti tabel')
        for x in range(1, len(tabz)+1):
            menu_opt = [f'{x}. {tabz[x]}' for x in range(len(tabz))]
            menu = prompt_menu(menu_opt)
        wb = load_workbook(tabz[menu-1])
        ROUND = int(wb.sheetnames[-1].split()[-1])+1
        wb.create_sheet(f'Round {ROUND}')
    # no workbook found, make new scoring file
    else:
        while True:
            fn = None
            try:
                fn = input('Introduceti nume fisier: ')
                wb = Workbook()
                fm = wb.worksheets[-1]
                fm.title = 'Round 1'
                gen_frame(fm, group, roundz)
            except:
                print(f'Nume fisier invalid: >> {fn} <<')
# GO
begin = choice(group)
print(f'Spor la joaca! Incepe {begin.nm}')
go = group.index([begin])
while True:
    for ndx in range(go, 4):
        bet = prompt_bet(group, ndx)
    for ndx in range(0, go):
        bet = prompt_bet(group, ndx)
