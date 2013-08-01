from flask import Flask
from flask import request, make_response, request, current_app, jsonify
from werkzeug import secure_filename

import boto
from boto.s3.key import Key

import os
import uuid
from functools import update_wrapper
from datetime import timedelta
from ConfigParser import SafeConfigParser

app = Flask(__name__)
config = SafeConfigParser()
config.read('config.ini')

ALLOWED_EXTENSIONS = set(config.get('app', 'ALLOWED_FILETYPES').split(','))
AWS_KEY = config.get('app', 'AWS_KEY')
AWS_SECRET = config.get('app', 'AWS_SECRET')
AWS_BUCKET = config.get('app', 'AWS_BUCKET')
UPLOAD_FOLDER = config.get('app', 'UPLOAD_FOLDER')
app.debug = config.get('app', 'DEBUG')

def allowed_file(filename):
    """ Checks if a set of file extentions are allowed """
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    """ Decorator to add origin to Access-Control-Allow-Origin headers """
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


@app.route('/upload', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*', headers='Access-Control-Allow-Origin')
def upload():
    """ Upload controller """

    print 'Starting upload...'
    if request.method == 'POST':
        image = request.files['file']
        print 'File obtained...'

        if allowed_file(image.filename):
            print 'Image allowed.'
            filename = secure_filename(image.filename)
            image.save(os.path.join(UPLOAD_FOLDER, filename))

            print 'Uploading to s3...'
            conn = boto.connect_s3(AWS_KEY, AWS_SECRET)
            b = conn.get_bucket(AWS_BUCKET)
            k = Key(b)

            print 'Setting key...'
            k.key = '%s_%s' % (uuid.uuid4(), filename)
            k.set_contents_from_filename(UPLOAD_FOLDER + filename)

            print 'Making public...'
            k.make_public
            k.set_acl('public-read')

            print 'Responding to request...'
            return jsonify(status='Success.')
        else:
            print 'File not allowed.'
            return jsonify(status='File not allowed.')
    else:
        print 'Upload failed.'
        return jsonify(status='fail')

if __name__ == '__main__':
    app.run()
