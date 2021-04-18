from icecream import ic
from db.client_db import Client, ClientStorage
from db.base import Base
from lib.variables import ENGINE
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine, select
from sqlalchemy.orm import mapper
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///messenger.sqlite3', echo=True)

from sqlalchemy.orm import sessionmaker

Base.metadata.create_all(ENGINE)
Session = sessionmaker(bind=ENGINE)

# Класс Session будет создавать Session-объекты, которые привязаны к базе данных
session = Session()

# client_storage = ClientStorage(session)
# client_storage.add_client(login='asdf', password='1234')
# new_user = select(Client).where(Client.login == 'asdf')
# result = session.execute(new_user)
# client_exists = client_storage.is_client_exist('asdf')
# ic(client_exists)
# ic(client_storage.check_auth_data(login='tippman', password='1234'))

# client_history_storage = ClientHistoryStorage(session)
# client_history_storage.add_record(client_id=1, ip_address='123.123.123.123')
#
# client = session.query(Client).filter(Client.login == 'tippman').one()
# ic('login %s pass %s', client.login, client.password)
# client_history = client.ClientHistory
# ic(client_history)

with session.begin():
    # all_clients = session.query(Client).all()
    # ic(all_clients[1].__dict__)

    client = session.query(Client).filter(Client.login=="tippman").one()
    ic(type(client.contacts.all()))
    ic([c.login for c in client.contacts.all()])
    target = ClientStorage(session).get_client('friend2')
    ic(target in client.contacts.all())


    # target = session.query(Client).filter(Client.login=="friend2").one()
    # client.contacts.remove(target)
    # client = Client(login='login', password='password')
    # friend1 = Client(login='friend1', password='password')
    # friend2 = Client(login='friend2', password='password')
    # session.add(client)
    # session.add(friend1)
    # session.add(friend2)
    # client = session.query(Client).filter(Client.login == 'login').one()
    # fr1 = Client(login='fr1')
    # fr2 = Client(login='fr2')
    # client.contact.append(friend1)
    # client.contact.append(friend2)




# session.close()
# for user_obj in result.scalars():
#     ic(user_obj.login)
