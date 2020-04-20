# importing modules
import time
import tomtomSearch
from flask_bootstrap import Bootstrap
from geopy.geocoders import GoogleV3
from flask import Flask, render_template, request, redirect, flash, session, jsonify, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, SelectField, RadioField
from wtforms.validators import DataRequired
import mysql.connector as mysql
from datetime import datetime

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


db = mysql.connect(
    host="localhost",
    user="root",
    passwd="$Soccer2001%",
    database="servers"
)

# declaring app name
app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = 'WAcodevid2020'


def getStore(latitude, longitude): # get stores from coordinates
    cursor = db.cursor(buffered=True)
    # SELECT school, student FROM servers.table1 LIMIT 1;
    store = []
    ids = []
    addresses = []
    for i in range(len(latitude)):

        query = 'SELECT name FROM servers.all_stores WHERE lat = ' + str(latitude[i]) + ' AND lon = ' + str(
            longitude[i]) + ';'

        cursor.execute(query)
        data_store = cursor.fetchall()

        query = 'SELECT id FROM servers.all_stores WHERE lat = ' + str(latitude[i]) + ' AND lon = ' + str(
            longitude[i]) + ';'

        cursor.execute(query)
        data_id = cursor.fetchall()

        query = 'SELECT freeFormAddress FROM servers.all_stores WHERE lat = ' + str(latitude[i]) + ' AND lon = ' + str(
            longitude[i]) + ';'

        cursor.execute(query)
        data_address = cursor.fetchall()

        # rcount = len(data)

        # print(rcount)
        if (len(data_store) != 0):
            store.append(data_store[0][0])
            ids.append(data_id[0][0])
            addresses.append((data_address[0][0]))

    return store, ids, addresses





def parseMessage(store, raw_item, raw_rating, raw_date): # get status messages
    messages = []
    type = []
    rating_choices = ['Full Stock', 'Majority Remaining', 'Half Remaining', 'Few Remaining', 'None Remaining']
    item_choices = ['Toilet Paper', 'Hand Sanitizer']

    color_array = []
    for x in range(len(raw_item)):
        i = len(raw_item) - x - 1

        new_message = '' + raw_date[i][0] + ' Status of ' + item_choices[
            int(raw_item[i][0]) - 1] + ' at ' + store + ': ' + rating_choices[int(raw_rating[i][0]) - 1]
        messages.append(new_message)
        color_array.append(int(raw_rating[i][0]))
        type.append(int(raw_item[i][0]))
    return messages, color_array, type


def parseBasicInfo(address, phone): # get basic store information for landing page
    message = 'Address: ' + address + '\n' + 'Phone: ' + phone
    return message

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/location', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def location():


    cursor = db.cursor(buffered=True)



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
        return redirect('/store')
    '''
    elif request.method == 'POST':
        print('hello')
        lat_request = request.get_json(force=True)['latitude']  # parse as JSON
        lon_request = request.get_json(force=True)['longitude']
        #session['user_address'] = tomtomSearch.reverseGeo(lat_request, lon_request)

        print('hello')
        print(lat_request)
        lat_lst, lon_lst = tomtomSearch.search(lat_request, lon_request)
        stores, ids, addresses = getStore(lat_lst, lon_lst)
        session['stores'] = []
        session['ids'] = []
        session['addresses'] = []

        session['stores'] = stores
        session['ids'] = ids
        session['addresses'] = addresses
        session['has_enabled'] = 'enabled'
        print(session.get('has_enabled'))
        # print(session.get('stores'))
        return render_template('location.html', title='Location', formItem = formItem)
    '''

    return render_template('location.html', title='Location', form = form)


@app.route('/store', methods=['GET', 'POST'])
def stores():
    cursor = db.cursor(buffered=True)

    form = StoreForm()
    if request.method == 'POST':
        flash('Status requested from the user {}'.format(form.stores.data))
        session['selected_store'] = session.get('stores')[int(form.stores.data)]
        # parsing lon and lat

        session['selected_id'] = session.get('ids')[int(form.stores.data)]

        return redirect('/login')
    status_values = []
    # get stores and addresses and statuses to form list
    for i in range(len(session.get('stores'))):
        form.stores.choices.append((str(i), (session.get('stores')[i] + ' - ' + session.get('addresses')[i])))
        query = "SELECT rating FROM servers.status_list WHERE id = '" + session.get('ids')[i] + "';"
        print(query)
        cursor.execute(query)
        print(query)
        status = cursor.fetchall()
        if len(status) == 0:
            status_values.append(0)
        else:
            status_values.append(status[0])

    return render_template("store.html", len=len(form.stores.choices), form=form, status_values=status_values)


@app.route('/status', methods=['GET', 'POST'])
def status():
    status_form = StatusForm()
    cursor = db.cursor(buffered=True)

    if request.method == 'POST':
        flash('Status requested from the user {}'.format(status_form.status_option.data))
        flash('Status requested from the user {}'.format(status_form.item_option.data))
        now = datetime.now()
        date_now = now.strftime("%m/%d/%Y %H:%M:%S")
        # add manager
        query = "INSERT INTO servers.status_list(date, item, rating, manager, store, id) VALUES('" + date_now + "'," + status_form.item_option.data + "," + status_form.status_option.data + ", 0, '" + \
                session['selected_store'] + "', '" + session['selected_id'] + "' );"
        cursor.execute(query)
        cursor.execute("COMMIT;")
        time.sleep(0.5)
        return redirect('/status')

    get_query = "SELECT * FROM servers.status_list WHERE id = '" + session['selected_id'] + "';"
    # print(get_query)
    cursor.execute(get_query)
    # print(cursor.fetchall())

    get_query = "SELECT item FROM servers.status_list WHERE id = '" + session['selected_id'] + "';"
    cursor.execute(get_query)
    raw_item = cursor.fetchall()
    print(raw_item)

    get_query = "SELECT rating FROM servers.status_list WHERE id = '" + session['selected_id'] + "';"
    cursor.execute(get_query)
    raw_rating = cursor.fetchall()

    get_query = "SELECT date FROM servers.status_list WHERE id = '" + session['selected_id'] + "';"
    cursor.execute(get_query)
    raw_date = cursor.fetchall()

    # get basic store info

    get_query = "SELECT phone FROM servers.all_stores WHERE id = '" + session['selected_id'] + "';"
    cursor.execute(get_query)
    raw_phone = cursor.fetchall()

    get_query = "SELECT freeFormAddress FROM servers.all_stores WHERE id = '" + session['selected_id'] + "';"
    cursor.execute(get_query)
    raw_address = cursor.fetchall()

    messages, colors, type_item = parseMessage(session['selected_store'], raw_item, raw_rating, raw_date)
    print(raw_address[0][0])
    basic_info = parseBasicInfo(raw_address[0][0], raw_phone[0][0])

    return render_template("status.html", store=session['selected_store'], form=status_form, messages=messages,
                           len=len(messages), colors=colors, type_item=type_item, basic_info=basic_info)


@app.route('/index', methods=['GET', 'POST'])
def homepage():
    session['stores'] = []
    session['ids'] = []
    session['addresses'] = []
    session['has_enabled'] = 'disabled'
    return render_template("index.html")


if __name__ == '__main__':
    # print(tomtomSearch.reverseGeo(42.642594, -71.435574))
    #print(tomtomSearch.geo('5 Vineyard Roac, westford Massachusetts'))
    app.run(use_reloader=True, debug=True)
