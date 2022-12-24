from flask import Blueprint, request
import json
from database import db, get_new_id
from cascade_deletion import delete_country_cascade

countries_app = Blueprint('countries_api', __name__)


@countries_app.route('/api/countries', methods=['GET'])
def get_countries():
    countries_db = list(db.tari.find({}))
    countries = list(map(lambda country: {
        'id': country['id'],
        'nume': country['nume_tara'],
        'lat': country['latitudine'],
        'lon': country['longitudine']
    }, countries_db))
    return json.dumps(countries), 200


@countries_app.route('/api/countries', methods=['POST'])
def add_country():
    request_data = request.get_json()
    requirements = ['nume', 'lat', 'lon']
    errors = list(filter(lambda key: key not in request_data, requirements))
    if len(errors) > 0:
        return 'Missing params', 400
    try:
        lat = float(request_data['lat'])
        lon = float(request_data['lon'])
        new_id = get_new_id('tari')
        db.tari.insert_one({
            'nume_tara': request_data['nume'],
            'id': new_id,
            'latitudine': lat,
            'longitudine': lon
        })
        return {'id': new_id}, 201
    except Exception as e:
        return f'Error insert: {e}', 400


@countries_app.route('/api/countries/<c_id>', methods=['PUT'])
def update_country(c_id):
    try:
        c_id = int(c_id)
    except Exception as e:
        return f'Error: {e}', 400

    request_data = request.get_json()
    requirements = ['nume', 'lat', 'lon']
    errors = list(filter(lambda key: key not in request_data, requirements))
    if len(errors) > 0:
        return 'Missing params', 400

    new_value = {"$set": {
        'id': c_id,
        'nume_tara': request_data['nume'],
        'latitudine': request_data['lat'],
        'longitudine': request_data['lon']
    }}
    try:
        result = db.tari.find_one_and_update({'id': c_id}, new_value)
        if result is None:
            return 'update error', 400
        return 'updated', 200
    except Exception as e:
        return f'Error update: {e}', 400


@countries_app.route('/api/countries/<c_id>', methods=['DELETE'])
def delete_country(c_id):
    try:
        c_id = int(c_id)
    except Exception as e:
        return f'Error: {e}', 400

    result = delete_country_cascade(c_id)

    if not result:
        return 'Not found', 404
        
    return 'deleted', 200
