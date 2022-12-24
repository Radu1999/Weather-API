from flask import Blueprint, request
import json
from database import db, get_new_id
from datetime import datetime

temperatures_app = Blueprint('temperatures_api', __name__)


@temperatures_app.route('/api/temperatures', methods=['POST'])
def add_temperature():
    request_data = request.get_json()
    requirements = ['idOras', 'valoare']
    errors = list(filter(lambda key: key not in request_data, requirements))
    if len(errors) > 0:
        return 'Missing params', 400
    try:
        val = float(request_data['valoare'])
        id_oras = int(request_data['idOras'])
        city = db.orase.find_one({'id': request_data['idOras']})
        if city is None:
            return 'Error', 400
            
        new_id = get_new_id('temperaturi')
        db.temperaturi.insert_one({
            'id_oras': id_oras,
            'id': new_id,
            'valoare': val,
            'timestamp': datetime.utcnow().timestamp()
        })
        return {'id': new_id}, 201
    except Exception as e:
        return f'Error insert: {e}', 400


@temperatures_app.route('/api/temperatures/<t_id>', methods=['PUT'])
def update_temperature(t_id):
    try:
        t_id = int(t_id)
    except Exception as e:
        return f'Error: {e}', 400

    request_data = request.get_json()
    requirements = ['idOras', 'valoare']
    errors = list(filter(lambda key: key not in request_data, requirements))
    if len(errors) > 0:
        return 'Missing params', 400

    new_value = {"$set": {
        'id': t_id,
        'id_oras': request_data['idOras'],
        'valoare': request_data['valoare']
    }}

    try:
        result = db.temperaturi.find_one_and_update({'id': t_id}, new_value)
        if result is None:
            return 'update error', 400
        return 'updated', 200

    except Exception as e:
        return f'Error: {e}', 400


@temperatures_app.route('/api/temperatures/cities/<city_id>', methods=['GET'])
def get_temperatures_by_city(city_id):
    try:
        city_id = int(city_id)
    except Exception as e:
        return f'Error: {e}', 400

    args = request.args
    condition = {'$gte': 0, '$lte': datetime.utcnow().timestamp()}
    start = args.get('from')
    if start is not None:
        condition["$gte"] = datetime.strptime(start, '%Y-%m-%d').timestamp()

    end = args.get('until')
    if end is not None:
        condition["$lte"] = datetime.strptime(end, '%Y-%m-%d').timestamp()

    temperatures_db = list(db.temperaturi.find(
        {'timestamp': condition, 'id_oras': city_id}
    ))
    temperatures = list(map(lambda temperature: {
        'id': temperature['id'],
        'valoare': temperature['valoare'],
        'timestamp': datetime.utcfromtimestamp(temperature['timestamp']).strftime("%Y-%m-%d")
    }, temperatures_db))
    return json.dumps(temperatures), 200


@temperatures_app.route('/api/temperatures/', methods=['GET'])
def get_temperatures():
    args = request.args
    condition_temp = {'$gte': 0, '$lte': datetime.utcnow().timestamp()}
    start = args.get('from')
    if start:
        condition_temp["$gte"] = datetime.strptime(start, '%Y-%m-%d').timestamp()

    end = args.get('until')
    if end:
        condition_temp["$lte"] = datetime.strptime(end, '%Y-%m-%d').timestamp()

    try:
        lat = -1 if args.get('lat') is None else float(args.get('lat'))
        lon = -1 if args.get('lon') is None else float(args.get('lon'))
    except Exception as e:
        return f'Error: {e}', 400

    temperatures_db = list(db.temperaturi.find(
        {'timestamp': condition_temp}
    ))
    temperatures = []
    for temperature in temperatures_db:
        city = db.orase.find_one({'id': temperature['id_oras']})
        if city is None:
            continue
        if lat != -1 and city['latitudine'] != lat:
            continue
        if lon != -1 and city['longitudine'] != lon:
            continue
        temperatures.append({
            'id': temperature['id'],
            'valoare': temperature['valoare'],
            'timestamp': datetime.utcfromtimestamp(temperature['timestamp']).strftime("%Y-%m-%d")
        })
    return json.dumps(temperatures), 200


@temperatures_app.route('/api/temperatures/countries/<country_id>', methods=['GET'])
def get_temperatures_by_country(country_id):
    try:
        country_id = int(country_id)
    except Exception as e:
        return f'Error: {e}', 400

    args = request.args
    condition = {'$gte': 0, '$lte': datetime.utcnow().timestamp()}
    start = args.get('from')
    if start is not None:
        condition["$gte"] = datetime.strptime(start, '%Y-%m-%d').utcnow()

    end = args.get('until')
    if end is not None:
        condition["$lte"] = datetime.strptime(end, '%Y-%m-%d').utcnow()

    cities = list(db.orase.find(
        {'id_tara': country_id},
    ))

    temperatures_db = []
    for city in cities:
        temperatures_db.extend(list(db.temperaturi.find(
           {'timestamp': condition,
            'id_oras': city['id']},
        )))

    temperatures = list(map(lambda temperature: {
        'id': temperature['id'],
        'valoare': temperature['valoare'],
        'timestamp': datetime.utcfromtimestamp(temperature['timestamp']).strftime("%Y-%m-%d")
    }, temperatures_db))
    return json.dumps(temperatures), 200


@temperatures_app.route('/api/temperatures/<t_id>', methods=['DELETE'])
def delete_temperature(t_id):
    try:
        t_id = int(t_id)
    except Exception as e:
        return f'Error: {e}', 400

    result = db.temperaturi.delete_one({'id': t_id})
    if result.deleted_count == 0:
        return 'Not found', 404
    return 'deleted', 200
