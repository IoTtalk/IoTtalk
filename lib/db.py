
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from ec_config import SQLITE_PATH, MYSQL_HOST, MYSQL_USER, MYSQL_PASS

Base = declarative_base()
engine = None

def connect(db_name):
    global engine

    if db_name.startswith('sqlite:'):
        url = 'sqlite+pysqlite:///' + SQLITE_PATH + '/' + db_name[7:]
    else:
        url = 'mysql+mysqlconnector://' + MYSQL_USER + ':'\
            + MYSQL_PASS + '@' + MYSQL_HOST + '/' + db_name

    engine = create_engine(url, pool_recycle=3600)


def create():
    if not engine:
        raise Exception('You should invoke connect(db_name) first.')
    Base.metadata.create_all(engine)
    

def get_session():
    if not engine:
        raise Exception('You should invoke connect(db_name) first.')
    return Session(engine)


##############################################################################
#####                                 schema                             #####
##############################################################################
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, Text, Float, Boolean, String, Enum, Date
from sqlalchemy.ext.declarative import declarative_base


class User(Base):           # not describe in document.
    __tablename__ = 'User'
    __table_args__ = {'sqlite_autoincrement': True}
    u_id = Column(Integer, primary_key=True, nullable=False)
    u_name = Column(String(255), nullable=False)
    passwd = Column(String(255), nullable=False)


class DeviceFeature(Base):
    __tablename__ = 'DeviceFeature'
    __table_args__ = {'sqlite_autoincrement': True}
    df_id = Column(Integer, primary_key=True, nullable=False)
    df_name = Column(String(255), nullable=False)
    df_type = Column(Enum('input', 'output'), nullable=False)
    df_category = Column(Enum('Sight', 'Hearing', 'Feeling', 'Motion', 'Other'), nullable=False)
    param_no = Column(Integer, nullable=False)
    comment = Column(Text, nullable=False)  # not describe in document.

class DeviceModel(Base):
    __tablename__ = 'DeviceModel'
    __table_args__ = {'sqlite_autoincrement': True}
    dm_id = Column(Integer, primary_key=True, nullable=False)
    dm_name = Column(String(255), nullable=False)
    dm_type = Column(Enum('smartphone', 'wearable', 'other'), nullable=False)   # not use now.


class DM_DF(Base):
    __tablename__ = 'DM_DF'
    __table_args__ = {'sqlite_autoincrement': True}
    mf_id = Column(Integer, primary_key=True, nullable=False)
    dm_id = Column(Integer, ForeignKey('DeviceModel.dm_id'), nullable=False)
    df_id = Column(Integer, ForeignKey('DeviceFeature.df_id'), nullable=False)

class Unit(Base):
    __tablename__ = 'Unit'
    __table_args__ = {'sqlite_autoincrement': True}
    unit_id = Column(Integer, primary_key=True, nullable=False)
    unit_name = Column(String(255), nullable=False)

class DF_Parameter(Base):
    __tablename__ = 'DF_Parameter'
    __table_args__ = {'sqlite_autoincrement': True}
    dfp_id = Column(Integer, primary_key=True, nullable=False)
    df_id = Column(Integer, ForeignKey('DeviceFeature.df_id'))
    mf_id = Column(Integer, ForeignKey('DM_DF.mf_id'))
    param_i = Column(Integer, nullable=False)       # start from 0
    param_type = Column(Enum('int', 'float', 'boolean', 'void', 'string', 'json'), nullable=False)
    u_id = Column(Integer, ForeignKey('User.u_id'))
    idf_type = Column(Enum('variant', 'sample'))
    min = Column(Float, default=0)
    max = Column(Float, default=0)
    normalization = Column(Boolean, default=0, nullable=False)
    unit_id = Column(Integer, ForeignKey('Unit.unit_id'), nullable=False, default=1) # 1 is None, need to change


class Device(Base):
    __tablename__ = 'Device'
    __table_args__ = {'sqlite_autoincrement': True}
    d_id = Column(Integer, primary_key=True, nullable=False)
    mac_addr = Column(String(255), nullable=False)
    monitor = Column(String(255), nullable=False)       # not describe in document.
    d_name = Column(String(255), nullable=False)
    status = Column(Enum('online', 'offline'), nullable=False)
    u_id = Column(Integer, ForeignKey('User.u_id'))
    dm_id = Column(Integer, ForeignKey('DeviceModel.dm_id'), nullable=False)


class Project(Base):
    __tablename__ = 'Project'
    __table_args__ = {'sqlite_autoincrement': True}
    p_id = Column(Integer, primary_key=True, nullable=False)
    p_name = Column(String(255), nullable=False)    # not describe in document.
    u_id = Column(Integer, ForeignKey('User.u_id'), nullable=False) # not describe in document.
    status = Column(Enum('on', 'off'), nullable=False)
    restart = Column(Boolean, nullable=False)       # shortcut
    exception = Column(Text, nullable=False)        # for debug
    sim = Column(Enum('on', 'off'), nullable=False)
    pwd = Column(String(32), nullable=False)    # password


class NetworkApplication(Base):
    __tablename__ = 'NetworkApplication'
    __table_args__ = {'sqlite_autoincrement': True}
    na_id = Column(Integer, primary_key=True, nullable=False)
    na_name = Column(String(255), nullable=False)
    na_idx = Column(Integer, nullable=False)        # not describe in document.
    p_id = Column(Integer, ForeignKey('Project.p_id'), nullable=False)


class DeviceObject(Base):
    __tablename__ = 'DeviceObject'
    __table_args__ = {'sqlite_autoincrement': True}
    do_id = Column(Integer, primary_key=True, nullable=False)
    dm_id = Column(Integer, ForeignKey('DeviceModel.dm_id'), nullable=False)
    p_id = Column(Integer, ForeignKey('Project.p_id'), nullable=False)
    do_idx = Column(Integer, nullable=False)
    d_id = Column(Integer, ForeignKey('Device.d_id'))


class DFObject(Base):
    __tablename__ = 'DFObject'
    __table_args__ = {'sqlite_autoincrement': True}
    dfo_id = Column(Integer, primary_key=True, nullable=False)
    do_id = Column(Integer, ForeignKey('DeviceObject.do_id'), nullable=False)
    df_id = Column(Integer, ForeignKey('DeviceFeature.df_id'), nullable=False)
    alias_name = Column(String, nullable=False)


class DF_Module(Base):
    __tablename__ = 'DF_Module'
    __table_args__ = {'sqlite_autoincrement': True}
    na_id = Column(Integer, ForeignKey('NetworkApplication.na_id'), primary_key=True, autoincrement=False, nullable=False)
    dfo_id = Column(Integer, ForeignKey('DFObject.dfo_id'), primary_key=True, autoincrement=False, nullable=False)
    param_i = Column(Integer, primary_key=True, autoincrement=False, nullable=False)
    idf_type = Column(Enum('variant', 'sample'))
    min = Column(Float, default=0)
    max = Column(Float, default=0)
    normalization = Column(Boolean, default=0, nullable=False)
    color = Column(Enum('red', 'black'), nullable=False)    # not describe in document.


class MultipleJoin_Module(Base):
    __tablename__ = 'MultipleJoin_Module'
    __table_args__ = {'sqlite_autoincrement': True}
    na_id = Column(Integer, ForeignKey('NetworkApplication.na_id'), primary_key=True, autoincrement=False, nullable=False)
    param_i = Column(Integer, primary_key=True, autoincrement=False, nullable=False)
    dfo_id = Column(Integer, ForeignKey('DFObject.dfo_id'), nullable=False)

