from database import db

def delete_city_cascade(c_id):
    db.temperaturi.delete_many({'id_oras': c_id})
    result = db.orase.delete_one({'id': c_id})
    if result.deleted_count == 0:
        return False
    return True

def delete_country_cascade(c_id):
    cities = list(db.orase.find({'id_tara': c_id}))
    for city in cities:
        delete_city_cascade(city['id'])
    result = db.tari.delete_one({'id': c_id})
    
    if result.deleted_count == 0:
        return False
    return True