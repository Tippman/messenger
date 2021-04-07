from icecream import ic
from db.client_db import Client, ClientStorage
from db.client_history_db import ClientHistory, ClientHistoryStorage
from db.base import Base

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine, select
from sqlalchemy.orm import mapper
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///messenger.sqlite3', echo=False)


from sqlalchemy.orm import sessionmaker
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


# Класс Session будет создавать Session-объекты, которые привязаны к базе данных
session = Session()

# client_storage = ClientStorage(session)
# client_storage.add_client(login='asdf', password='1234')
# new_user = select(Client).where(Client.login == 'asdf')
# result = session.execute(new_user)
# client_exists = client_storage.is_client_exist('asdf')
# ic(client_exists)
# ic(client_storage.check_auth_data(login='asdf', password='1234'))

client_history_storage = ClientHistoryStorage(session)
client_history_storage.add_record(client_id=1, ip_address='123.123.123.123')

session.close()
# for user_obj in result.scalars():
#     ic(user_obj.login)