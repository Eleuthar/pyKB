import io
from xlsxwriter import Workbook
from openpyxl import load_workbook
from datetime import date
from os import listdir
from dataclasses import dataclass
import json
from re import search
from copy import copy
from sys import argv, exit
from pdb import set_trace

# any single argument triggers test

# customization
env = json.load(open('env.json'))
# first column dedicated for round count
COLUMN_OFFSET = env['column_offset'] + 66

@dataclass
class Member:
    nm: str
    bet_char: str
    done_char: str
    point_char: str
    bet: list
    done: list
    point: list
    report: list
    total: int


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
            if not eval(condition):
                opt = ''
                continue
            else:
                return opt
        return opt


def group_count():
    gamer_num = ''
    while not gamer_num.isdigit():
        gamer_num = input('Numar jucatori: ')
    return int(gamer_num)


def join_players(COLUMN_OFFSET, gamer_num):
    group = []
    uzr_char = COLUMN_OFFSET
    print()
    for q in range(gamer_num):
        # bet \ done \ point
        bet_char = chr(uzr_char)
        done_char = chr(uzr_char + 1)
        point_char = chr(uzr_char+ 2)
        who = input('Nume jucator: ')
        # nm,bet_char,done_char,point_char,winz,failz,total
        group.append(
            Member(
                nm=who,
                bet_char = bet_char,
                done_char = done_char,
                point_char = point_char,
                bet = [], done = [], point = [],
                report = [], total=0
            )
        )
        uzr_char += 3
    return group


# the amount of cards in one round depends on the number of players
def hand_num(gamer_num):
    return [1 for z in range(gamer_num)] + \
    [x for x in range(2,8)] + \
        [8 for z in range(gamer_num)] + \
            [x for x in range(7,1,-1)] + \
                [1 for z in range(gamer_num)]


def format_data(pen, formatting, pending_colorize, group, roundz, gamer_num):   # tall name row 
    pen.set_row(0, 27)
    # round number column
    round_col = chr(COLUMN_OFFSET-1)
    pen.write(f'{round_col}3', 'Nr', formatting['done'])
    # narrow round counter column
    pen.set_column(f"{round_col}:{round_col}", 5)
    # all rows except for name
    for row in range(1,4):
        pen.set_row(row, 25)
    for uzr in group:
        # name
        pen.merge_range(f"{uzr.bet_char}1:{uzr.point_char}1", uzr.nm, formatting['header'])
        # total
        pen.merge_range(f"{uzr.bet_char}2:{uzr.point_char}2", uzr.total, formatting['total'])
        # stats
        for col in (uzr.bet_char, uzr.done_char, uzr.point_char):
            pen.set_column(f"{col}:{col}", 10)
        pen.write(f'{uzr.bet_char}3', 'Pariat', formatting['stat'])
        pen.write(f'{uzr.done_char}3', 'Facut', formatting['stat'])
        pen.write(f'{uzr.point_char}3', 'Puncte', formatting['stat'])
        # round iteration from row 4
        for j in range(len(roundz)):
            row = j+4
            pen.set_row(row, 25)
            pen.write(f'{round_col}{row}', f'#{j+1}', formatting['done'])
            pen.write(f'{uzr.bet_char}{row}', uzr.bet[j], formatting['bet'])
            pen.write(f'{uzr.done_char}{row}', uzr.done[j], formatting['done'])
            point = f'{uzr.point_char}{row}'
            color = pending_colorize.get(point, '')
            pen.write(point, uzr.point[j], formatting['point'])
    # table bottom border
    # pen.merge_range(
        # f'{group[0].bet_char}{row+1}:{group[-1].point_char}{row+1}', 
        # '', wb.add_format({'top': 2}))


def export_dataframe(output, fname, ROUND, max_col, max_row, begin_char):
    output.seek(0)
    memwb = load_workbook(output)
    mainframe = memwb.active
    tgt_wb = load_workbook(fname)
    tgt_frame = tgt_wb.create_sheet(f"ROUND {ROUND}")
    # column width
    for col in range(begin_char+1, max_col):
        char = chr(col)
        tgt_frame.column_dimensions[char].width = mainframe.column_dimensions[char].width-4
    for row in range(1, max_row):
        # row height
        tgt_frame.row_dimensions[row].height = mainframe.row_dimensions[row].height-4
        for col in range(begin_char, max_col):
            coord = f'{chr(col)}{row}'
            orig = mainframe[coord]
            tgt = tgt_frame[coord]
            tgt.value = orig.value
            tgt.font = copy(orig.font)
            tgt.fill = copy(orig.fill)
            tgt.border = copy(orig.border)
            tgt.alignment = copy(orig.alignment)
    # MERGED
    for merged_range in mainframe.merged_cells.ranges:
        tgt_frame.merge_cells(
            start_row = merged_range.min_row, 
            start_column = merged_range.min_col,
            end_row = merged_range.max_row,
            end_column = merged_range.max_col
        )
    tgt_wb.save(fname)
    output.close()


def get_tabz():
    tabz = []
    for q in listdir():
        if 'xlsx' in q and not q.startswith('~'):
            tabz.append(q)
    return tabz


def prompt_bet(who, ndx, final_bidder, bid, hand):
    turn = f'{who} -->'
    allowed = None
    # no constraint for final bidder if bid > hand
    if ndx == final_bidder and bid <= hand:
        diff = hand - bid
        allowed = [q for q in range(0, hand+1)]
        allowed.remove(diff)
    else:
        allowed = [q for q in range(0, hand+1)]
    mzg = f"{turn} {allowed}"
    condition = f'opt in {allowed}'
    bet = int(rewind_prompt(mzg, condition=condition))
    return bet


# pick workbook or make new
def prompt_menu(menu):
    mzg = '\nAlegeti optiune'
    for z in menu:
        print(z)
    condition = f"opt in range(0, {len(menu)})"
    menu = rewind_prompt(mzg, condition=condition)
    return menu
    

def mk_wb(ROUND, fname, is_new, output):
    if not is_new:
        wb = Workbook(output, {'in_memory': True})
        pen = wb.add_worksheet(f'ROUND {ROUND}')
    else:
        wb = Workbook(fname)
        pen = wb.add_worksheet(f'ROUND {ROUND}')
    return wb, pen


def main_menu(
        tabz, is_new=True, ROUND=1, 
        fname=f"Whist {date.today().strftime('%d-%m-%Y')}.xlsx",
        menu=0
    ):
    """ Return 
        * round counter for sheetname 
        * filename for new or existing workbook
    """
    if len(tabz) > 0:
        menu_opt = ['\n\n0. EXIT', '1. Creati tabel nou', '2. Alegeti tabel']
        # enrich prompt menu for singular or plural
        if len(tabz) > 1:
            mzg = 'mai multe tabele'
        else:
            mzg = 'un tabel'
        # score workbooks menu
        print(f'\nAm gasit {mzg}\n')
        for z in tabz:
            print(z)
        menu = prompt_menu(menu_opt)
        if menu == 0:
            exit()
        # pick existing scoring file
        if menu == 2:
            is_new = False
            menu_opt = [f'{x+1}. {tabz[x]}' for x in range(len(tabz))]
            menu_opt.insert(0, '\n\n0. Meniu anterior')
            menu = prompt_menu(menu_opt)
            if menu == 0:
                return 'back', 'to', 'menu'
            fname = tabz[menu-1]
            reader = load_workbook(fname)
            ROUND = len(reader.sheetnames)+1
            return is_new, fname, ROUND
        # make new scoring file
        else:
            menu_opt = ['\n\n0. Inapoi', '1.Alege nume', '2.Genereaza nume cu data de azi', ]
            menu = prompt_menu(menu_opt)
            if menu == 0:
                return 'back to menu'
            elif menu == 2:
                fname = f"Whist {date.today().strftime('%d-%m-%Y')}.xlsx"
            else:
                reserved = ("CON", "PRN", "AUX", "NUL", "COM1", "LPT1")
                pattern = r'[<>:"/\\|?*]'
                condition = f"not search({pattern}, opt) and (filename.strip() != '') and not (filename.split('.')[0].upper() in reserved_names)"
                menu_opt = rewind_prompt('Introduceti nume fisier: ', condition=condition)
                fname = f"{fname}.xlsx"
            return is_new, fname, ROUND
                
    else:
        fname = f"Whist {date.today().strftime('%d-%m-%Y')}.xlsx"
        print("Tabelul de scor: " + fname)
        return is_new, fname, ROUND


# mark Cell for color formatting during datapen dump
def colorize(pending_colorize, color, point_char, row, gamer_num):
    for j in range(row-gamer_num, row):
        pending_colorize[f'{point_char}{j}'] = f'{color}_color'
    return pending_colorize


def parse_point(gamer_num, round, hand, bidder, colorize, pending_colorize):
    BONUS = 5
    done = bidder.done[round]
    bet = bidder.done[round]

    # win
    if done == bet:
        if hand >= 1:
            bidder.report.append(1)
        point = 5 + bet
        bidder.point.append(point)
        bidder.total += bidder.point[round]
        # positive bonus & reset streak
        if hand > 1:
            winz = bidder.report[round-BONUS:round].count(1)
            if winz == BONUS:
                bidder.total += (BONUS * gamer_num)
                pending_colorize = colorize(
                    pending_colorize, 'green', bidder.point_char, round, gamer_num)
    # lose
    else:
        if hand > 1:
            bidder.report.append(0)
        # make negative to positive to allow subtraction from total
        point = int(str(done - bet).strip('-'))
        bidder.point.append(point)
        bidder.total -= point
        if hand != 1:
            failz = bidder.report[round-BONUS:round].count(0)
            if failz == BONUS:
                # negative bonus & reset streak
                bidder.total -= (BONUS * gamer_num)
                pending_colorize = colorize(
                    pending_colorize, 'red', bidder.point_char, round, gamer_num)
    return pending_colorize


def demo(output, fname, wb, pen, formatting, roundz):
    gamer_num = 4
    group = [
        Member(nm='ela', bet_char='D', done_char='E', point_char='F',
            bet = [1, 1, 1, 1, 2, 3, 4, 5, 1, 2, 4, 2, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1],
            done= [1, 1, 1, 1, 2, 3, 4, 5, 2, 3, 5, 1, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1],
            point=[],
            report=[], total=0
        ),
        Member(nm='geo', bet_char='G', done_char='H', point_char='I',
            bet = [1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1],
            done =[1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1],
            point=[],
            report=[], total=0),
        Member(nm='flo', bet_char='J', done_char='K', point_char='L',
            bet = [1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1],
            done =[1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1],
            point=[],
            report=[], total=0),
        Member(nm='cip', bet_char='M', done_char='N', point_char='O',
            bet = [1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1],
            done= [1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1],
            point=[],
            report=[], total=0)
    ]
    pending_colorize = {}
    for round in range(len(roundz)):
        row = round + 4
        for bidder in group:
            hand = roundz[round]
            pending_colorize = parse_point(
                gamer_num, round, hand, bidder, colorize, pending_colorize
            )
    format_data(pen, formatting, pending_colorize, group, roundz, gamer_num)
    wb.close()
    if not is_new:
        # dump in memory dataframe to file
        export_dataframe(output, fname, 1, 
        (len(group)*3+66), len(roundz)+3, COLUMN_OFFSET-1)


if __name__ == '__main__':
    # in memory writer object
    output = io.BytesIO()

    # TESTING: COMMENT 344 & 345 & UNCOMMENT line 346
    # gamer_num = group_count()
    # group = join_players(COLUMN_OFFSET, gamer_num)
    gamer_num = 4

    wb, pen = None, None
    # number of deck dealing per round
    roundz = hand_num(gamer_num=4)
    # find score workbook in game directory
    tabz = get_tabz()
    # if workbook is not new, make in memory copy 
    # add new sheet with openpyxl
    is_new, fname, ROUND = main_menu(tabz)
    while is_new == 'back':
        is_new, fname, ROUND = main_menu(tabz)
    wb, pen = mk_wb(ROUND, fname, is_new, output)
    
    # formatting
    formatting = {}
    for bg in ['header','total','stat','bet','done','point','green_point','red_point']:
        formatting[bg] = wb.add_format(env['formatting'][bg])
    _next = -1
    pending_colorize = {}
    group = []

    # TEST ONLY, comment 348, 350
    if len(argv) == 2:
        demo(output, fname, wb, pen, formatting, roundz)
        exit()

    # PRODUCTION
    else:
        while True:
            print(f'\nSpor la joaca!\n')
            for j in range(len(roundz)):
                row = j+4
                hand = roundz[j]
                print(f"\n\n#{j+1} Runda de {hand}\n{'='*len('runda de xxxx')}")
                # bidding
                print(f'\nPariaza\n{"`"*len("nPariaza")}')
                bid = 0
                _next += 1
                if _next == gamer_num:
                    _next = 0
                order = [x for x in range(_next, gamer_num)] + [x for x in range(0, _next)]
                final_bidder = order[-1]
                for ndx in order:
                    who = group[ndx]
                    bet = prompt_bet(who.nm, ndx, final_bidder, bid, hand)
                    who.bet.append(bet)
                    bid += bet
                # done
                print(f'\nMaini facute\n{"`"*len("Maini facute")}')
                for ndx in order:
                    bidder = group[ndx]
                    condition = f"opt <= {hand}"
                    done = rewind_prompt(bidder.nm, condition)
                    bidder.done.append(done)
                    # winner
                    bet = bidder.bet[-1]
                    # update dict of cells to be colored
                    pending_colorize = parse_point(
                        gamer_num, row, hand, bidder, colorize, pending_colorize)
            next = ''
            format_data(pen, formatting, pending_colorize, group, roundz, gamer_num)
            wb.close()
            if not is_new:
                # dump in memory dataframe to file
                export_dataframe(output, fname, ROUND, 
                    (len(group)*3+66), len(roundz)+3, COLUMN_OFFSET-1)

            while not next.isalpha():
                next = input("\n\nJoc nou? Y \\ N: ")
                next = next.upper()
                if next.upper() not in ['Y', 'N']:
                    continue
                elif next == 'N':
                    exit()
                else:
                    _next = -1
                    ROUND += 1
                    output = io.BytesIO()
                    fname = f'ROUND {ROUND}.xlsx'
                    wb = Workbook(output, {'in_memory': True})
                    pen = wb.add_worksheet(f'ROUND {ROUND}')
                    for uzr in group:
                        for prop in ['total','winz','failz']:
                            setattr(uzr, prop, 0)
                        for prop in ['bet','done','point']:
                            setattr(uzr, prop, [])
                    break
