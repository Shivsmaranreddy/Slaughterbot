"""Local demonstration API. Bind to loopback and use fictional operational records."""
from contextlib import asynccontextmanager
from pathlib import Path
import json, os, secrets, threading
from typing import Literal
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, ConfigDict, model_validator
from build.integration.common import ROOT
from build.integration.registry import status
from build.integration.inference import infer, fuse
from build.hardware.controller import SafetyController
from . import database as db

controller=SafetyController()
control_lock=threading.Lock()

@asynccontextmanager
async def lifespan(app):
    db.initialize()
    yield
    controller.stop()

app=FastAPI(title='SLAUGHTER BOT / local experimental demo',lifespan=lifespan)

def manager(authorization: str = Header(default='')):
    expected=os.environ.get('SB_MANAGER_TOKEN','')
    if len(expected)<16:
        raise HTTPException(503,'Set SB_MANAGER_TOKEN to at least 16 characters before using manager routes')
    if not secrets.compare_digest(authorization,'Bearer '+expected):
        raise HTTPException(401,'Manager token required')

class StrictModel(BaseModel):
    model_config=ConfigDict(extra='forbid',allow_inf_nan=False)

class Order(StrictModel):
    service: Literal['demonstration sorting','demonstration positioning']
    quantity: float=Field(gt=0,le=10000)
    note: str=Field(default='',max_length=500)

class OrderUpdate(StrictModel):
    status: Literal['received','scheduled','in_progress','completed','cancelled']

class Feedback(StrictModel):
    rating: int=Field(ge=1,le=5)

class Batch(StrictModel):
    name: str=Field(min_length=1,max_length=80)
    input_kg: float=Field(gt=0,le=1000000)
    output_kg: float=Field(default=0,ge=0)
    waste_kg: float=Field(default=0,ge=0)
    status: Literal['received','in_progress','completed']='received'
    @model_validator(mode='after')
    def mass_balance(self):
        if self.output_kg+self.waste_kg>self.input_kg+1e-9:
            raise ValueError('Output plus waste exceeds input mass')
        return self

class Task(StrictModel):
    title: str=Field(min_length=1,max_length=120)
    due: str=Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    status: Literal['pending','completed']='pending'
    @model_validator(mode='after')
    def valid_date(self):
        from datetime import date
        date.fromisoformat(self.due)
        return self

class Equipment(StrictModel):
    name: str=Field(min_length=1,max_length=80)
    state: Literal['offline','mock_ready','maintenance']
    maintenance_due: str=Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    @model_validator(mode='after')
    def valid_date(self):
        from datetime import date
        date.fromisoformat(self.maintenance_due)
        return self

class Assessment(StrictModel):
    model_id: Literal['model_1_visual_cnn','model_2_ultrasound_3d','model_3_environment_rl','model_4_robotic_rl']
    relative_path: str | None=Field(default=None,max_length=300)
    observation: list[float] | None=Field(default=None,max_length=7)

class Action(StrictModel):
    action: int=Field(ge=0,le=2,strict=True)
    confidence: float=Field(ge=0,le=1)

@app.get('/api/health')
def health(): return {'status':'ok','mode':'LOCAL_DEMO','physical_hardware':False}

@app.get('/api/models')
def models():
    return [{k:r.get(k) for k in ['id','status','provenance','reason']} for r in status()]

@app.post('/api/orders')
def order_create(order:Order):
    token=db.create_order(order.service,order.quantity,order.note)
    return {'tracking_token':token,'status':'received','provenance':'demonstration'}

@app.get('/api/orders/{token}')
def order_get(token:str):
    with db.connection() as con:
        row=con.execute('SELECT * FROM orders WHERE id=?',(token,)).fetchone()
        if row is None: raise HTTPException(404,'Order not found')
        return dict(row)

@app.post('/api/orders/{token}/feedback')
def order_feedback(token:str,feedback:Feedback):
    with db.connection() as con:
        cursor=con.execute('UPDATE orders SET feedback=? WHERE id=?',(feedback.rating,token))
        if cursor.rowcount!=1: raise HTTPException(404,'Order not found')
    return {'saved':True}

@app.get('/api/manager/overview',dependencies=[Depends(manager)])
def overview():
    batches=db.rows('batches')
    return {'provenance':'demonstration','orders':db.rows('orders'),'batches':batches,
            'tasks':db.rows('tasks'),'equipment':db.rows('equipment'),
            'assessments':db.rows('assessments'),'audit':db.rows('audit'),
            'mass_balance':{'input_kg':sum(b['input_kg'] for b in batches),
                            'output_kg':sum(b['output_kg'] for b in batches),
                            'waste_kg':sum(b['waste_kg'] for b in batches)}}

@app.patch('/api/manager/orders/{token}',dependencies=[Depends(manager)])
def update_order(token:str,update:OrderUpdate):
    with db.connection() as con:
        changed=con.execute('UPDATE orders SET status=? WHERE id=?',(update.status,token))
        if changed.rowcount!=1: raise HTTPException(404,'Order not found')
        db.audit(con,'order.status',{'status':update.status})
    return {'updated':True}

@app.post('/api/manager/batches',dependencies=[Depends(manager)])
def batch_create(batch:Batch):
    with db.connection() as con:
        c=con.execute('INSERT INTO batches(name,input_kg,output_kg,waste_kg,status) VALUES(?,?,?,?,?)',tuple(batch.model_dump().values()))
        db.audit(con,'batch.created',batch.model_dump()); return {'id':c.lastrowid}

@app.put('/api/manager/batches/{batch_id}',dependencies=[Depends(manager)])
def batch_update(batch_id:int,batch:Batch):
    with db.connection() as con:
        c=con.execute('UPDATE batches SET name=?,input_kg=?,output_kg=?,waste_kg=?,status=? WHERE id=?',tuple(batch.model_dump().values())+(batch_id,))
        if c.rowcount!=1: raise HTTPException(404,'Batch not found')
        db.audit(con,'batch.updated',{'id':batch_id,**batch.model_dump()})
    return {'updated':True}

@app.post('/api/manager/tasks',dependencies=[Depends(manager)])
def task_create(task:Task):
    with db.connection() as con:
        c=con.execute('INSERT INTO tasks(title,due,status) VALUES(?,?,?)',tuple(task.model_dump().values()))
        return {'id':c.lastrowid}

@app.put('/api/manager/tasks/{task_id}',dependencies=[Depends(manager)])
def task_update(task_id:int,task:Task):
    with db.connection() as con:
        c=con.execute('UPDATE tasks SET title=?,due=?,status=? WHERE id=?',tuple(task.model_dump().values())+(task_id,))
        if c.rowcount!=1: raise HTTPException(404,'Task not found')
    return {'updated':True}

@app.post('/api/manager/equipment',dependencies=[Depends(manager)])
def equipment_create(equipment:Equipment):
    with db.connection() as con:
        c=con.execute('INSERT INTO equipment(name,state,maintenance_due) VALUES(?,?,?)',tuple(equipment.model_dump().values()))
        return {'id':c.lastrowid}

@app.post('/api/manager/assess',dependencies=[Depends(manager)])
def assess(request:Assessment):
    payload={}
    if request.relative_path:
        root=(ROOT/'output/datasets').resolve(); path=(root/request.relative_path).resolve()
        if not path.is_relative_to(root): raise HTTPException(400,'Input must be inside output/datasets')
        payload={'image_path':str(path),'volume_path':str(path)}
    if request.observation is not None: payload['observation']=request.observation
    result=fuse([infer(request.model_id,payload)])
    with db.connection() as con:
        con.execute('INSERT INTO assessments(result) VALUES(?)',(json.dumps(result),))
    return result

@app.post('/api/manager/mock/arm',dependencies=[Depends(manager)])
def arm():
    with control_lock: controller.arm_mock()
    return {'mode':'MOCK_ONLY','armed':True}

@app.post('/api/manager/mock/stop',dependencies=[Depends(manager)])
def stop():
    with control_lock: controller.stop()
    return {'emergency_stop':True}

@app.post('/api/manager/mock/action',dependencies=[Depends(manager)])
def action(request:Action):
    with control_lock: result=controller.execute(request.action,request.confidence)
    with db.connection() as con: db.audit(con,'mock.action',result)
    return result

@app.get('/')
@app.get('/customer')
def customer(): return FileResponse(ROOT/'build/interfaces/customer_ui/index.html')

@app.get('/manager')
def dashboard(): return FileResponse(ROOT/'build/interfaces/msme_manager/index.html')

@app.get('/enterprise')
def enterprise(): return FileResponse(ROOT/'build/interfaces/enterprise_manager/index.html')
