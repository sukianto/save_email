#!m_venv/bin/python

#date
import pytz
from datetime import datetime

#flask
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import request
from flask import abort

#cache
from werkzeug.contrib.cache import MemcachedCache


app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

cache = MemcachedCache(['localhost:6379'])


class Email(db.Model):
    email_id = db.Column(db.Integer, primary_key=True)
    email_addr = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return '<Event %r>' % self.email_subject

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.email_id,
            'email_addr': self.email_addr,

        }


@app.route('/save_emails', methods=['POST'])
def save_emails():
    #validation
    if not request.json or not 'event_id' in request.json:
        abort(400)

    if not request.json or not 'email_subject' in request.json:
        abort(400)

    if not request.json or not 'email_content' in request.json:
        abort(400)

    if not request.json or not 'timestamp' in request.json:
        abort(400)

    if not request.json or not 'email_address' in request.json:
        abort(400)

    #save email to database
    email = Email(email_addr=request.json['email_address'])
    db.session.add(email)
    db.session.commit()

    #calculate trigger time
    tz = pytz.timezone('Asia/Singapore')
    trigger_time = datetime.now(tz) - datetime.strptime(request.json['timestamp'], '%d %b %Y %H:%M')

    #set cache
    cache.set('email_event', "[{0},{1},{2}]".format(
        request.json['email_address'], request.json['email_subject'], request.json['email_content']
    ), timeout=trigger_time)

    return jsonify(
        [i.serialize for i in Email.query.filter_by(email_addr=request.json['email_address'])]
    ), 201


if __name__ == '__main__':
    app.run(debug=True)
