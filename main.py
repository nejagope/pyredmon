import redis
import json

import pymongo
import os
import sys

import asyncio
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers

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
MONGO_ITEMS_COLLECTION = os.environ['MONGO_ITEMS_COLLECTION']

NATS_SERVER = os.environ['NATS_SERVER']
NATS_SUBJECT = os.environ['NATS_SUBJECT']

async def run(loop):
    nc = NATS()
    await nc.connect(NATS_SERVER, loop=loop)
    async def message_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        print("Received a message on '{subject} {reply}': {data}".format(subject=subject, reply=reply, data=data))
        
        try:        
            item = json.loads(data)            
            #Redis
            r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=0)
            #Se guarda el último item insertado en Redis
            #r.hmset(REDIS_LAST_ITEM, item) #deprecated usar hset en lugar de hmset
            r.hset(REDIS_LAST_ITEM, "Nombre", item["Nombre"])
            r.hset(REDIS_LAST_ITEM, "Departamento", item["Departamento"])
            r.hset(REDIS_LAST_ITEM, "Edad", item["Edad"])
            r.hset(REDIS_LAST_ITEM, "Forma de contagio", item["Forma de contagio"])
            r.hset(REDIS_LAST_ITEM, "Estado", item["Estado"])
            #Se agrega la edad del último item insertado en la lista de edades en Redis
            r.rpush(REDIS_AGES_LIST, item["Edad"])

            #mongo
            client = pymongo.MongoClient('mongodb://%s:%s@%s:%s' %(MONGO_USER, MONGO_PASSWORD,MONGO_HOST, MONGO_PORT))
            db = client[MONGO_DB_NAME]
            collection = db[MONGO_ITEMS_COLLECTION]
            #Se inserta el item en mongo, en la colección items
            x = collection.insert_one(item)
            
        except Exception as e:            
            print("Unexpected error:", sys.exc_info()[0])
            if hasattr(e, 'message'):
                print("Error  inesperado: " + e.message)
            
    print('Escuchando...')
    # Simple publisher and async subscriber via coroutine.
    sid = await nc.subscribe(NATS_SUBJECT, cb=message_handler)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.run_forever()