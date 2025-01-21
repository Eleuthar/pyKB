from openpyxl import load_workbook, Workbook
from openpyxl.styles import Alignment
from random import choice
from datetime import date
from os import listdir
from collections import namedtuple
from pdb import set_trace


# keep user prompt on same line to prevent terminal clutter
def rewind_prompt(mzg, condition=None):
    opt = ''
    # prompt option must be digit in a certain range
    print()
    while True:
        while not opt.isdigit():
            print("\033[A\033[A")
            opt = input(f'{mzg}:  \b')
        opt = int(opt)
        if condition is not None:
            while not eval(condition):
                continue        
        return opt


def group_count():
    gamer_num = ''
    while not gamer_num.isdigit():
        gamer_num = input('Numar jucatori: ')
    return int(gamer_num)


def join_players(gamer_num):
    group = []
    char = 64
    for q in range(gamer_num):
        char+=2
        who = input('Nume jucator: ')
        # 'nm','chr','bet','fact','winz','failz','total'
        group.append(Member(who, chr(char), 0, 0, 0, 0, 0))
    return group


# the amount of cards in one round depends on the number of players
def hand_num(gamer_num):
    return [1 for z in range(gamer_num)] + \
    [x for x in range(2,8)] + \
        [8 for z in range(gamer_num)] + \
            [x for x in range(8,1,-1)] + \
                [1 for z in range(gamer_num)]


def merge_and_write(sheet, start_row, end_row, start_col, end_col, value):
    sheet.merge_cells(start_row=start_row, start_column=start_col, end_row=end_row, end_column=end_col)
    cell = sheet.cell(row=start_row, column=start_col, value=value)
    cell.alignment = Alignment(horizontal="center", vertical="center")


# initialize scoring worksheet
def init_frame(fm, group, roundz, gamer_num):
    # deck in hand per round
    for q in range(len(roundz)):
        fm[f'A{q+4}'].value = roundz[q]
    # total score under name row    
    for q in range(gamer_num):
        uzr = group[q]
        char = uzr.chr
        start_col = fm[f'{char}1'].col_idx
        merge_and_write(fm, 1, 1, start_col, start_col+1, uzr.nm)
        merge_and_write(fm, 2, 2, start_col, start_col+1, uzr.total)
        fm[f'{char}3'].value = 'Pariat'
        fm[f'{chr(ord(char)+1)}3'].value = 'Facut'
        # hands start at row 4
        for j in range(len(roundz)):
            hand = j+3
            # bet
            fm[f'{char}{hand}'].value = 0
            # fact
            fm[f'{chr(ord(char)+1)}{hand}'].value = 0


def get_tabz():
    tabz = []
    for q in listdir():
        if 'xlsx' in q:
            tabz.append(q)
    return tabz
        

def prompt_bet(who, bid, hand):
    turn = f'{who.nm} -->'
    if bid == hand:
        mzg = f'{turn} minim 1'
        condition = 'opt >= 1'
        bet = rewind_prompt(mzg, condition=condition)
    elif bid < hand:
        diff = hand - bid
        opt = [q for q in range(0, diff+1)]
        set_trace()
        mzg = f"{turn} {', '.join(opt)} sau mai mare ca {diff}"
        condition = f'bet in {opt} or bet > {diff}'
        bet = rewind_prompt(mzg, condition=condition)
    else:
        mzg = f"{turn} 0 sau mai mult"
        condition = f'bet >= 0'
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
    fname = None
    frame = None
    ROUND = 1
    # make new workbook if none found
    if len(tabz) == 0:
        dt = date.today().strftime('%d-%m-%Y')
        fname = f'wzt_{dt}.xlsx'
        wb = Workbook()
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
            ROUND = len(wb.sheetnames)+1
            frame = wb.create_sheet(title=f'Round {ROUND}')
        # make new scoring file
        else:
            while True:
                try:
                    fname = input('Introduceti nume fisier: ')
                    wb = Workbook()
                    frame = wb.worksheets[-1]
                    frame.title = 'ROUND 1'
                except:
                    print(f'Nume fisier invalid: >> {fname} <<')
    return wb, fname, frame, ROUND


if __name__ == '__main__':
    # define gamer properties
    Member = namedtuple('Member', ['nm','chr','bet','fact','winz','failz','total'])
    # number of players
    gamer_num = group_count()
    #  player join
    group = join_players(gamer_num)
    # number of deck dealing per round
    roundz = hand_num(gamer_num)
    # find existing score workbook in game directory
    tabz = get_tabz()
    # read existing or write new workbook
    wb, fname, frame, ROUND = get_wb_frame(tabz)
    init_frame(frame, group, roundz, gamer_num)

    # GO
    while True:
        begin = choice(group)
        print(f'\nSpor la joaca! Incepe {begin.nm}\n')
        go = group.index(begin)
        order = list(range(go, 4)) + list(range(0, go))
        for j in range(len(roundz)):
            hand = roundz[j]
            print(f"\nRunda de {hand}\n{'='*len('runda de x')}")

            # bidding
            print(f'\nPariaza\n{"`"*len("nPariaza")}')
            bid = 0
            for ndx in order:
                bid += prompt_bet(group[ndx], bid, hand)

            # fact
            print(f'\nMaini facute\n{"="*len("Maini facute")}')
            for ndx in order:
                bidder = group[ndx]
                bidder.fact = rewind_prompt(bidder.nm)
                # winner
                if bidder.fact == bidder.bet:
                    bidder.winz += 1
                    bidder.total += (5+bidder.bet)
                    # positive bonus & reset streak
                    if bidder.winz == gamer_num:
                        bidder.total += (5*gamer_num)
                        bidder.winz = 0
                # loser
                else:
                    bidder.failz += 1
                    bidder.total -= (5+ (bidder.fact - bidder.bet))
                    # negative bonus & reset streak
                    if bidder.failz == gamer_num:
                        bidder.total -= (5*gamer_num)
                        bidder.failz = 0
                # update player data, rounds begin at row 4 on split columns 
                char = bidder.chr
                frame[f'{char}{ndx}'].value += bidder.bet
                frame[f'{chr(ord(char)+1)}{ndx}'].value += bidder.fact
                wb.save(fname)
        
                