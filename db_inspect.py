import sqlite3
from app import app
import os

with app.app_context():
    uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    print('Using DB URI:', uri)
    if uri and uri.startswith('sqlite:///'):
        path = uri.replace('sqlite:///', '')
    else:
        path = os.path.join(os.path.dirname(__file__), 'kopernikpizza.db')

    print('DB path:', path)
    con = sqlite3.connect(path)
    cur = con.cursor()
    tables = ['pizzas','ingredients','customers','delivery_persons','delivery_zones','order_items','orders','discount_codes']
    for t in tables:
        try:
            cur.execute(f'SELECT count(*) FROM {t}')
            print(f'{t}:', cur.fetchone()[0])
        except Exception as e:
            print(f'{t}: error -', e)
    con.close()
