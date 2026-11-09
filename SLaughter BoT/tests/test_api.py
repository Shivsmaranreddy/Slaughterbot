import pytest
from fastapi.testclient import TestClient
from build.backend.app import app, controller
from build.backend import database

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(database,'DB',tmp_path/'test.db')
    monkeypatch.setenv('SB_MANAGER_TOKEN','test-manager-token-123456')
    controller.stop()
    with TestClient(app) as c: yield c

HEADERS={'Authorization':'Bearer test-manager-token-123456'}

def test_order_workflow(client):
    r=client.post('/api/orders',json={'service':'demonstration sorting','quantity':2,'note':'blue inert cubes'})
    assert r.status_code==200
    token=r.json()['tracking_token']
    assert client.patch('/api/manager/orders/'+token,json={'status':'completed'}).status_code==401
    assert client.patch('/api/manager/orders/'+token,json={'status':'completed'},headers=HEADERS).status_code==200
    assert client.get('/api/orders/'+token).json()['status']=='completed'
    assert client.post('/api/orders/'+token+'/feedback',json={'rating':5}).status_code==200

def test_bad_mass_rejected(client):
    r=client.post('/api/manager/batches',headers=HEADERS,json={'name':'demo','input_kg':1,'output_kg':1,'waste_kg':1})
    assert r.status_code==422

def test_missing_model_and_traversal(client):
    r=client.post('/api/manager/assess',headers=HEADERS,json={'model_id':'model_1_visual_cnn'})
    assert r.json()['perception'][0]['status']=='ABSTAIN'
    r=client.post('/api/manager/assess',headers=HEADERS,json={'model_id':'model_1_visual_cnn','relative_path':'../../README.md'})
    assert r.status_code==400

def test_pages_and_safety(client):
    for path in ['/customer','/manager','/enterprise']:
        assert client.get(path).status_code==200
    client.post('/api/manager/mock/arm',headers=HEADERS)
    client.post('/api/manager/mock/stop',headers=HEADERS)
    r=client.post('/api/manager/mock/action',headers=HEADERS,json={'action':2,'confidence':1})
    assert not r.json()['accepted']
