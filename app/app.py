# importing modules
from flask import Flask, render_template, request, redirect, flash
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired
import mysql.connector as mysql

class LocationForm(FlaskForm):
    latitude = StringField('Latitude', validators=[DataRequired()])
    longitude = StringField('Longitude', validators=[DataRequired()])
    submit = SubmitField('Enter')


db = mysql.connect(
    host = "localhost",
    user = "root",
    passwd = "WAcodevid2020",
    database = "servers"
)



# declaring app name
app = Flask(__name__)
app.config['SECRET_KEY'] = 'WAcodevid2020'

def getStore(latitude, longitude):

    cursor = db.cursor(buffered=True)
    #SELECT school, student FROM servers.table1 LIMIT 1;
    query = 'SELECT name FROM servers.stores WHERE lat = ' + latitude + ' AND lon = ' + longitude + ';'

    cursor.execute(query)

    #SELECT B from table_name WHERE A = 'a';
    ## 'fetchall()' method fetches all the rows from the last executed statement
    #database = cursor.fetchall() ## it returns a list of all databases present
    data = cursor.fetchall()
    #rcount = len(data)
    store = []
    #print(rcount)
    store = data[0][0]


    return store

@app.route('/location', methods=['GET', 'POST'])
def location():
    form = LocationForm()

    if form.validate_on_submit():
        flash('Latitude requested from user {}, Longitude requested from the user={}'.format(form.latitude.data, form.longitude.data))
        store = getStore(form.latitude.data, form.longitude.data)
        cursor = db.cursor(buffered=True)
        query = "UPDATE servers.found SET foundStore = '" + store + "' WHERE id = 1;"
        cursor.execute(query)
        return redirect('/store')
    else:
        return render_template('location.html', title='Location', form=form)

# defining home page

@app.route('/index', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def homepage():
    return render_template("index.html")


@app.route('/store', methods=['GET', 'POST'])
def stores():
    cursor = db.cursor(buffered=True)

    cursor.execute('SELECT foundStore FROM servers.found;')
    store = cursor.fetchone()
    print(store[0])
    return render_template("store.html", len=1, store=store[0])


if __name__ == '__main__':
    app.run(use_reloader=True, debug=True)
    #getStore('42.54485','-71.47424')

