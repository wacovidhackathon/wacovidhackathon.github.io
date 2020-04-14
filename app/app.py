# importing modules
import time

from flask import Flask, render_template, request, redirect, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, SelectField, RadioField
from wtforms.validators import DataRequired
import mysql.connector as mysql
from datetime import datetime

class LocationForm(FlaskForm):
    latitude = StringField('Latitude', validators=[DataRequired()])
    longitude = StringField('Longitude', validators=[DataRequired()])
    submit = SubmitField('Enter')

class StatusForm(FlaskForm):
    status_option = SelectField('status_option', choices=[('1','Full Stock'), ('2','Majority Remaining'), ('3','Half Remaining'), ('4', 'Few Remaining'), ('5','None Remaining')])
    item_option = SelectField('item_option', choices=[('1', 'Toilet Paper'), ('2', 'Hand Sanitizer')])
    submit = SubmitField('Enter')
class StoreForm(FlaskForm):
    stores = RadioField('stores', choices=[])
    submit = SubmitField('View')
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
    data = cursor.fetchall()
    #rcount = len(data)
    store = []
    #print(rcount)
    store = data[0][0]


    return store

def parseMessage(store, raw_item, raw_rating, raw_date):
    messages = []

    rating_choices = ['Full Stock', 'Majority Remaining', 'Half Remaining', 'Few Remaining','None Remaining']
    item_choices = ['Toilet Paper', 'Hand Sanitizer']
    #colors = {1: '#12e012', 2: '#64d164', 3: '#ebeb21', 4: '#d95050', 5:'#d92525'}
    color_array = []
    for i in range(len(raw_item)):
        '''
        print(raw_date[i])
        print(item_choices[int(raw_item[i][0])])
        print(rating_choices[int(raw_rating[i][0])])
        print(store)
        '''
        new_message = '' + raw_date[i][0] + ' Status of ' + item_choices[int(raw_item[i][0])-1] + ' at ' + store + ': ' + rating_choices[int(raw_rating[i][0])-1]
        messages.append(new_message)
        color_array.append(int(raw_rating[i][0]))
    return messages, color_array

@app.route('/location', methods=['GET', 'POST'])
def location():
    form = LocationForm()
    cursor = db.cursor(buffered=True)
    query = "DELETE FROM servers.found;"
    cursor.execute(query)
    if form.validate_on_submit():
        flash('Latitude requested from user {}, Longitude requested from the user={}'.format(form.latitude.data, form.longitude.data))
        stores = []
        stores.append(getStore(form.latitude.data, form.longitude.data))
        session['stores'] = stores

        #note that the iD is on autoincrement
        #when have all stores have a for loop here and change the getStore method

        return redirect('/store')
    else:
        return render_template('location.html', title='Location', form=form)


@app.route('/store', methods=['GET', 'POST'])
def stores():
    cursor = db.cursor(buffered=True)

    form = StoreForm()
    if request.method == 'POST':
        flash('Status requested from the user {}'.format(form.stores.data))

        session['selected_store'] = session.get('stores')[int(form.stores.data)]
        return redirect('/status')

    for i in range(len(session.get('stores'))):
        form.stores.choices.append((str(i), session.get('stores')[i]))

    return render_template("store.html", len=len(form.stores.choices), form=form)


@app.route('/status', methods=['GET', 'POST'])
def status():
    status_form = StatusForm()
    cursor = db.cursor(buffered=True)

    if request.method == 'POST':
        flash('Status requested from the user {}'.format(status_form.status_option.data))
        flash('Status requested from the user {}'.format(status_form.item_option.data))
        now = datetime.now()
        date_now = now.strftime("%m/%d/%Y %H:%M:%S")
        #add manager
        query = "INSERT INTO servers.status_list(date, item, rating, manager, store) VALUES('" + date_now + "'," + status_form.item_option.data +  "," + status_form.status_option.data +", 0, '" + session['selected_store'] +"');"
        cursor.execute(query)
        cursor.execute("COMMIT;")
        time.sleep(0.5)
        return redirect('/status')

    get_query = "SELECT * FROM servers.status_list WHERE store = '" + session['selected_store'] + "';"
    cursor.execute(get_query)
    print(cursor.fetchall())

    get_query = "SELECT item FROM servers.status_list WHERE store = '" + session['selected_store'] + "';"
    cursor.execute(get_query)
    raw_item = cursor.fetchall()
    print(raw_item)

    get_query = "SELECT rating FROM servers.status_list WHERE store = '" + session['selected_store'] + "';"
    cursor.execute(get_query)
    raw_rating = cursor.fetchall()

    get_query = "SELECT date FROM servers.status_list WHERE store = '" + session['selected_store'] + "';"
    cursor.execute(get_query)
    raw_date = cursor.fetchall()

    messages, colors = parseMessage(session['selected_store'],raw_item, raw_rating, raw_date)


    return render_template("status.html", store = session['selected_store'],  form = status_form, messages = messages, len = len(messages), colors = colors)

@app.route('/index', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def homepage():
    return render_template("index.html")




if __name__ == '__main__':
    app.run(use_reloader=True, debug=True)

