from fastapi import FastAPI, Path, Query, HTTPException
import json

app = FastAPI()

def load_json():
    with open("patients.json", 'r') as f:
        data = json.load(f)
        
    return data

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

@app.get("/patient_view/{patient_id}")
def patient(patient_id: str = Path(..., description='ID of the patient', example='P001')):
    data = load_json()
    if patient_id in data:
        return data[patient_id]
    else:
        raise HTTPException(status_code= 404, detail= 'Patient not found')
    
@app.get("/sort")
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