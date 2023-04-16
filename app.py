from flask import Flask, send_file
import pandas as pd
import tempfile
import getpass
from sqlalchemy import create_engine

app = Flask(__name__)

user = getpass.getuser()
connection_string = f"postgresql+psycopg2://{user}:@localhost:5433/{user}"
engine = create_engine(connection_string)

@app.route('/download/<book_id>')
def get_book_stats(book_id):
    data = pd.read_sql(f'SELECT * from public."Borrows" WHERE book_id={book_id}', con = engine)
    data.drop('user_id', axis=1, inplace=True)

    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        
        writer = pd.ExcelWriter(tmp.name, engine="xlsxwriter", datetime_format="mmm d yyyy hh:mm:ss", date_format="mmmm dd yyyy")
        data.to_excel(writer, sheet_name="Sheet1")
        writer.close()

    return send_file(tmp.name, as_attachment=True, download_name=f'{book_id}_stats.xlsx')
    
