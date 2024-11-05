#!/usr/bin/env python
# coding: utf-8

# In[10]:


import pandas as pd
import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, text, types
import traceback
import chardet
from sqlalchemy.exc import DataError


# In[28]:


from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
import uvicorn
from typing import List


# In[7]:


import sqlalchemy
import json
import re


# In[17]:


def createEngine(filePath, paramTablename):
    try:
        testData = pd.read_csv(filePath + paramTablename)
        paramDict = {}
        for i in range(0, len(testData)):
            paramDict[testData.iloc[i, 1]] = testData.iloc[i, 2]; ####### 1,2 말고 column에서 '%like%'비슷하게 하는거 뭐 없는지
        dbPrefix = paramDict['dbPrefix']
        dbID = paramDict['id']
        dbPw = paramDict['pw']
        dbIp = paramDict['ip']
        dbPort = paramDict['port']
        dbName = paramDict['dbName']

        if dbPrefix == "oracle+cx_oracle":
            engine = create_engine('oracle+cx_oracle://{}:{}@{}:{}/{}'.format(dbID,dbPw,dbIp,dbPort,dbName))
        elif dbPrefix == "postgresql":
            engine = create_engine(f"{dbPrefix}://{dbID}:{dbPw}@{dbIp}:{dbPort}/{dbName}")
        elif dbPrefix == "mysql+pymysql" : 
            engine = create_engine(f"{dbPrefix}://{dbID}:{dbPw}@{dbIp}:{dbPort}/{dbName}")
        elif dbPrefix == "mariadb":
            engine = create_engine(f'mysql+pymysql://{dbID}:{dbPw}@{dbIp}:{dbPort}/{dbName}')
        else :
            print(f"{dbPrefix} 엔진을 실행하기 위해서는 추가적인 코드를 작성해야 합니다.")
        
        return engine
    except Exception as e:
        print("[ERROR] : ", e)


# In[12]:


def importFileToTable(filePath, targetName):
    try:
        files = os.listdir(filePath)
        for filename in files:
            if filename == targetName:
                # 확장자 부분 잘라내서 이름이랑 확장자로 저장
                tableName, file_extension = os.path.splitext(filename)
                # 테이블명에 특수문자 있으면 _로 바꾸고, 소문자로 전환
                tableName = re.sub(r'\W+', '_', tableName)
                tableName = tableName.lower()
                # 파일 확장자 체크하는 부분
                if file_extension.lower() not in ['.txt', '.csv']:
                    print(f"{filename} 파일은 지원되지 않는 형식입니다.")
                    continue
                else:
                    # 파일 인코딩 감지
                    full_path = os.path.join(filePath, filename)
                    encoding = detect_encoding(full_path)
                    inData = pd.read_csv(full_path, encoding=encoding, low_memory=False)
                    columns = list(inData.columns)
                    
                # column 순회하면서 형태 체크해서 typeDict에 담아줌
                typeDict = {}
                for column in columns:
                    if inData[column].dtypes == 'float64':
                        typeDict[column] = Float
                    elif inData[column].dtypes == 'int64':
                        typeDict[column] = Integer
                    else:
                        typeDict[column] = String(100)
    
                # SQLAlchemy를 사용하여 table 객체 생성
                metadata = MetaData()
                columns = [Column(column, typeDict[column]) for column in inData.columns]
                table = Table(tableName, metadata, *columns)
                # table 객체를 사용해서 쿼리 작성하고 utf8mb4 형식으로 변경
                with engine.connect() as conn:
                    conn.execute(text(f"DROP TABLE IF EXISTS {tableName}"))
                    table.create(bind=engine)
                    conn.execute(text(f"ALTER TABLE {tableName} CONVERT TO CHARACTER SET utf8mb4"))
    
                # csv에서 추출한 indata를 db에 생성한 table에 append
                try:
                    inData.to_sql(name=tableName, if_exists="append", con=engine, index=False)
                except DataError as e:
                    print("[DataError]: ", e)
                    error_message = str(e)
                    # 정규 표현식을 사용하여 컬럼 이름 추출
                    match = re.search(r"for column ['\"]?(\w+)['\"]?", error_message)
                    if match:
                        problematic_column = match.group(1)
                        # 테이블 이름 제거 (필요한 경우)
                        if "." in problematic_column:
                            problematic_column = problematic_column.split(".")[-1]
                        # 쿼리 작성
                        print(f"Changing column: {problematic_column} to String(100)")
                        with engine.connect() as conn:
                            conn.execute(text(f"ALTER TABLE {tableName} MODIFY COLUMN `{problematic_column}` VARCHAR(100)"))
                        # 변경된 타입으로 다시 시도
                        inData.to_sql(name=tableName, if_exists="append", con=engine, index=False, dtype=typeDict)
                    else:
                        print("Could not extract column name from error message.")
    except Exception as e:
        print("[ERROR] : ", e)
        traceback.print_exc()


# In[19]:


def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']


# In[ ]:


def get_table_names(engine):
    # 제공된 엔진을 사용하여 데이터베이스에 연결합니다.
    with engine.connect() as connection:
        # 데이터베이스 메타데이터를 불러옵니다
        metadata = sqlalchemy.MetaData()
        metadata.reflect(bind=engine)
        
        # 데이터베이스에 있는 모든 테이블 이름을 가져옵니다
        table_names = metadata.tables.keys()
        
        # JSON 형식으로 변환하여 반환합니다
        json_data = json.dumps(list(table_names), ensure_ascii=False)
        
        return json_data


# In[20]:


app = FastAPI(title="ML API")


# In[21]:


from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# In[22]:


###라우터 정의
@app.get("/")
async def root():
    try:
        return {"message":"server is now running"}
    except Exception as e:
        print("[ERROR] : ", e)


# In[31]:


class FileData(BaseModel):
    filePath: str
    fileName: str


# In[24]:


filePath = "../dataset/"
paramTablename = "paramTableSample.csv"
engine = createEngine(filePath, paramTablename)


# In[32]:


@app.post("/importFileToTable")
async def importFileToDB(files: List[FileData]):
    try:
        for file in files:
            filePath = file.filePath
            fileName = file.fileName
            print(f"File Path: {filePath}, File Name: {fileName}")
            importFileToTable(filePath, fileName)
        return {"status": "success", "message": "Files processed successfully"}
    except Exception as e:
        print("[ERROR] : ", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# In[ ]:


@app.get("/selectTable")
async def selectTable():
    try:
        table_names_json = get_table_names(engine)
        return table_names_json
    except Exception as e:
        print("[ERROR] : ", e)


# In[46]:


class inData(BaseModel):
    inputText: str


# In[47]:


@app.post("/selectTargetTable")
async def importFileToDB(x:inData):
    try:
        tableName = x.inputText
        with engine.connect() as connection:
            query = f"SELECT * FROM {tableName}"
            result = pd.read_sql(query, connection)
            result.fillna(0, inplace=True)
            result = result.head(10)
            
        return result.to_dict(orient='records')
    except Exception as e:
        print("[ERROR] : ", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# In[ ]:


@app.post("/insertQuery")
async def importFileToDB(x:inData):
    try:
        query = x.inputText
        with engine.connect() as connection:
            result = pd.read_sql(query, connection)
            result.fillna(0, inplace=True)
            result = result.head(10)
            
        return result.to_dict(orient='records')
    except Exception as e:
        print("[ERROR] : ", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# In[16]:


### 서버 구동
if __name__ == "__main__":
    uvicorn.run("ETLserving:app", host="0.0.0.0", port=9998, log_level="debug",
                proxy_headers=True, reload=True)


# In[43]:


# table_names_json = get_table_names(engine)
# print(table_names_json)

