from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, String, Date, DateTime, Float, Boolean, Text)
from scrapy.utils.project import get_project_settings

Base = declarative_base()


def db_connect():

    return create_engine(get_project_settings().get("DATABASE_URL"))




class Quote(Base):
    __tablename__ = "main_quote"

    id = Column(Integer, primary_key=True)
    url_content = Column('text', Text())
    job_data_id = Column('job_data_id', Integer())


class URL_details(Base):
    __tablename__ = "main_url_details"

    id = Column(Integer, primary_key=True)
    job_data_id = Column('job_data_id', Integer())
    site_name = Column('site_name', Text())
    total_violations = Column('total_violations', Text())
    total_verify = Column('total_verify', Text())
    total_pass = Column('total_pass', Text())
    total_score = Column('total_score', Text())





