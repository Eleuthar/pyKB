from os import listdir
import sys
import requests as rq
import json
from pypdf import PdfReader
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


rq.urllib3.disable_warnings()


def read_pdf(pdf_name):
    """ """
    rdr = PdfReader(pdf_name)
    fpage = rdr.pages[0].extract_text()
    # prevent bad parsing due to corupted pdf
    fpage = fpage.replace("custom_\n\n", " kg ").split("\n")
    end_fpage = len(fpage)
    # determine supplier
    for ndx in range(end_fpage):
        txt = fpage[ndx]
        if txt.upper().strip() == "DONOR":
            begin_furnizor = ndx + 1
            break
    # previous index is last supplier element
    for ndx in range(begin_furnizor, end_fpage):
        txt = fpage[ndx]
        if txt.startswith("CIF"):
            end_furnizor = ndx
            break
    # end determine supplier
    data = {
        "supplier": " ".join(fpage[begin_furnizor:end_furnizor]),
        "date_created": fpage[1].split()[5].replace("/", "."),
        "document_number": fpage[1].split()[3],
        "grand_total": 0.00,
        "save": "save",
    }
    start_content = None
    # determine content start
    for ndx in range(end_furnizor, end_fpage):
        if fpage[ndx].endswith("Total kg"):
            start_content = ndx + 1
            break
    if start_content is None:
        print("No `total kg` found")
        sys.exit()
    row = 0

    # mark end of last page content
    done = False
    for page in rdr.pages:
        content = page.extract_text()
        # prevent bad parsing due to corupted pdf
        content = content.replace("custom_\npiece\n", " kg ").split("\n")
        for txt in content[start_content:]:
            if txt.startswith("Total aviz"):
                done = True
                break
            txt = txt.split()
            val = float(txt[-2])
            data["grand_total"] += val
            price = txt[-3]
            quant = txt[-4]
            prod = txt[-6:0:-1]
            prod.reverse()
            prod = " ".join(prod)
            row += 1
            #  PARAM materiale curatenie
            data[f"items[{row}][product]"] = prod
            data[f"items[{row}][number_of_calories]"] = ""
            data[f"items[{row}][quantity]"] = quant
            data[f"items[{row}][price]"] = price
            data[f"items[{row}][subtotal]"] = val
        if done:
            break
        start_content = 0
    return data


def new_cookie(uzr, pvd):
    """
    payload = {
        "supplier": "ADMIN DEMO",
        "date_created": "18.03.2026",
        "document_number": "888",
        "grand_total": 286.06,
        "save": "save",
        "items[1][product]": "*HB PIEPT PORC CU OS FEL.750G",
        "items[1][number_of_calories]": "",
        "items[1][quantity]": "5",
        "items[1][price]": "22.45",
        "items[1][subtotal]": 112.25,
        "items[2][product]": "*SUPORTERO MICI PORC-VITA 700G",
        "items[2][number_of_calories]": "",
        "items[2][quantity]": "5",
        "items[2][price]": "16.29",
        "items[2][subtotal]": 81.45,
        "items[3][product]": "*HB COTLET PORC FARA OS FEL.650G",
        "items[3][number_of_calories]": "",
        "items[3][quantity]": "4",
        "items[3][price]": "23.09",
        "items[3][subtotal]": 92.36,
    }
    """
    auth_uri = "https://gestiune.filantropiahusi.ro/utilizatori/autentificare"
    driver = webdriver.Firefox()
    driver.get(auth_uri)
    uzr_field = driver.find_element(By.ID, "login")
    pvd_field = driver.find_element(By.ID, "password")
    uzr_field.send_keys(uzr)
    pvd_field.send_keys(pvd)
    pvd_field.send_keys(Keys.RETURN)
    cookie = f"ci_session={driver.get_cookies()[0]['value']}"
    return {"Cookie": cookie}


optz = [
    "alimente",
    "materiale",
    "rechizite",
    "inventar",
    "mijloace",
    "constructii",
    "consumabile",
    "meniu",
]
mapping = {
    "alimente": 1,
    "materiale": 2,
    "rechizite": 3,
    "inventar": 4,
    "mijloace": 5,
    "constructii": 6,
    "consumabile": 7,
    "meniu": 8,
}

if __name__ == "__main__":
    opt = sys.argv[1]
    joined_optz = {", ".join(optz)}
    while opt not in optz:
        print(f"Optiune invalida, alegeti dintre: {joined_optz}")
        sys.exit()

    with open("credential.json", encoding="UTF-8") as auth:
        credential = json.load(auth)
        uzr = credential["login"]
        pvd = credential["parola"]
    HEADER = new_cookie(uzr, pvd)

    for pdf in listdir():
        if pdf.endswith("pdf"):
            payload = read_pdf(pdf)
            qid = mapping[opt]
            URI = f"https://gestiune.filantropiahusi.ro/admin/gestiune/tip/{qid}/adaugare-intrare"
            rq.post(URI, headers=HEADER, data=payload, verify=False, timeout=10)
