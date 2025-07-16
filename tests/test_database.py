## Test cases for database SQLite using in memory database fixture from conftest.py
#

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select #, SQLModel, create_engine
#from sqlmodel.pool import StaticPool
from app.services.database.database import get_session 
 

def test_read_test(session: Session, test_model_class):
    test_entry_1 = test_model_class(id=1, test_index_string="index_string1", test_string="string1")  
    session.add(test_entry_1)
    session.commit()
    
    statement = select(test_model_class)
    results = session.exec(statement)
    
    data = results.first()

    assert data.test_index_string == test_entry_1.test_index_string
    assert data.test_string == test_entry_1.test_string
    assert data.id == test_entry_1.id

''' 
def test_update_hero(session: Session, client: TestClient):
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
    session.add(hero_1)
    session.commit()

    response = client.patch(f"/heroes/{hero_1.id}", json={"name": "Deadpuddle"})
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Deadpuddle"
    assert data["secret_name"] == "Dive Wilson"
    assert data["age"] is None
    assert data["id"] == hero_1.id


def test_delete_hero(session: Session, client: TestClient):
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
    session.add(hero_1)
    session.commit()

    response = client.delete(f"/heroes/{hero_1.id}")

    hero_in_db = session.get(Hero, hero_1.id)

    assert response.status_code == 200

    assert hero_in_db is None
    '''