from pymongo import MongoClient, ASCENDING

client = MongoClient('mongo', 27017, username='root', password='rootpassword')
db = client.flask_db
db.tari.create_index([("nume_tara", ASCENDING)], unique=True)
db.orase.create_index([("id_tara", ASCENDING), ("nume_oras", ASCENDING)], unique=True)
db.temperaturi.create_index([("id_oras", ASCENDING), ("timestamp", ASCENDING)], unique=True)

def get_new_id(collection):
    counter_db = db.counters.find_one_and_update({'_id': collection},
                                                 {'$inc': {'seq': 1}},
                                                 projection={'seq': True, '_id': False})
    if counter_db is None:
        db.counters.insert_one({
            '_id': collection,
            "seq": 0
        })
        return 0

    return counter_db['seq'] + 1
