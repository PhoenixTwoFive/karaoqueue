from flask import Flask, render_template
import helpers
import database
import os, errno
app = Flask(__name__)
@app.route("/")
def home():
    return render_template('index.html', list=database.get_list())

@app.route("/list")
def index():
    list = database.get_list()
    for entry in list:
        print(entry[0])
    return str(database.get_list())

if __name__ == "__main__":
    """try:
        os.remove("test.db")
        print("removed database")
    except OSError:
        print("failed to remove database")
        pass"""
    database.create_entry_table()
    database.create_list_view()
    database.import_songs(helpers.get_songs(helpers.get_catalog_url()))
    app.run(debug=True)
