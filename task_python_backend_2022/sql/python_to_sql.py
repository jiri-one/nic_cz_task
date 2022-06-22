from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base
# from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy import select

Base = declarative_base()

class Domain(Base):
    __tablename__ = "domain"
    id = Column(Integer, primary_key=True)
    domain_name = Column(String(63)) # max domain name length is 63 chars
    registred = Column(DateTime, default=datetime.utcnow) # or some date and time
    unregistred = Column(DateTime)

class DomainFlag(Base):
    __tablename__ = "domain_flag"
    id = Column(Integer, primary_key=True)
    domain_name = Column(Integer, ForeignKey("domain.domain_name"))
    expired = Column(Boolean, default=False)
    outzone = Column(Boolean, default=False)
    delete_candidate = Column(Boolean, default=False)

engine = create_engine("sqlite://", echo=True, future=True) # now I am on Windows (my business notebook) and is really difficult to setup postgresql here :).
Base.metadata.create_all(engine)

print(select(Domain.domain_name, DomainFlag.domain_name).where(Domain.registred == True, DomainFlag.expired == False))
print(select(DomainFlag.domain_name).filter((DomainFlag.expired == True) | (DomainFlag.outzone == True)))
