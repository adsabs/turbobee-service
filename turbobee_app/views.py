import pdb
from flask import url_for, current_app, request, Blueprint, jsonify
from flask import json
from flask_discoverer import advertise
from adsmsg import TurboBeeMsg
from models import Pages
import datetime as dt
import hashlib
from sqlalchemy import exc
from sqlalchemy.orm import load_only
import uuid
from adsmutils import get_date

bp = Blueprint('turbobee_app', __name__)




@advertise(scopes=['ads-consumer:turbobee'], rate_limit = [1000, 3600*24])
@bp.route('/', methods=['POST'])
@bp.route('/<string:qid>', methods=['GET', 'POST', 'DELETE'])
def store(qid=None):
    
    if request.method == 'GET':
        with current_app.session_scope() as session:
            page = session.query(Pages).filter_by(qid=qid).first()
            if not page:
                return jsonify({'qid': qid, 'msg': 'Not found'}), 404
            return current_app.wrap_response(page)
    elif request.method == 'POST':
        out = {}
        if not request.files:
            return jsonify({'qid': qid, 'msg': 'Invalid params, missing data stream'}), 501
        
        # there might be many objects in there...
        msgs = []
        for _, fo in request.files.items():
            
            if not hasattr(fo, 'read'):
                continue # not a file object
            
            # assuming we are not going to crash...(?)
            msg = TurboBeeMsg.loads('adsmsg.turbobee.TurboBeeMsg', fo.read())
            msgs.append(msg)
            
        out = []
        if len(msgs):
            out = current_app.set_pages(msgs)
        
        if 'errors' in out:
            return jsonify(out), 400
        return jsonify(out), 200
    
    elif request.method == 'DELETE':
        with current_app.session_scope() as session:
            pages = session.query(Pages).options(load_only('qid')).filter_by(qid=qid).first()
        
            qid = None
            if not pages:
                return jsonify({'qi': qid, 'msg': 'Not found'}), 404
            else:
                qid = pages.qid
                session.delete(pages)

            try:
                session.commit()
            except exc.IntegrityError as e:
                session.rollback()

            return jsonify({'qid': qid, 'status': 'deleted'}), 200


# convert datestring s to datetime object
def str_to_dt(s):
    return dt.datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f')


@advertise(scopes=['ads-consumer:turbobee'], rate_limit = [1000, 3600*24])
@bp.route('/search', methods=['GET'])
def search():

    keys = request.args.keys()

    # default is 50, max is 100
    rows = min(current_app.config.get('MAX_RETURNED', 100), int(request.args.get('rows') or 50)) 
    with current_app.session_scope() as session:

        if 'begin' in keys and 'end' in keys:
            begin = str_to_dt(request.args['begin'])
            end = str_to_dt(request.args['end'])
            query = session.query(Pages).filter(Pages.created.between(begin, end))
        elif 'begin' in keys: # search for all records after begin
            begin = str_to_dt(request.args['begin'])
            query = session.query(Pages).filter(Pages.created >= begin)
        elif 'end' in keys: # search for all records before end
            end = str_to_dt(request.args['end'])
            query = session.query(Pages).filter(Pages.created <= end)
        elif 'at' in keys: # search for all records created at specific timestamp
            at = str_to_dt(request.args['at'])
            query = session.query(Pages).filter(Pages.created == at)
        else:
            return jsonify({'msg': 'Invalid parameters %s' % keys}), 505
            
        query = query.order_by(Pages.updated.asc()) \
            .limit(rows)
            
        if 'fields' in keys: # load only some fields
            allowed_fields = ['qid', 'created', 'updated', 'expires', 'lifetime',
                              'content_type', 'content']
            fields = keys.get('fields', allowed_fields)
            fields_to_load = list(set(fields) & set(allowed_fields))
            query = query.options(load_only(*fields_to_load))

        try:
            pages = query.all()
            # it is possible that toJSON() will eagerly load all fields (defeating load_only() above)
            result = map(lambda page: page.toJSON(), pages) 
            return jsonify(result)
        except Exception as e:
            current_app.logger.error('Failed request: %s (error=%s)', keys, e)
            return jsonify({'msg': e.message}), 500

            




