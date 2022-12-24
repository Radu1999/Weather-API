from flask import Blueprint, request
import json
from database import db, get_new_id
from cascade_deletion import delete_city_cascade

cities_app = Blueprint('cities_api', __name__)


@cities_app.route('/api/cities', methods=['GET'])
def get_cities():
    cities_db = list(db.orase.find({}))
    cities = list(map(lambda city: {
        'id': city['id'],
        'idTara': city['id_tara'],
        'nume': city['nume_oras'],
        'lat': city['latitudine'],
        'lon': city['longitudine']
    }, cities_db))
    return json.dumps(cities), 200


@cities_app.route('/api/cities', methods=['POST'])
def add_city():
    request_data = request.get_json()
    requirements = ['nume', 'lat', 'lon', 'idTara']
    errors = list(filter(lambda key: key not in request_data, requirements))
    if len(errors) > 0:
        return 'Missing params', 400
    try:
        lat = float(request_data['lat'])
        lon = float(request_data['lon'])
        id_tara = int(request_data['idTara'])
        country = db.tari.find_one({'id': request_data['idTara']})
        if country is None:
            return 'Error', 400
            
        new_id = get_new_id('orase')
        db.orase.insert_one({
            'id_tara': id_tara,
            'nume_oras': request_data['nume'],
            'id': new_id,
            'latitudine': lat,
            'longitudine': lon
        })
        return {'id': new_id}, 201
    except Exception as e:
        return f'Error insert: {e}', 400


@cities_app.route('/api/cities/country/<c_id>', methods=['GET'])
def get_cities_by_country(c_id):
    try:
        c_id = int(c_id)
    except Exception as e:
        return f'Error: {e}', 400

    cities_db = list(db.orase.find({'id_tara': c_id}))
    cities = list(map(lambda city: {
        'id': city['id'],
        'idTara': city['id_tara'],
        'nume': city['nume_oras'],
        'lat': city['latitudine'],
        'lon': city['longitudine']
    }, cities_db))
    return json.dumps(cities), 200


@cities_app.route('/api/cities/<c_id>', methods=['PUT'])
def update_city(c_id):
    try:
        c_id = int(c_id)
    except Exception as e:
        return f'Error: {e}', 400

    request_data = request.get_json()
    requirements = ['nume', 'lat', 'lon', 'idTara']
    errors = list(filter(lambda key: key not in request_data, requirements))
    if len(errors) > 0:
        return 'Missing params', 400

    new_value = {"$set": {
        'id': c_id,
        'id_tara': request_data['idTara'],
        'nume_oras': request_data['nume'],
        'latitudine': request_data['lat'],
        'longitudine': request_data['lon']
    }}
    
    try:
        result = db.orase.find_one_and_update({'id': c_id}, new_value)
        if result is None:
            return 'update error', 400
        return 'updated', 200
    except Exception as e:
        return f'Error at update {e}', 400

@cities_app.route('/api/cities/<c_id>', methods=['DELETE'])
def delete_city(c_id):
    try:
        c_id = int(c_id)
    except Exception as e:
        return f'Error: {e}', 400
    result = delete_city_cascade(c_id)
    if not result:
        return 'Not found', 404
    return 'deleted', 200
