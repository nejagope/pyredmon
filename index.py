import redis
import json

import pymongo
import os
import sys
from flask import Flask, render_template, request, jsonify
from bson.json_util import dumps

REDIS_HOST = os.environ['REDIS_HOST']
REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
REDIS_PORT = os.environ['REDIS_PORT']
REDIS_AGES_LIST = os.environ['REDIS_AGES_LIST']
REDIS_LAST_ITEM = os.environ['REDIS_LAST_ITEM']

MONGO_HOST = os.environ['MONGO_HOST']
MONGO_USER = os.environ['MONGO_USER']
MONGO_PASSWORD = os.environ['MONGO_PASSWORD']
MONGO_PORT = os.environ['MONGO_PORT']
MONGO_DB_NAME = os.environ['MONGO_DB']

app = Flask(__name__)

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/add")
def add():
	try:
		item = request.get_json()
		#redis		
		r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=0)				
		#last item
		r.hmset(REDIS_LAST_ITEM, item)
		#ages list
		r.rpush(REDIS_AGES_LIST, item["Edad"])	
		
		#insert whole item in mongo items
		client = pymongo.MongoClient('mongodb://%s:%s@%s:%s' %(MONGO_USER, MONGO_PASSWORD,MONGO_HOST, MONGO_PORT))		
		db = client[MONGO_DB_NAME]
		collection = db["items"]		
		x = collection.insert_one(item)							
		return jsonify({"error": 0, "result": "OK"})	
	
	except Exception as e:	
		if hasattr(e, 'message'):
			print("Error  inesperado: " + e.message)
			return jsonify({"error": 1, "result": "Unexpected error: " + e.message}), 500
		else:
			print("Error inesperado: " + e)
			return jsonify({"error": 1, "result": "Unexpected error: " + e}), 500

@app.route("/addall")
def addAll():
	try:
		items = request.get_json()		
		lastIndex = len(items) - 1
		if lastIndex > -1: 
			#redis		
			r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=0)				
			#last item
			r.hmset(REDIS_LAST_ITEM, items[lastIndex])
			#ages list
			for item in items:
				r.rpush(REDIS_AGES_LIST, item["Edad"])	
			
			#insert items in mongo
			client = pymongo.MongoClient('mongodb://%s:%s@%s:%s' %(MONGO_USER, MONGO_PASSWORD,MONGO_HOST, MONGO_PORT))		
			db = client[MONGO_DB_NAME]
			collection = db["items"]		
			x = collection.insert_many(items)					
		return jsonify({"error": 0, "result": "OK"})
	
	except Exception as e:	
		if hasattr(e, 'message'):
			print("Error  inesperado: " + e.message)
			return jsonify({"error": 1, "result": "Unexpected error: " + e.message}), 500
		else:
			print("Error inesperado: " + e)
			return jsonify({"error": 1, "result": "Unexpected error: " + e}), 500

@app.route("/items")
def items():
	try:		
		client = pymongo.MongoClient('mongodb://%s:%s@%s:%s' %(MONGO_USER, MONGO_PASSWORD,MONGO_HOST, MONGO_PORT))		
		db = client[MONGO_DB_NAME]
		collection = db["items"]				
		itemsJson = dumps(collection.find())		
		return itemsJson		
	
	except Exception as e:	
		if hasattr(e, 'message'):
			print("Error  inesperado: " + e.message)
			return jsonify({"error": 1, "result": "Unexpected error: " + e.message}), 500
		else:
			print("Error inesperado: " + e)
			return jsonify({"error": 1, "result": "Unexpected error: " + e}), 500

if __name__ == "__main__":
	app.run(debug=True, host="0.0.0.0")
