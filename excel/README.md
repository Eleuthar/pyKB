Instructiuni utilizare script pt registru PANGAR
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Deschideti terminal din directorul scriptului in aceeasi locatie cu tabelul Excel

* Dupa prima copiere in calculator a programului executati comanda de mai jos, in rest, de la randul 9
> pip install -r requirement.txt

* La fiecare executie, rulati comenzile de mai jos in terminal
> vnv\Scripts\activate
> python REG.py REG.xlsx


* Urmati instructiunile ilustrate pt configurarea zecimalelor separate de virgula si separatorul de mii cu punct.

* Atentie la instructiunile interactive din script


Observatii
``````````
* 7 ian
    \\ Intrare eronata `candele tip 0` 220 vs 240
    \\ Intrare eronata `candele tip 4` 34 vs 36

for x in range(10,17):
    for q in ('E','F','H','J'):
        tgt = frame[f'{q}{x}']
        if tgt.value is not None and isinstance(tgt.value, str):
            tgt.data_type='n'
            tgt.number_format='#,##0.00'
            tgt.value = float(tgt.value.replace(',','.'))