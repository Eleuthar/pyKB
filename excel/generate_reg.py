from xlsxwriter import Workbook
from datetime import datetime, timedelta
from os import listdir
from collections import namedtuple


def get_prod():    
    year = None
    inventory = {}
    nr = 10
    begin_chr = ord('D')
    pth = ''
    for txt in listdir():
        if txt.endswith('.txt'):
            pth = txt
            break
    with open(pth) as txt:
        year = txt.readline().strip()
        for prod in txt.readlines():
            if '=' in prod:
                product, price = prod.split('=')
                price = price.strip()
                # remove thousand separator
                price = price.split('.')
                price = ''.join(price)
                # handle decimal separator conflict
                price = price.replace(',','.')
                product = product.strip()
                inventory[nr] = {
                    'prod': product, 
                    '$': float(price),
                    'chr': chr(begin_chr)
                }
                nr += 1
                begin_chr += 1
    return year, inventory


def get_week_dates(start_date, end_date):
    ''' start_date = "2025-JAN-01"  end_date = "2025-DEC-31" '''
    # Ensure dates are in datetime format
    # Month as text (e.g., "NOV")
    start_date = datetime.strptime(start_date, "%Y-%b-%d") 
    end_date = datetime.strptime(end_date, "%Y-%b-%d")
    
    # Adjust start_date to the nearest Monday if it isn't already
    if start_date.weekday() != 0:
        start_date += timedelta(days=(0 - start_date.weekday()) % 7)
    
    # Generate all Mondays between start_date and end_date
    week_dates = []
    current_date = start_date
    while current_date <= end_date:
        week_dates.append(current_date.strftime("%Y-%b-%d").upper())  # Format with uppercase month
        current_date += timedelta(days=7)
    
    # '2025-JAN-06' to '6 IAN', etc
    for j in range(len(week_dates)):
        y, month, day = week_dates[j].split('-')
        day = day.lstrip('0')
        for letter in ['J', 'Y']:
            if letter in month:
                month = month.replace(letter, 'I')
                break
        week_dates[j] = ' '.join([day, month])

    return week_dates


def enrich_mapping(month_mapping, week_dates):
    wb_ndx = 0
    for month in month_mapping:
        wk = week_dates[wb_ndx]
        begin = wk
        while month in wk:
            month_mapping[month]['wkz'].append(wk)
            wb_ndx += 1
            try:
                wk = week_dates[wb_ndx]
            except:
                break
        # update range value
        end = month_mapping[month]['wkz'][-1]
        month_mapping[month]['range'] = f'{begin}:{end}'
    # handle December, having no next month to trigger else condition
    begin = month_mapping[month]['wkz'][0]
    end = month_mapping[month]['wkz'][-1]
    month_mapping[month]['range'] = f'{begin}:{end}'


def generate_monthly_report_formula(month_mapping, month, prod_row):

    # =('1 IAN'!E10 * '1 IAN'!B10) + ('8 IAN'!E10 * '8 IAN'!B10) + ...
    amount_in = '='
    for wk in month_mapping[month]['wkz']:
        amount_in += f"('{wk}'!E{prod_row} * '{wk}'!B{prod_row}) + "
    amount_in = amount_in.rstrip(' + ')
    wk_range = month_mapping[month]['range']
    end_wk = month_mapping[month]['wkz'][-1]

    # =SUM('1 IAN:29 IAN'!B10)
    quant_in = f"=SUM('{wk_range}'!{'B'}{prod_row})"
    quant_out = f"=SUM('{wk_range}'!{'G'}{prod_row})"
    amount_out = f"=SUM('{wk_range}'!{'H'}{prod_row})"

    # stock is using the last sheet from month_mapping['range']
    quant_stock = f"='{end_wk}'!{'I'}{prod_row}"
    amount_stock = f"='{end_wk}'!{'J'}{prod_row}"
    return [quant_in, amount_in, quant_out, amount_out, quant_stock, amount_stock]
    


def generate_report_grid(pen, formatter, month_mapping, prod):

    # formula aggregator for general totals
    quant_in_month_row = []
    amount_in_month_row = []
    quant_out_month_row = []
    amount_out_month_row = []

    pen.set_column('A:A', 10)
    pen.set_row(6, 23)
    pen.merge_range('E1:G3', 'RAPORT GENERAL 2024\r\nPAROHIA DOMUS - VOLUNTARI', formatter.title)
    pen.merge_range('A6:C6', 'Stoc anterior', formatter.head)

    # product names on row 5, starting on col D == 68
    for prod_row in prod:
        prod_chr = prod[prod_row]['chr']
        name = prod[prod_row]['prod']
        pen.set_column(f"{prod_chr}:{prod_chr}", len(name)+4)
        pen.write(f"{prod_chr}5", name, formatter.head)

    # A:A
    row = 1
    for month in month_mapping:
        row += 6
        end = row+5

        quant_in_month_row.append(row)
        amount_in_month_row.append(row+1)
        quant_out_month_row.append(row+2)
        amount_out_month_row.append(row+3)
        
        pen.merge_range(f'A{row}:A{end}', month, formatter.head)
        # B:B 
        pen.merge_range(f'B{row}:B{row+1}', 'Intrare', formatter.regular)
        pen.merge_range(f'B{row+2}:B{row+3}', 'Iesire', formatter.regular)
        pen.merge_range(f'B{row+4}:B{row+5}', 'Stoc', formatter.regular)
        # C:C 
        # cantitate \ total per B parent item
        for z in range(0,6,2):
            quant_row = row+z
            amount_row = row+z+1
            pen.write(f'C{quant_row}', 'Cantitate', formatter.regular)
            pen.write(f'C{amount_row}', 'Total', formatter.regular)
            pen.set_row(quant_row, 23)
            pen.set_row(amount_row, 23)

        # build formula for each type
        for prod_ndx in prod:
            prod_chr = prod[prod_ndx]['chr']
            [
                quant_in,
                amount_in,
                quant_out,
                amount_out,
                quant_stock,
                amount_stock
            ] = generate_monthly_report_formula(month_mapping, month, prod_row)

            pen.write(f'{prod_chr}{row}', quant_in, formatter.regular)
            pen.write(f'{prod_chr}{row+1}', amount_in, formatter.price)
            pen.write(f'{prod_chr}{row+2}', quant_out, formatter.regular)
            pen.write(f'{prod_chr}{row+3}', amount_out, formatter.price)
            pen.write(f'{prod_chr}{row+4}', quant_stock, formatter.regular)
            pen.write(f'{prod_chr}{row+5}', amount_stock, formatter.price)

    pen.merge_range('A80:A83', 'TOTAL GENERAL', formatter.head)
    pen.merge_range(f'B80:B81', 'Intrare', formatter.regular)
    pen.merge_range(f'B82:B83', 'Iesire', formatter.regular)
    for row in [80,82]:
        pen.write(f'C{row}', 'Cantitate', formatter.regular)
        pen.write(f'C{row+1}', 'Total', formatter.regular)
        pen.set_row(row, 23)
        pen.set_row(row+1, 23)

    for prod_ndx in prod:
        prod_chr = prod[prod_ndx]['chr'] 
        range_quant_in = [f'{prod_chr}{x}' for x in quant_in_month_row]
        range_amount_in = [f'{prod_chr}{x}' for x in amount_in_month_row]
        range_quant_out = [f'{prod_chr}{x}' for x in quant_out_month_row]
        range_amount_out = [f'{prod_chr}{x}' for x in amount_out_month_row]
        for pair in (
            (80, range_quant_in),
            (82, range_quant_out)
        ):
            pen.write(f'{prod_chr}{pair[0]}', "=SUM(" + ', '.join(pair[1]) + ")", formatter.regular)
            
        for pair in (
            (81, range_amount_in),
            (83, range_amount_out)
        ):
            pen.write(f'{prod_chr}{pair[0]}', "=SUM(" + ', '.join(pair[1]) + ")", formatter.price)


def generate_week_registry(
        pen, prev, report_title, prod, formatter, year, stock_row, first_sheet=False
    ):
    pen.set_column('A:A', 18)
    pen.set_column('E:E', 11)
    pen.set_column('G:G', 11)
    pen.set_column('I:I', 12)
    # NR CRT row 9
    crt = 1
    for j in range(ord('A'), ord('K')):
        pen.write(f'{chr(j)}9', crt, formatter.regular)
        crt += 1

    pen.set_row(9, 23)
    pen.merge_range('A1:C3', 'PAROHIA DOMUS – VOLUNTARI\r\nREGISTRU LUMANARI', formatter.title)
    merger = {
        'A5:A8': 'TIP PRODUS',
        'B5:F5': 'INTRARI',
        'G5:H5': 'IESIRI',
        'I5:J5': 'STOCURI',
        'B6:C7': 'Cantitate',
        'D6:D8': "U.M.",
        'G6:G8': "Cantitate"
    }
    for coord, txt in merger.items():
        pen.merge_range(coord, txt, formatter.head)
    
    headers = {
        'B8': 'Adaugat',
        'C8': 'Anterior',
        'E6': 'Pret unitar',
        'F6': "Valoare totala",
        'F7': "col.4 x (col.1+2)",
        'H6': "Valoare totala",
        'H7': "col.4 x col.6",
        'I6': "Cantitate",
        'I7': "col.(1+2)-col.6",
        'J6' : "Valoare",
        'J7': "col.4 x col.8)",
    }
    for coord, txt in headers.items():
        pen.write(coord, txt, formatter.head)

    for ron in ['E8','F8','H8','J8']:
        pen.write(ron, "~ LEI ~", formatter.head)

    # sheet[1] col C exception
    # weekly sheet formulas
    pen.merge_range('E2:G2', f'DATA: {pen.name} {year}', formatter.title)
    for prod_row in prod:
        pen.set_row(prod_row+1, 21)
        A = f'A{prod_row}'
        B = f'B{prod_row}'
        C = f'C{prod_row}'
        D = f'D{prod_row}'
        E = f'E{prod_row}'
        G = f'G{prod_row}'
        I = f'I{prod_row}'
        F = f'F{prod_row}'
        H = f'H{prod_row}'
        I = f'I{prod_row}'
        J = f'J{prod_row}'
        # PRODUCT NAME
        rep_chr = prod[prod_row]['chr']
        pen.write(A, f"=='{report_title}'!{rep_chr}{stock_row-1}", formatter.head)
        # NIR
        pen.write(B, 0, formatter.regular)
        # previous stock
        pen.write(C, f"=='{prev}'!I{prod_row}", formatter.regular)
        # unit measure 
        pen.write(D, f"=='{prev}'!D{prod_row}", formatter.regular)
        # unit price
        pen.write(E, f"='{prev}'!E{prod_row}", formatter.price)
        # quantity and amount
        pen.write(F, f"={E} *({B} + {C})", formatter.price)
        pen.write(H, f"={G} * {E}", formatter.price)
        pen.write(I, f"=({B} + {C}) - {G}", formatter.regular)
        pen.write(J, f"={I} * {E}", formatter.price)
    BEGIN_ROW = 10
    END_ROW = prod_row
    TOTAL_ROW = prod_row+1
    # weekly totals used by general report
    # prod_row is the value from the above iteration of products
    pen.write(f'A{TOTAL_ROW}', "TOTAL", formatter.head)
    for col in ['B','C','D','E','G','I']:
        # empty row 9 & total
        pen.write(f'{col}9', "", formatter.regular)
        pen.write(f'{col}{TOTAL_ROW}', "", formatter.regular)
        
    for z in ['F','H','J']:
        pen.write(
           f'{z}{TOTAL_ROW}', 
           f'=SUM({z}{BEGIN_ROW}:{z}{END_ROW})', 
           formatter.price
        )
    # initial stock
    # set first week sheet BEGIN_ROW-END_ROW as GENERAL REPORT INITIAL STOCK ROW
    if first_sheet:
        rep_title = f'Raport general {year}'
        rep_ord = ord('C')
        for row in prod:
            C = f'C{row}'
            D = f'D{row}'
            E = f'E{row}'
            rep_chr = prod[row]['chr']
            pen.write(C, f"=='{rep_title}'!{rep_chr}{stock_row}", formatter.head)
            pen.write(D, "buc.", formatter.regular)
            pen.write(E, prod[row]['$'], formatter.price)


if __name__ == '__main__':

    month_mapping = {
        'IAN': { 'row': 7, 'range': '', 'wkz': [] },
        'FEB': { 'row': 13, 'range': '', 'wkz': [] },
        'MAR': { 'row': 19, 'range': '', 'wkz': [] },
        'APR': { 'row': 25, 'range': '', 'wkz': [] },
        'MAI': { 'row': 31, 'range': '', 'wkz': [] },
        'IUN': { 'row': 37, 'range': '', 'wkz': [] },
        'IUL': { 'row': 43, 'range': '', 'wkz': [] },
        'AUG': { 'row': 49, 'range': '', 'wkz': [] },
        'SEP': { 'row': 55, 'range': '', 'wkz': [] },
        'OCT': { 'row': 61, 'range': '', 'wkz': [] },
        'NOV': { 'row': 67, 'range': '', 'wkz': [] },
        'DEC': { 'row': 73, 'range': '', 'wkz': [] }
    }

    year, prod = get_prod()
    workbook = Workbook(f'Registru Parohia DOMUS {year}.xlsx')
    Formatter = namedtuple('Formatter', ('title', 'head', 'regular', 'price'))

    regular = workbook.add_format({
        "font_name": "Bahnschrift",
        "font_size": 10,
        "align": "center",
        "valign": "vcenter",
        "border": 1
    })
    title = workbook.add_format({
        "font_name": "Bahnschrift",
        "font_size": 11,
        "bold": True,
        "align": "center",
        "valign": "vcenter",
        'text_wrap': True
    })
    head = workbook.add_format({
        "font_name": "Bahnschrift",
        "font_size": 11,
        "bold": True,
        "align": "center",
        "valign": "vcenter",
        "border": 1,
        'text_wrap': True
    })
    price = workbook.add_format({
        "font_name": "Bahnschrift",
        "font_size": 10,
        'num_format': '0.00',
        "align": "center",
        "valign": "vcenter",
        "border": 1
    })

    formatter = Formatter(title, head, regular, price)
    wkz = get_week_dates(f"{year}-JAN-01", f"{year}-DEC-31")
    enrich_mapping(month_mapping, wkz)
    report_title = f'Raport general {year}'
    pen = workbook.add_worksheet(report_title)
    generate_report_grid(pen, formatter, month_mapping, prod)
    # first weekly sheet
    pen = workbook.add_worksheet(wkz[0])
    generate_week_registry(
        pen, report_title, report_title, prod, formatter, year, 6, first_sheet=True
    )
    for x in range(1, len(wkz)):
        wk = wkz[x]
        prev = wkz[x-1]
        pen = workbook.add_worksheet(wk)
        generate_week_registry(pen, prev, report_title, prod, formatter, year, 6)
    workbook.close()