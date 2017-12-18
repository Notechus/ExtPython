from flask import Flask, jsonify, request, abort
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, TIMESTAMP
from datetime import datetime

engine = create_engine("sqlite:///contacts.db", echo=True)
Base = declarative_base()
app = Flask(__name__)


def serialize_datetime(date):
    if date is None:
        return None
    else:
        return [date.strftime("%Y-%m-%d"), date.strftime("%H:%M:%S")]


class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    phone_number = Column(String(15), nullable=False, unique=True)
    last_called = Column(TIMESTAMP, nullable=True)
    last_seen = Column(TIMESTAMP, nullable=True)

    def __repr__(self):
        return "<Contact(id='%s', name='%s', surname='%s', email='%s', phone_number='%s' , last_called='%s')>" % (
            self.id, self.name, self.surname, self.email, self.phone_number, self.last_called)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'surname': self.surname,
            'email': self.email,
            'phone_number': self.phone_number,
            'last_called': None if self.last_called is None else self.last_called.isoformat(),
            'last_seen': None if self.last_seen is None else self.last_seen.isoformat()
        }


@app.route('/')
def index():
    return "Hello! try /api/contacts"


@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    contacts = [c.serialize() for c in session.query(Contact).order_by(Contact.surname).all()]
    return jsonify(contacts)


@app.route('/api/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    contact = session.query(Contact).get(contact_id)
    return jsonify(contact.serialize())


@app.route('/api/contacts', methods=['POST'])
def create_contact():
    if not request.json:
        abort(400)
    else:
        c = Contact()
        c.name = request.json.get('name')
        c.surname = request.json.get('surname')
        c.email = request.json.get('email')
        c.phone_number = request.json.get('phone_number')
        c.last_called = request.json.get('last_called')
        c.last_seen = request.json.get('last_seen')

        session.add(c)
        session.commit()

        return 200


@app.route('/api/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    if not request.json:
        abort(400)
    else:
        c = session.query(Contact).get(contact_id)
        c.name = request.json.get('name')
        c.surname = request.json.get('surname')
        c.email = request.json.get('email')
        c.phone_number = request.json.get('phone_number')
        c.last_called = datetime.utcfromtimestamp(request.json.get('last_called'))
        c.last_seen = datetime.utcfromtimestamp(request.json.get('last_seen'))
        session.commit()

        return 200


@app.route('/api/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    c = session.query(Contact).get(contact_id)
    session.delete(c)
    session.commit()

    return 200


@app.route('/api/contacts/<int:contact_id>/see', methods=['POST'])
def see_contact(contact_id):
    c = session.query(Contact).get(contact_id)
    c.last_seen = datetime.now()
    session.commit()

    return 200


@app.route('/api/contacts/<int:contact_id>/call', methods=['POST'])
def call_contact(contact_id):
    c = session.query(Contact).get(contact_id)
    c.last_called = datetime.now()
    session.commit()

    return 200


if __name__ == '__main__':
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    app.run(debug=True)
