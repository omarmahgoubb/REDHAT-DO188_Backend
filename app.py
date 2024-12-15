import app as app
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from datetime import datetime
from functools import wraps
from bson import ObjectId



app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:4200"])

#app.config["MONGO_URI"] = "mongodb://localhost:27017/package_tracking_system"
app.config["MONGO_URI"] = "mongodb://mymongo:27017/package_tracking_system"

mongo = PyMongo(app)

LOGGED_IN_USERS_COLLECTION = "logged_in_users"


#Validation functions
def is_courier(user):
    return user.get("role") == "courier"

def is_admin(user):
    return user.get("role") == "admin"
#####################################################################################################################
#Feature 1
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')
    role = data.get('role', 'user')

    if not name or not email or not password or not role :
        return jsonify({"message": "Name, email, and password are required"}), 400

    existing_user = mongo.db.users.find_one({"$or": [{"name": name}, {"email": email}]})
    if existing_user:
        return jsonify({"message": "The email or username has been used before"}), 400

    mongo.db.users.insert_one(data)
    return jsonify({"message": "User registered successfully"}), 201
##################################################################################################################
#Feature 2
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = mongo.db.users.find_one({"email": data['email']})

    if user and user['password'] == data['password']:
        role = user.get('role', 'user')
        mongo.db[LOGGED_IN_USERS_COLLECTION].delete_many({})
        mongo.db[LOGGED_IN_USERS_COLLECTION].insert_one({
            "email": user['email'],
            "role": role
        })
        return jsonify({"message": "Login successful", "email": user['email'], "role": role}), 200
    return jsonify({"message": "Invalid credentials"}), 401
######################################################################################################################
#Feature 3,4
@app.route('/create_order', methods=['POST'])
def create_order():
    logged_in_user = mongo.db.logged_in_users.find_one()
    if not logged_in_user:
        return jsonify({"message": "No user is currently logged in"}), 400
    email = logged_in_user['email']
    data = request.json

    product_id = data.get('product_id')
    delivery_address = data.get('delivery_address')
    pickup_location = data.get('pickup_location')
    dropoff_location = data.get('dropoff_location')
    package_details = data.get('package_details')
    delivery_time = data.get('delivery_time')

    if not product_id or not delivery_address or not pickup_location\
            or not dropoff_location or not package_details or not delivery_time:
        return jsonify({"message": "All fields are required (Product ID, Delivery Address, Pickup Location, Dropoff Location, Package Details, Delivery Time)"}), 400

    order_data = {
        "email": email,
        "product_id": product_id,
        "delivery_address": delivery_address,
        "pickup_location": pickup_location,
        "dropoff_location": dropoff_location,
        "package_details": package_details,
        "delivery_time": delivery_time,
        "order_status": "Pending",
        "courier": "aramex",
        "created_at": datetime.now()
    }
    mongo.db.orders.insert_one(order_data)
    return jsonify({"message": "Order created successfully"}), 201
######################################################################################################################
#Feature 5
@app.route('/my_orders', methods=['GET'])
def my_orders():
    logged_in_user = mongo.db.logged_in_users.find_one()
    if not logged_in_user:
        return jsonify({"message": "No user is currently logged in"}), 400
    email = logged_in_user['email']
    orders = mongo.db.orders.find({"email": email})
    order_list = []
    for order in orders:
        order_data = {
            "order_id": str(order["_id"]),
            "product_id": order["product_id"],
            "delivery_address": order["delivery_address"],
            "order_status": order["order_status"],
            "created_at": order["created_at"].strftime('%Y-%m-%d %H:%M:%S')  # Format date
        }
        order_list.append(order_data)
    return jsonify({"orders": order_list}), 200
#######################################################################################################################
#Feature 6
@app.route('/order_details/<order_id>', methods=['GET'])
def order_details(order_id):
    logged_in_user = mongo.db.logged_in_users.find_one()
    if not logged_in_user:
        return jsonify({"message": "No user is currently logged in"}), 400
    email = logged_in_user['email']
    try:
        order_object_id = ObjectId(order_id)
    except Exception as e:
        return jsonify({"message": "Invalid order ID format"}), 400
    order = mongo.db.orders.find_one({"email": email, "_id": order_object_id})
    if not order:
        return jsonify({"message": "Order not found for the logged in user"}), 404
    order_info = {
        "order_id": str(order["_id"]),
        "product_id": order["product_id"],
        "delivery_address": order["delivery_address"],
        "pickup_location": order.get("pickup_location", ""),
        "dropoff_location": order.get("dropoff_location", ""),
        "package_details": order.get("package_details", ""),
        "delivery_time": order.get("delivery_time", ""),
        "order_status": order["order_status"],
        "courier": order.get("courier", ""),
        "created_at": order["created_at"].strftime('%Y-%m-%d %H:%M:%S')
    }
    return jsonify({"order_details": order_info}), 200

@app.route('/order_details/<order_id>', methods=['PATCH'])
def cancel_order(order_id):
    logged_in_user = mongo.db.logged_in_users.find_one()
    if not logged_in_user:
        return jsonify({"message": "No user is currently logged in"}), 400
    try:
        order_object_id = ObjectId(order_id)
    except:
        return jsonify({"message": "Invalid order ID format"}), 400
    order = mongo.db.orders.find_one({"email": logged_in_user['email'], "_id": order_object_id})
    if not order:
        return jsonify({"message": "Order not found for the logged in user"}), 404
    if order["order_status"] == "Pending":
        mongo.db.orders.update_one(
            {"_id": order_object_id},
            {"$set": {"order_status": "Canceled"}}
        )
        return jsonify({"message": "Order status updated to 'Canceled'"}), 200
    elif order["order_status"] == "Canceled":
        return jsonify({"message": "The order is already canceled"}), 400
    else:
        return jsonify({"message": "The order is confirmed and cannot be canceled"}), 403
######################################################################################################################
#Feature 7
#Courier features
@app.route('/orders_by_courier/<courier>', methods=['GET'])
def get_orders_by_courier(courier):
    user = mongo.db.logged_in_users.find_one()
    if not is_courier(user):
        return jsonify({"message": "You are not allowed to use this"}), 403
    if not courier:
        return jsonify({"message": "Courier name is required"}), 400
    orders = mongo.db.orders.find({"courier": courier})
    order_list = []
    for order in orders:
        order_info = {
            "order_id": str(order["_id"]),
            "product_id": order["product_id"],
            "delivery_address": order["delivery_address"],
            "order_status": order["order_status"],
            "created_at": order["created_at"].strftime('%Y-%m-%d %H:%M:%S'),  # Format the date
        }
        order_list.append(order_info)
    if not order_list:
        return jsonify({"message": "No orders found for the specified courier"}), 404
    return jsonify({"orders": order_list}), 200

@app.route('/accept_order', methods=['POST'])  # Using POST method for updating
def accept_order():
    user = mongo.db.logged_in_users.find_one()  # Replace with your actual user retrieval logic
    if not is_courier(user):
        return jsonify({"message": "You are not allowed to use this"}), 403
    data = request.get_json()
    order_id = data.get('order_id')
    courier_name = data.get('courier')
    if not order_id or not courier_name:
        return jsonify({"message": "Order ID and courier name are required"}), 400
    try:
        order_object_id = ObjectId(order_id)
    except Exception as e:
        return jsonify({"message": "Invalid order ID format"}), 400
    order = mongo.db.orders.find_one({"_id": order_object_id})
    if not order:
        return jsonify({"message": "Order not found"}), 404
    if order["courier"] != courier_name:
        return jsonify({"message": "This order does not belong to the specified courier"}), 403
    if order["order_status"] == "Canceled":
        return jsonify({"message": "Order is already Canceled"}), 403
    mongo.db.orders.update_one(
        {"_id": order_object_id},
        {"$set": {"order_status": "Accepted by courier"}}
    )
    return jsonify({"message": "Order is accepted by courier "}), 200

@app.route('/reject_order', methods=['POST'])
def reject_order():
    user = mongo.db.logged_in_users.find_one()
    if not is_courier(user):
        return jsonify({"message": "You are not allowed to use this"}), 403
    data = request.json
    order_id = data.get('order_id')
    courier = data.get('courier')
    if not order_id or not courier:
        return jsonify({"message": "Order ID and courier are required"}), 400
    try:
        order_object_id = ObjectId(order_id)
    except:
        return jsonify({"message": "Invalid order ID format"}), 400
    order = mongo.db.orders.find_one({"_id": order_object_id})
    if not order:
        return jsonify({"message": "Order not found"}), 404
    if order["courier"] == courier:
        if order["order_status"] == "Canceled":
            return jsonify({"message": "Sorry, the order is already canceled and cannot be rejected"}), 403
        else:
            mongo.db.orders.update_one({"_id": order_object_id}, {"$set": {"order_status": "order rejected by courier"}})
            return jsonify({"message": "Order rejected successfully"}), 200
    else:
        return jsonify({"message": "This order does not belong to the specified courier"}), 403
######################################################################################################################
#Feature 8
@app.route('/update_order_status', methods=['POST'])
def update_order_status():
    user = mongo.db.logged_in_users.find_one()
    if not is_courier(user):
        return jsonify({"message": "You are not authorized to update the order status"}), 403
    data = request.json
    order_id = data.get('order_id')
    new_status = data.get('new_status')
    if not order_id or not new_status:
        return jsonify({"message": "Order ID and new status are required"}), 400
    valid_statuses = ["picked up", "in transit", "delivered"]
    if new_status not in valid_statuses:
        return jsonify({"message": "Invalid status"}), 400
    try:
        order_object_id = ObjectId(order_id)
    except Exception:
        return jsonify({"message": "Invalid order ID format"}), 400
    order = mongo.db.orders.find_one({"_id": order_object_id})
    if not order:
        return jsonify({"message": "Order not found"}), 404
    if order["order_status"] == "Canceled":
        return jsonify({"message": "Order is canceled and cannot be updated"}), 400
    mongo.db.orders.update_one(
        {"_id": order_object_id},
        {"$set": {"order_status": new_status}}
    )
    return jsonify({"message": f"Order status updated to '{new_status}' successfully"}), 200
#######################################################################################################################
#Feature 9
@app.route('/manage_update', methods=['PUT'])
def manage_orders_update():
    user = mongo.db.logged_in_users.find_one()
    if not is_admin(user):
        return jsonify({"message": "You are not allowed to use this"}), 403
    data = request.get_json()
    order_id = data.get('order_id')
    update_fields = {key: value for key, value in data.items() if key != 'order_id'}
    if not order_id or not update_fields:
        return jsonify({"message": "Order ID and fields to update are required"}), 400
    result = mongo.db.orders.update_one({"_id": ObjectId(order_id)}, {"$set": update_fields})
    if result.matched_count == 0:
        return jsonify({"message": "Order not found"}), 404
    return jsonify({"message": "Order updated successfully"}), 200

@app.route('/manage_delete/<order_id>', methods=['DELETE'])
def manage_orders_delete(order_id):
    user = mongo.db.logged_in_users.find_one()
    if not is_admin(user):
        return jsonify({"message": "You are not allowed to use this"}), 403
    try:
        result = mongo.db.orders.delete_one({"_id": ObjectId(order_id)})
    except Exception as e:
        return jsonify({"message": "Invalid order ID format"}), 400
    if result.deleted_count == 0:
        return jsonify({"message": "Order not found"}), 404
    return jsonify({"message": "Order deleted successfully"}), 200

@app.route('/manage_get_all', methods=['GET'])
def get_all_orders():

    user = mongo.db.logged_in_users.find_one()
    if not is_admin(user):
        return jsonify({"message": "You are not allowed to use this"}), 403
    orders = mongo.db.orders.find()
    order_list = []
    for order in orders:
        order_info = {
            "order_id": str(order["_id"]),
            "product_id": order.get("product_id"),
            "delivery_address": order.get("delivery_address"),
            "order_status": order.get("order_status"),
            "created_at": order.get("created_at").strftime('%Y-%m-%d %H:%M:%S'),
        }
        order_list.append(order_info)
    return jsonify({"orders": order_list}), 200
######################################################################################################################
#Feature 10
@app.route('/assigned-to-courier', methods=['GET'])
def get_assigned_orders():
    user = mongo.db.logged_in_users.find_one()
    if not is_admin(user):
        return jsonify({"message": "You are not allowed to use this"}), 403
    courier_name = request.args.get('courier')
    if not courier_name:
        return jsonify({"error": "Courier name is required"}), 400
    orders = mongo.db.orders.find({'courier': courier_name})
    order_list = []
    for order in orders:
        order['_id'] = str(order['_id'])
        order_list.append(order)
    return jsonify(order_list), 200

@app.route('/reassign', methods=['PUT'])
def reassign_order():
    user = mongo.db.logged_in_users.find_one()
    if not is_admin(user):
        return jsonify({"message": "You are not allowed to use this"}), 403
    data = request.get_json()
    order_id = data.get('order_id')
    new_courier_name = data.get('courier')
    if not order_id or not new_courier_name:
        return jsonify({"error": "Order ID and new courier name are required"}), 400
    result = mongo.db.orders.update_one(
        {'_id': ObjectId(order_id)},
        {'$set': {'courier': new_courier_name}}
    )
    if result.matched_count == 0:
        return jsonify({"error": "Order not found"}), 404
    return jsonify({"message": "Order reassigned successfully"}), 200
######################################################################################################################
@app.route('/logout', methods=['POST'])
def logout():
    data = request.json
    email = data.get('email')

    if email:
        mongo.db[LOGGED_IN_USERS_COLLECTION].delete_one(
            {"email": email})
        return jsonify({"message": "Logout successful"}), 200
    return jsonify({"message": "Email is required"}), 400
#######################################################################################################################
if __name__ == '__main__':
    app.run(debug=True)
