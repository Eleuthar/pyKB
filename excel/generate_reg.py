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
                product, price = prod.strip().split('=')
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
        for wk in week_dates:
            if month in wk:
                month_mapping[month]['wkz'].append(wk)
                wb_ndx += 1
            else:
                # update range value
                begin = month_mapping[month]['wkz'][0]
                end = month_mapping[month]['wkz'][-1]
                month_mapping[month]['range'] = f'{begin}:{end}'
                break
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

    pen.merge_range('E2:G3', 'RAPORT GENERAL 2024\nPAROHIA DOMUS - VOLUNTARI', formatter.title)
    pen.merge_range('A6:C6', 'Stoc anterior', formatter.head)

    row = 7
    # product names on row 6, starting on col D == 68
    for prod_row in prod:
        prod_chr = prod[prod_row]['chr']
        pen.write(f"{prod_chr}6" , prod[prod_row]['prod'], formatter.head)
    # A:A     
    for month in month_mapping():
        end = row+6
        pen.merge_range(f'A{row}:A{end}', month, formatter.head)
        # B:B 
        pen.merge_range(f'B{row}:B{row+1}', 'Intrare', formatter.regular)
        pen.merge_range(f'B{row+2}:B{row+3}', 'Iesire', formatter.regular)
        pen.merge_range(f'B{row+4}:B{row+5}', 'Stoc', formatter.regular)
        # C:C 
        # cantitate \ total per B parent item
        for z in range(3):
            quant_row = row+z
            amount_row = row+z+1
            pen.write(f'C{quant_row}', 'Cantitate', formatter.regular)
            pen.write(f'C{amount_row}', 'Total', formatter.regular)
         
        quant_in_month_row.append(row)
        amount_in_month_row.append(row+1)
        quant_out_month_row.append(row+2)
        amount_out_month_row.append(row+3)

        pen.write(f'{prod_chr}{row}', quant_in, formatter.regular)
        pen.write(f'{prod_chr}{row+1}', amount_in, formatter.regular)
        pen.write(f'{prod_chr}{row+2}', quant_out, formatter.regular)
        pen.write(f'{prod_chr}{row+3}', amount_out, formatter.regular)
        pen.write(f'{prod_chr}{row+4}', quant_stock, formatter.regular)
        pen.write(f'{prod_chr}{row+5}', amount_stock, formatter.regular)
        [
            quant_in,
            amount_in,
            quant_out,
            amount_out,
            quant_stock,
            amount_stock
        ] = generate_monthly_report_formula(month_mapping, month, prod_row)
        row += 6
        
    for prod_ndx in prod:
        prod_chr = prod[prod_ndx]['chr'] 
        range_quant_in = [f'{prod_chr}{x}' for x in quant_in_month_row]
        range_amount_in = [f'{prod_chr}{x}' for x in amount_in_month_row]
        range_quant_out = [f'{prod_chr}{x}' for x in quant_out_month_row]
        range_amount_out = [f'{prod_chr}{x}' for x in amount_out_month_row]
        for pair in (
            (81, range_quant_in),
            (82, range_amount_in),
            (83, range_quant_out),
            (84, range_amount_out)
        ):
            pen.write(
                f'{prod_chr}{pair[0]}', 
                "=SUM(" + ', '.join(pair[1]) + ")",
                formatter.regular
            )

def generate_week_registry(pen, prev, prod, formatter, year, stock_row=None):
    # sheet[1] col C exception
    # weekly sheet formulas
    pen.write('F2', f'DATA: {pen.title} {year}', formatter.title)
    for prod_row in prod:
        B = f'B{prod_row}'
        C = f'C{prod_row}'
        E = f'E{prod_row}'
        G = f'G{prod_row}'
        I = f'I{prod_row}'
        F = f'F{prod_row}'
        H = f'H{prod_row}'
        I = f'I{prod_row}'
        J = f'J{prod_row}'
        # previous stock
        pen.write(C, f"=='{prev}'!I{prod_row}", formatter.regular)
        # unit price
        pen.write(E, f"='{prev}'!E{prod_row}", formatter.regular)
        # quantity and amount
        pen.write(F, f"={E} *({B} + {C})", formatter.regular)
        pen.write(H, f"={G} * {E}", formatter.regular)
        pen.write(I, f"=({B} + {C}) - {G}", formatter.regular)
        pen.write(J, f"={I} * {E}", formatter.regular)
    BEGIN_ROW = 10
    END_ROW = prod_row
    TOTAL_ROW = prod_row+1
    # weekly totals used by general report
    # prod_row is the value from the above iteration of products
    for z in ['F','H','J']:
        pen.write(
           f'{z}{TOTAL_ROW}', 
           f'=SUM({z}{BEGIN_ROW}:{z}{END_ROW})', 
           formatter.regular
        )
    # initial stock
    # set first week sheet BEGIN_ROW-END_ROW as GENERAL REPORT INITIAL STOCK ROW
    if stock_row is not None:
        rep_title = f'Raport general {year}'
        rep_ord = ord('C')
        for row in prod:
            C = f'C{row}'
            rep_chr = prod[row]['chr']
            pen.write(C, f"=='{rep_title}'!{rep_chr}{stock_row}", formatter.head)


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
        'SEPT': { 'row': 55, 'range': '', 'wkz': [] },
        'OCT': { 'row': 61, 'range': '', 'wkz': [] },
        'NOV': { 'row': 67, 'range': '', 'wkz': [] },
        'DEC': { 'row': 73, 'range': '', 'wkz': [] }
    }

    year, prod = get_prod()
    workbook = Workbook(f'Registru Parohia DOMUS {year}.xlsx')
    Formatter = namedtuple('Formatter', ('title', 'head', 'regular'))

    regular = workbook.add_format({
        "font_name": "Calibri",
        "font_size": 12,
        "align": "center",
        "valign": "vcenter",
        "border": 1
    })

    title = workbook.add_format({
        "font_name": "Bahnschrift",
        "font_size": 14,
        "font_weight": "bold",
        "align": "center",
        "valign": "vcenter",
    })

    head = workbook.add_format({
        "font_name": "Calibri",
        "font_size": 13,
        "font_weight": "bold",
        "align": "center",
        "valign": "vcenter",
        "border": 2
    })

    formatter = Formatter(title, head, regular)
    wkz = get_week_dates(f"{year}-JAN-01", "{year}-DEC-31")
    enrich_mapping(month_mapping, wkz)
    pen = workbook.add_worksheet(f'Raport general {year}')
    report_title = pen.title
    generate_report_grid(pen, formatter, month_mapping, prod)
    # first weekly sheet
    pen = workbook.add_worksheet(wkz[0])
    generate_week_registry(pen, report_title, prod, formatter, year, stock_row=6)
    for wk in wkz:
        prev = pen.title
        pen = workbook.add_worksheet(wkz)
        generate_week_registry(pen, prev, prod, formatter, year)