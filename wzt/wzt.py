from openpyxl import load_workbook, Workbook
from openpyxl.styles import Alignment
from random import choice
from datetime import date
from os import listdir
from collections import namedtuple


# keep user prompt on same line to prevent terminal clutter
def rewind_prompt(mzg, condition=None):
    opt = ''
    # prompt option must be digit in a certain range
    print()
    while True:
        while not opt.isdigit():
            print("\033[A\033[A")
            opt = input(f'mzg:  \b')
        opt = int(opt)
        while not eval(condition):
            continue
        return opt


def group_count():
    gamer_num = ''
    while not gamer_num.isdigit():
        gamer_num = input('Numar jucatori: ')
    return int(gamer_num)


def join_players(gamer_num):
    for q in range(gamer_num):
        group = []
        who = input('Nume jucator: ')
        group.append(Member(who, 0, chr(q+66), 0))
    return group


# the amount of cards in one round depends on the number of players
def hand_num(gamer_num):
    return [1 for z in range(gamer_num)] + \
    [x for x in range(2,8)] + \
        [8 for z in range(gamer_num)] + \
            [x for x in range(8,1,-1)] + \
                [1 for z in range(gamer_num)]


# initialize scoring worksheet
def init_frame(fm, group, roundz):
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
        

def prompt_bet(who, bid, round):
    turn = f'"Pariu {who.nm}, '
    if bid == round:
        mzg = f'{turn} minim 1'
        condition = 'opt >= 1'
        bet = rewind_prompt(mzg, condition=condition)
    elif bid < round:
        mzg = f'{turn} 0 sau mai mare ca {bid}'
        diff = round - bid
        opt = [q for q in range(0, diff)]
        condition = f'opt in {opt}'
        bet = rewind_prompt(mzg, condition=condition)
    who.bet = bet
    return int(bet)


# pick workbook or make new
def prompt_menu(menu_opt):
    mzg = 'Alegeti optiune'
    for z in menu_opt:
        print(z)
    condition = range(1, len(menu_opt)+1)
    menu = rewind_prompt(mzg, condition=condition)
    return menu
    

def get_wb_frame(tabz):
    wb = None
    frame = None
    # make new workbook if none found
    if len(tabz) == 0:
        wb = Workbook(f'wzt_{date.today().strftime('%d-%m-%Y')}.xlsx')
        frame = wb.worksheets[-1]
        frame.title = 'ROUND 1'
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
            frame = wb.create_sheet(f'Round {ROUND}')
        # make new scoring file
        else:
            while True:
                fn = None
                try:
                    fn = input('Introduceti nume fisier: ')
                    wb = Workbook()
                    fm = wb.worksheets[-1]
                    fm.title = 'Round 1'                
                except:
                    print(f'Nume fisier invalid: >> {fn} <<')


# define gamer properties
Member = namedtuple('Member', ['nm','chr','bet','fact','winz']) 
# number of players
gamer_num = group_count()
#  player join
group = join_players(gamer_num)
# number of deck dealing per round
roundz = hand_num(gamer_num)
# find existing score workbook in game directory
tabz = get_tabz()
# read existing or write new workbook
wb, frame = get_wb_frame(tabz)
init_frame(frame, group, roundz)


# GO
ROUND = 1
while True:
    begin = choice(group)
    print(f'Spor la joaca! Incepe {begin.nm}')
    go = group.index([begin])
    for round in roundz:
        # bidding
        bid = 0
        for ndx in range(go, 4):
            bid += prompt_bet(group[ndx], bid, round) 
        for ndx in range(0, go):
            bid += prompt_bet(group[ndx], bid, round)
        # fact
        for ndx in range(go, 4):
            bid += prompt_bet(group[ndx], bid, round) 
        for ndx in range(0, go):
            bid += prompt_bet(group[ndx], bid, round)
