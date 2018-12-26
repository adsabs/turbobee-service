import pdb
from flask import url_for, current_app, request, Blueprint, jsonify
from flask import json
from flask_discoverer import advertise
from adsmsg import TurboBeeMsg
from models import Pages
import datetime as dt
from sqlalchemy import exc
from sqlalchemy.orm import load_only
from adsmutils import get_date
import dateutil.parser
import base64

bp = Blueprint('turbobee_app', __name__)



@advertise(scopes=[], rate_limit = [1000, 3600*24])
@bp.route('/<string:qid>', methods=['GET', 'HEAD'])
def store_get(qid=None):
    if request.method == 'GET':
        with current_app.session_scope() as session:
            page = session.query(Pages).filter_by(qid=qid).first()
            if not page:
                return jsonify({'qid': qid, 'msg': 'Not found'}), 404
            return current_app.wrap_response(page)
    elif request.method == 'HEAD':
        with current_app.session_scope() as session:
            # TODO: make it more efficient
            page = session.query(Pages).filter_by(qid=qid).options(load_only('id')).first()
            if page:
                return '', 200
            else:
                return '', 404


@advertise(scopes=['ads-consumer:turbobee'], rate_limit = [1000, 3600*24])
@bp.route('/update', methods=['POST'])
@bp.route('/update/<string:qid>', methods=['POST', 'DELETE'])
def store(qid=None):
    
    if request.method == 'POST':
        out = {}
        
        # there might be many objects in there...
        msgs = []
        for _, fo in request.files.items():
            
            if not hasattr(fo, 'read'):
                continue # not a file object
            
            # on error, we'll crash early; that's OK
            msg = TurboBeeMsg.loads('adsmsg.turbobee.TurboBeeMsg', fo.read())
            msgs.append(msg)
        
        # also read data posted the normal way
        for k, v in request.form.items():
            msg = TurboBeeMsg.loads('adsmsg.turbobee.TurboBeeMsg', base64.decodestring(v))
            msgs.append(msg)
        
        if not len(msgs):
            return jsonify({'msg': 'Empty stream, no messages were received'}), 501
            
            
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


@advertise(scopes=['ads-consumer:turbobee'], rate_limit = [1000, 3600*24])
@bp.route('/search', methods=['GET'])
def search():

    keys = request.args.keys()

    # default is 50, max is 100
    rows = min(current_app.config.get('MAX_RETURNED', 100), int(request.args.get('rows') or 50)) 
    with current_app.session_scope() as session:

        if 'begin' in keys and 'end' in keys:
            begin = dateutil.parser.parse(request.args['begin'])
            end = dateutil.parser.parse(request.args['end'])
            query = session.query(Pages).filter(Pages.created.between(begin, end))
        elif 'begin' in keys: # search for all records after begin
            begin = dateutil.parser.parse(request.args['begin'])
            query = session.query(Pages).filter(Pages.created >= begin)
        elif 'end' in keys: # search for all records before end
            end = dateutil.parser.parse(request.args['end'])
            query = session.query(Pages).filter(Pages.created <= end)
        elif 'at' in keys: # search for all records created at specific timestamp
            at = dateutil.parser.parse(request.args['at'])
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

