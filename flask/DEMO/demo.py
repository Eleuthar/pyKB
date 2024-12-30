# export FLASK_APP=demo.py

from core import qpp

if __name__=="__main__":
    qpp.run(debug=True, use_reloader=True)