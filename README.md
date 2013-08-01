# s3-uploader

*s3-uploader* is a simple Flask app which uploads arbitrary *allowed* files to an Amazon S3 bucket.

## Configure

- Open config.ini.sample and set the following:

```ini
[app]
ALLOWED_FILETYPES = png,jpg,jpeg,JPG,JPEG,PNG ;No spaces
AWS_KEY = awskey
AWS_SECRET = awssecret
AWS_BUCKET = bucketname
UPLOAD_FOLDER = /tmp/
DEBUG = True ;Set to false if using in a production environment
```
- Rename `config.ini.sample` to `config.ini`
- `pip install -r requirements.txt` to install dependencies
- `python s3-uploader.py` to start the app
- `curl --form "fileupload=@filename.jpg" http://127.0.0.1:5000/upload` to test a file upload

## Notes

Running the development server locally is usually just for development. It is recommended to deploy
the app using a proper server such as gunicorn or uWSGI behind nginx (or apache). Refer to the 
[Flask Documentation](http://flask.pocoo.org/docs/deploying/) for deployment options.

I created this app to fulfill the backend of my 
[jquery-file-upload-simplified](https://github.com/alfg/jquery-file-upload-simplified) demo.


## License
Released under the [MIT license](http://www.opensource.org/licenses/MIT).
