import pandas as pd
from fastapi.exceptions import HTTPException
import os
import json
def addnewdata(name,data,id):
    try:
        existing_csv_file = f'./Csvdata/{id}.csv'
        if os.path.exists(existing_csv_file):
            df = pd.read_csv(existing_csv_file)
            a=df.to_json()
            b=json.loads(a)
            iddata=list(b['id'].values())
            rid=iddata[len(iddata)-1]+1
        else:
            rid=1
            columns = ['id','name', 'data']
            df = pd.DataFrame(columns=columns)
        new_entry = pd.DataFrame({'id':rid,'name': [name], 'data': [data]})
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(existing_csv_file, index=False)
        a= os.path.dirname(os.path.abspath(__file__))+f'\Csvdata\{id}.csv'
        return str(a)
    except Exception as e:
        raise HTTPException(status_code=300, detail=e)

def Getcsvdataformat(path):
    print(path)
    if os.path.exists(path):
        df=pd.read_csv(path)
        a=df.to_json()
        b=json.loads(a)
        d=list(b.keys())
        id=list(b[d[0]].values())
        name=list(b[d[1]].values())
        data=list(b[d[2]].values())
        res=[]
        for i in range(len(name)):
            res.append({'id':id[i],'name':name[i],'data':data[i]})
        return res
    else:
        raise HTTPException(status_code=300, detail='CSV file does not exist')
    
def Updatecsvdata(name,id,data,fileid):
    path=f'./Csvdata/{fileid}.csv'
    if os.path.exists(path):
        df=pd.read_csv(path)
        index_to_edit = df.loc[df['id'] == id].index[0]
        df.loc[index_to_edit, 'name'] = name
        df.loc[index_to_edit, 'data'] = data
        df.to_csv(path, index=False)
        return {'details':"Successfully edited"}
    else:
        raise HTTPException(status_code=300, detail='CSV file does not exist')
def Deletecsvdata(id,fileid):
    path=f'./Csvdata/{fileid}.csv'
    if os.path.exists(path):
        df=pd.read_csv(path)
        df = df.drop(df[df['id'] == id].index)
        df.to_csv(path, index=False)
        return {'details':"Successfully Data Deleted"}
    else:
        raise HTTPException(status_code=300, detail='CSV file does not exist')
