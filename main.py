from fastapi import FastAPI, Path, Query, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional #allow a field to have one of the value in Literal 
import json

app = FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(..., description='ID of the patient', examples=['P001'])]
    name: Annotated[str, Field(..., description='Name of the patient')]
    city: Annotated[str, Field(..., description='City of the patient')]
    age: Annotated[int, Field(..., gt=0, lt=120, description='Age of the patient')]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description='Gender of the patient')]
    height: Annotated[float, Field(..., gt=0, description='height of the patient in mtrs')]
    weight: Annotated[float, Field(..., gt=0, description='Weight of the patient in kgs')]
    
    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2), 2)
        return bmi
        
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'
    
    
class Patient_update(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(gt=0, default=None)]
    gender: Annotated[Optional[Literal['male', 'female', 'others']], Field(default=None)]
    height: Annotated[Optional[float], Field(gt=0, default=None)]
    weight: Annotated[Optional[float], Field(gt=0, default=None)]
    
def load_json():
    with open("patients.json", 'r') as f:
        data = json.load(f)
        
    return data

def save_json(data):
    with open("patients.json", 'w') as f:
        json.dump(data, f)

@app.get("/")
def Hello():
    return {'message': 'Patient management system API'}

@app.get("/about")
def about():
    return{'message': 'A fully functional API to manage patient record'}

@app.get("/view")
def view():
    data = load_json()  
    return data

@app.get("/patient_view/{patient_id}") #path parameter
def patient(patient_id: str = Path(..., description='ID of the patient', example='P001')):
    data = load_json()
    if patient_id in data:
        return data[patient_id]
    else:
        raise HTTPException(status_code= 404, detail= 'Patient not found')
    
@app.get("/sort")  #query parameter
def sort_data(sort_by: str = Query(..., description='Sort on the basis of Height, Weight, bmi'), order:str = Query('asc', description='order by either asc or desc')):
    
    sort_value = ['height', 'weight', 'bmi']
    
    if sort_by not in sort_value:
        raise HTTPException(status_code=400, detail='Invalid sort')
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail='Invalid order')
    
    data = load_json()
    sort_order = True if order =='desc' else False
    
    sorted_data = sorted(data.values(), key = lambda x: x.get(sort_by, 0), reverse=sort_order)
    return sorted_data

@app.post('/create')
def create_patient(patient: Patient):
    
    #load existing data
    data = load_json()
    
    #check if patient already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient already exists")
    
    #add new patient to the database
    data[patient.id] = patient.model_dump(exclude=['id'])
    
    #save into the json file
    save_json(data)
    
    return JSONResponse(status_code=200, content={'message': 'patient created successfully'})

@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: Patient_update):
    data = load_json()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    existing_info = data[patient_id]
    
    updated_info = patient_update.model_dump(exclude_unset= True)
    
    for key, value in updated_info.items():
        existing_info[key] = value
    
    
    #convert existing info to pydantic object to get updated bmi and verdict and again convert to dict
    existing_info['id'] = patient_id
    existing_info_obj = Patient(**existing_info)
    
    existing_info = existing_info_obj.model_dump(exclude=['id'])
    
    data[patient_id] = existing_info
    
    save_json(data)
    
    return JSONResponse(status_code=200, content={'message': 'patient updated successfully'})

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):
    data = load_json()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    del data[patient_id]
    
    save_json(data)
    return JSONResponse(status_code=200, content={'message': 'patient deleted successfully'})
    