from flask import Flask, render_template, jsonify, request
from codes import generateUniqueCode
from app import db
from app.models import ManagerInformationss, ReturnedOrderss

app = Flask(__name__)

from codes import generateManagerCode
from sms import *

BASE_URL = ("http://testhorizon.gothiagroup.com/"
            "eCommerceServicesWebApi_ver339/api/v3/")

@app.route("/")
def index():

    return render_template('return_form.html')


@app.route('/dashboard')
def dashboard():

    data = getTemplateStubs()

    return render_template('dashboard.html',
        data_taken=data['taken'],
        data_purchased=data['purchased'],
        data_returned=data['returned']
    )

@app.route('/solution')
def solution():

    return render_template('solution.html')

@app.route('/codes')
def codes():
    manager_code = generateManagerCode()
    return jsonify({"manager_codes": manager_code})


@app.route('/managers/add')
def add_manager():
    desc = request.args.get('desc', '')
    storeName = request.args.get('storeName', '')
    storeAddress = request.args.get('storeAddress', '')
    num = generateUniqueCode()
    manager = ManagerInformationss(desc, storeName, storeAddress, num)
    db.session.add(manager)
    db.session.commit()
    return num



@app.route('/return/', methods=['POST'])
def return_product():
    orderNumber = request.form['orderNumber']
    managerId = request.form['managerCode']

    if ReturnedOrderss.query.get(orderNumber) is not None:
        return jsonify({"Error": "Already returned this order."})
    #r = requests.get(BASE_URL + "orders/"+orderNumber)
    #if r.status_code is not 200:
        #return jsonify({"Error": "Not a valid order ID"})
    if ManagerInformationss.query.filter_by(returnCode=managerId).count() != 1:
        return jsonify({"Error": "Manager ID not valid"})
    # TODO: Call their API, the item has been returned
    # Possibly via SMS.

    manager = ManagerInformationss.query.filter_by(returnCode=managerId).first()
    res = generateUniqueCode()  # Not atomic at this point
    manager.returnCode = res

    db.session.add(ReturnedOrderss(orderNumber, manager.storeName, manager.storeAddress))
    db.session.commit()
    return jsonify({"New Manager Id": res})

@app.route('/managers/clear')
def clear_managers():
    db.session.query(ManagerInformationss).delete()
    db.session.commit()
    return jsonify({"Status": "Good"})

@app.route('/returns/clear')
def clear_returns():
    db.session.query(ReturnedOrderss).delete()
    db.session.commit()
    return jsonify({"Status": "Good"})

@app.route('/managers/show')
def show_managers():
    managers = [m.serialize() for m in ManagerInformationss.query.all()]
    print(managers)
    return jsonify({"manager_codes": managers})

@app.route('/returns/addresses')
def return_addresses():
    addresses = [(r.storeName, r.storeAddress) for r in ReturnedOrderss.query.all()]
    return jsonify(addresses)

@app.route("/receive_sms", methods=['GET', 'POST'])
def receive_sms():
    receiveSMS(request)
    # @app.route really wants to return a template
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', threaded=True)
