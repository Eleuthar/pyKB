group = [
    Member(nm='ela', bet_char='D', done_char='E', point_char='F',
        bet = [1, 1, 1, 1, 2, 3, 4, 5, 1, 2, 4, 2, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1],
        done= [1, 1, 1, 1, 2, 3, 4, 5, 2, 3, 5, 1, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1],
        point=[1, 1, 1, 1, 2, 3, 4, 5, -1, -1, -1, -1, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1],
        winz=0, failz=0, total=0
    ),
    Member(nm='geo', bet_char='G', done_char='H', point_char='I',
        bet = [1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1],
        done =[1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1],
        point=[1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1],
        winz=0, failz=0, total=0),
    Member(nm='flo', bet_char='J', done_char='K', point_char='L',
        bet = [1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1],
        done =[1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1],
        point=[1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1],
        winz=0, failz=0, total=0),
    Member(nm='cip', bet_char='M', done_char='N', point_char='O',
        bet = [1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1],
        done= [1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1],
        point=[1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1],
        winz=0, failz=0, total=0)
]

# <<<<<<<<<<<<<<<  TZT
# pending_colorize = {
#     'F12':'red_','F13':'red_','F14':'red_','F15':'red_',
#     'I11':'green_','I12':'green_','I13':'green_','I14':'green_',
# } 
# format_data(pen, formatting, pending_colorize, group, roundz, gamer_num)  
# wb.close() 
# if not is_new:
#     export_dataframe(output, fname, ROUND, 
#         (len(group)*3+COLUMN_OFFSET), len(roundz)+3, COLUMN_OFFSET-1)
# <<<<<<<<<<<<<<<  TZT