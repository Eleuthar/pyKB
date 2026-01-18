from wzt import group_count, join_players, hand_num, next_fight, env, COLUMN_OFFSET, BEGIN_ROUND_ROW, parse_point, colorize, format_data, Member
from xlsxwriter import Workbook
import json
import io


# first column dedicated for game count
output = io.BytesIO()
group = [
    Member(nm='P1', bet_char='D', done_char='E', point_char='F',
        bet=[1, 1, 2, 3, 4, 5, 2, 2, 4, 2, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1],
        done=[1, 1, 2, 3, 4, 5, 2, 3, 5, 1, 7, 7, 7, 6, 5, 4, 3, 2, 1, 1],
        point=[], report=[], total=0
    ),
    Member(nm='P2', bet_char='G', done_char='H', point_char='I',
        bet= [1, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1],
        done=[1, 1, 2, 3, 4, 5, 5, 4, 3, 2, 1, 8, 7, 6, 5, 4, 3, 2, 1, 1],
        point=[], report=[], total=0
    ),
    # Member(nm='P3', bet_char='J', done_char='K', point_char='L',
    #     bet=[1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1],
    #     done=[1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1],
    #     point=[],
    #     report=[], total=0),
    # Member(nm='P4', bet_char='M', done_char='N', point_char='O',
    #     bet=[1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1],
    #     done=[1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1],
    #     point=[],
    #     report=[], total=0)
    ]
gamer_num = len(group)
roundz = hand_num(gamer_num)
pending_colorize = {}
# find previous score workbooks in game directory
fname, ROUND = next_fight()
wb = Workbook(fname)
pen = wb.add_worksheet(f'ROUND {ROUND}')

formatting = {}
for bg in ['header','total','stat','bet','done','point','green_point','red_point']:
    formatting[bg] = wb.add_format(env['formatting'][bg])

for game in range(len(roundz)):
    for bidder in group:
        hand = roundz[game]
        pending_colorize = parse_point(
            gamer_num, game, hand, bidder, colorize, pending_colorize
        )
        print(pending_colorize)
format_data(pen, formatting, pending_colorize, group, roundz, gamer_num)
wb.close()

