# importing modules
import time

#import sshtunnel as sshtunnel

import tomtomSearch
from flask_bootstrap import Bootstrap
from flask import Flask, render_template, request, redirect, flash, session, jsonify, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, SelectField, RadioField
from wtforms.validators import DataRequired
#import mysql.connector as mysql
from datetime import datetime
from flaskext.mysql import MySQL

'''
TODO:
-add so user can input address as well
- fix the full page 2 columns
- add information about the store
- integrate the user
- authenticate the managers
'''


class LocationForm(FlaskForm):
    address = StringField('Address', validators=[DataRequired()])
    item_option = SelectField('item_option', choices=[('1', 'Toilet Paper'), ('2', 'Hand Sanitizer')])
    submit = SubmitField('Enter')

class StatusForm(FlaskForm):
    status_option = SelectField('status_option',
                                choices=[('1', 'Full Stock'), ('2', 'Majority Remaining'), ('3', 'Half Remaining'),
                                         ('4', 'Few Remaining'), ('5', 'None Remaining')])
    item_option = SelectField('item_option', choices=[('1', 'Toilet Paper'), ('2', 'Hand Sanitizer')])
    submit = SubmitField('Enter')


class StoreForm(FlaskForm):
    stores = RadioField('stores', choices=[])
    submit = SubmitField('View')








# declaring app name
app = Flask(__name__)
#Bootstrap(app)
app.config['SECRET_KEY'] = 'WAcodevid2020'

mysql = MySQL()

  # MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'WestfordCodevid1'
app.config['MYSQL_DATABASE_PASSWORD'] = 'WAcodevid2020'
app.config['MYSQL_DATABASE_DB'] = 'WestfordCodevid1$codevid'
app.config['MYSQL_DATABASE_HOST'] = 'WestfordCodevid123.mysql.pythonanywhere-services.com'
mysql.init_app(app)



def getStore(latitude, longitude): # get stores from coordinates
    db = mysql.connect()
    cursor = db.cursor()
    # SELECT school, student FROM table1 LIMIT 1;
    store = []
    ids = []
    addresses = []
    for i in range(len(latitude)):

        query = 'SELECT name FROM all_stores WHERE lat = ' + str(latitude[i]) + ' AND lon = ' + str(
            longitude[i]) + ';'

        cursor.execute(query)
        data_store = cursor.fetchall()

        query = 'SELECT id FROM all_stores WHERE lat = ' + str(latitude[i]) + ' AND lon = ' + str(
            longitude[i]) + ';'

        cursor.execute(query)
        data_id = cursor.fetchall()

        query = 'SELECT freeFormAddress FROM all_stores WHERE lat = ' + str(latitude[i]) + ' AND lon = ' + str(
            longitude[i]) + ';'

        cursor.execute(query)
        data_address = cursor.fetchall()

        # rcount = len(data)

        # print(rcount)
        if (len(data_store) != 0):
            store.append(data_store[0][0])
            ids.append(data_id[0][0])
            addresses.append((data_address[0][0]))
    cursor.close()
    db.close()
    return store, ids, addresses


def getItemStatus(selected_item, store_id, num_to_average): #get the status of the selected item using moving average
    db = mysql.connect()
    cursor = db.cursor()
    query = "SELECT rating FROM status_list WHERE id = '" + str(store_id) + "' AND item = " + str(selected_item) +";"
    cursor.execute(query)
    status_values = []
    status = cursor.fetchall()

    moving_average = 0
    for i in range(len(status)):
        status_values.append(5-(status[i][0])+1)

    if len(status_values) != 0:
        for i in range(min(len(status_values),num_to_average)):
            moving_average += status_values[i]

        moving_average = moving_average/min(num_to_average, len(status_values))
    cursor.close()
    db.close()
    return round(moving_average)



def parseMessage(store, raw_item, raw_rating, raw_date, raw_user): # get status messages

    messages = []
    type = []
    rating_choices = ['Full Stock', 'Majority Remaining', 'Half Remaining', 'Few Remaining', 'None Remaining']
    item_choices = ['Toilet Paper', 'Hand Sanitizer']

    color_array = []
    for x in range(len(raw_rating)):
        i = len(raw_rating) - x - 1
        if raw_user[i][0] == None:
            new_message = '' + raw_date[i][0] + ' Status of ' + item_choices[
                raw_item - 1] + ' at ' + store + ': ' + rating_choices[int(raw_rating[i][0]) - 1]
        else:
            new_message = '' + raw_date[i][0] + ' Status of ' + item_choices[raw_item - 1] + ' at ' + store + ': ' + rating_choices[int(raw_rating[i][0]) - 1] + " - " + raw_user[i][0]
        messages.append(new_message)
        color_array.append(int(raw_rating[i][0]))
        type.append(int(raw_item))
    return messages, color_array, type


def getAddress(address): # get basic store information for landing page
    message = 'Address: ' + address
    return message

def getPhone(phone):
    message = 'Phone:' + phone
    return message
def getItem(key):
    items = {'1': 'Toilet Paper', '2': 'Hand Sanitizer'}
    return items[key]

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        session['user'] = data
        print("hello",data)
    return "h"

@app.route('/location', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def location():
    db = mysql.connect()
    cursor = db.cursor()
    form = LocationForm()

    if form.validate_on_submit():
        flash('Item requested from the user {}'.format(form.item_option.data))
        flash('Item requested from the user {}'.format(form.address.data))
        session['selected_item'] = form.item_option.data
        user_lat, user_lon = tomtomSearch.geo(form.address.data)
        lat_lst, lon_lst = tomtomSearch.search(user_lat, user_lon)
        stores, ids, addresses = getStore(lat_lst, lon_lst)
        session['stores'] = []
        session['ids'] = []
        session['addresses'] = []

        session['stores'] = stores
        session['ids'] = ids
        session['addresses'] = addresses
        cursor.close()
        db.close()
        return redirect('/store')

    cursor.close()
    db.close()
    return render_template('location.html', title='Location', form = form)


@app.route('/store', methods=['GET', 'POST'])
def stores():
    db = mysql.connect()
    cursor = db.cursor()

    form = StoreForm()
    if request.method == 'POST':

        #flash('Status requested from the user {}'.format(form.stores.data))
        option =  int(request.form['options'])
        session['selected_store'] = session.get('stores')[option]


        session['selected_id'] = session.get('ids')[option]
        cursor.close()
        db.close()
        return redirect('/item-status')
    status_values = []

    radio = {}
    for i in range(len(session.get('stores'))): # append radio button options
        form.stores.choices.append((str(i), (session.get('stores')[i] + ' - ' + session.get('addresses')[i])))
        radio[i] = str(session.get('stores')[i] + ' - ' + session.get('addresses')[i])
        status_values.append(getItemStatus(session.get('selected_item'), session.get('ids')[i], 5))
    cursor.close()
    db.close()
    return render_template("store.html", len=len(form.stores.choices), form=form, status_values=status_values, radio = radio, selected_item_index = int(session.get('selected_item')), selected_item_name = getItem(session.get('selected_item')))



@app.route('/item-status', methods=['GET', 'POST'])
def status():
    db = mysql.connect()
    status_form = StatusForm()
    cursor = db.cursor()

    if request.method == 'POST':
        user_email = ' '
        print()
        if session.get('user')['user_email'] == '':
            print("hello")
            cursor.close()
            db.close()
            return redirect("/item-status")
        user_email = session.get('user')['user_email']
        flash('Status requested from the user {}'.format(status_form.status_option.data))
        #flash('Status requested from the user {}'.format(status_form.item_option.data))
        now = datetime.now()
        date_now = now.strftime("%m/%d/%Y %H:%M:%S")
        # add manager

        query = "INSERT INTO status_list(date, item, rating, manager, store, id, user) VALUES('" + date_now + "'," + session.get('selected_item') + "," + status_form.status_option.data + ", 0, '" + session['selected_store'] + "', '" + session['selected_id'] + "','"+ user_email+"');"
        print(query)
        cursor.execute(query)
        cursor.execute("COMMIT;")
        time.sleep(0.5)
        cursor.close()
        db.close()
        return redirect('/item-status')



    get_query = "SELECT rating FROM status_list WHERE item = " + session.get('selected_item') +" AND id = '" + session['selected_id']  + "';"

    cursor.execute(get_query)
    raw_rating = cursor.fetchall()

    get_query = "SELECT date FROM status_list WHERE item = " + session.get('selected_item') +" AND id = '" + session['selected_id']  + "';"
    cursor.execute(get_query)
    raw_date = cursor.fetchall()

    get_query = "SELECT user FROM status_list WHERE item = " + session.get('selected_item') +" AND id = '" + session['selected_id']  + "';"
    cursor.execute(get_query)
    raw_user = cursor.fetchall()

    # get basic store info

    get_query = "SELECT phone FROM all_stores WHERE id = '" + session['selected_id']  + "';"
    cursor.execute(get_query)
    raw_phone = cursor.fetchall()

    get_query = "SELECT freeFormAddress FROM all_stores WHERE id = '" + session['selected_id']  + "';"
    cursor.execute(get_query)
    raw_address = cursor.fetchall()

    messages, colors, type_item = parseMessage(session['selected_store'], int(session.get('selected_item')), raw_rating, raw_date, raw_user)

    basic_info = []
    basic_info.append(getPhone(raw_phone[0][0]))
    basic_info.append(raw_address[0][0])

    #user_email = request.get_json()
    cursor.close()
    db.close()
    if session.get('user')['user_email'] == '':
        return render_template("status.html", signIn=0, store=session['selected_store'], form=status_form,
                               messages=messages,
                               len=len(messages), colors=colors, type_item=type_item, basic_info=basic_info,
                               selected_item=getItem(session.get('selected_item')))
    else:
        return render_template("status.html", signIn = 1, store=session['selected_store'], form=status_form, messages=messages,
                               len=len(messages), colors=colors, type_item=type_item, basic_info=basic_info, selected_item = getItem(session.get('selected_item')))


@app.route('/index', methods=['GET', 'POST'])
def homepage():
    session['stores'] = []
    session['ids'] = []
    session['addresses'] = []
    session['has_enabled'] = 'disabled'
    return render_template("index.html")


if __name__ == '__main__':
    app.run(use_reloader=True, debug=True)

