
from flask import current_app, request, Blueprint, jsonify
from flask.ext.discoverer import advertise


bp = Blueprint('turbobee_app', __name__)


@advertise(scopes=['scope1', 'scope2'], rate_limit = [5000, 3600*24])
@bp.route('/date/<date>', methods=['GET', 'POST'])
@bp.route('/date', methods=['GET'])
def date(date=None):
    
    if request.method == 'GET':
        return jsonify({'date': current_app.get_date(date)}), 200
    elif request.method == 'POST':
        return jsonify({'date': current_app.get_date(date)}), 200
            

@advertise(scopes=['scope1', 'scope2'], rate_limit = [5000, 3600*24])
@bp.route('/example', methods=['GET'])
def api_usage():
    """
    This resource uses the request.Session to access an api that
    requires an oauth2 token, such as our own adsws. client is
    a member provided by ADS Microservice Utils
    """
    r = current_app.client.get(current_app.config.get('SAMPLE_URL'))
    return r.json()
