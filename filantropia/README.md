* Executa in terminal comanda de mai jos pentru instalarea librariilor necesare.
`python3 -m pip install --user requests pypdf selenium`

* Actualizati fisierul `credential.json` cu datele de autentificare.

* Executia scriptului se face astfel, alegand obligatoriu una din optiunile separate de `|` :
`python3 nir.py alimente | materiale | rechizite | inventar | mijloace | constructii | consumabile | meniu`

 !!! In timpul executiei, programul va valida tipul de avize care se doresc a fi importate. Nu executati scriptul avand avize de categorii diferite in acelasi director !!! 

* In acelasi director in care in care se afla scriptul, adaugati doar avizele PDF care apartin aceleiasi categorii din cele mai jos.
Exemplu: aviz de materiale executat ca fiind de alimente, va duce la importarea in cadrul gestiunii de alimente, cu produse aferente materialelor.

* Dupa executia scriptului, stergeti sau mutati PDF-urile din director si faceti loc urmatoarelor avize grupate pe categorii
