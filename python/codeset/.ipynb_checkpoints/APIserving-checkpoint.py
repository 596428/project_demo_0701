#!/usr/bin/env python
# coding: utf-8

# In[13]:


import pandas as pd
import numpy as np
from fastapi import FastAPI, Query
import uvicorn
import pickle
import sklearn
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, text, types
from typing import Optional
import xmltodict


# In[5]:


# ### 모델 불러오기
# with open("listedDtcore.dump","rb") as fw:
#     loadedObjects = pickle.load(fw)
# groupKeys, models, features, transDict, fuelDict = loadedObjects


# In[3]:


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


# In[4]:


filePath = "../dataset/"
paramTablename = "paramTableSample.csv"
engine = createEngine(filePath, paramTablename)


# In[5]:


insertPath


# In[11]:


app = FastAPI(title="ML API")


# In[7]:


from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# In[8]:


###라우터 정의
@app.get("/")
async def root():
    try:
        return {"message":"server is now running"}
    except Exception as e:
        print("[ERROR] : ", e)


# In[9]:


class inDataset(BaseModel):
    # 필수 필드
    TYPE: str = Field(..., description="요청파일타입")
    SERVICE: str = Field(..., description="서비스명 : 공시지가")
    SIGUNGU_NM: str = Field(..., description="시군구명")
    YEAR: int = Field(..., description="연도")

    # 선택적 필드
    BJDONG_NM: Optional[str] = Field(None, description="법정동명")
    BONBEON: Optional[int] = Field(None, description="본번")
    BUBEON: Optional[int] = Field(None, description="부번")
    PILGI_CD: Optional[str] = Field(None, description="필지구분코드")


# In[10]:


## post 정의 
@app.post("/serving", status_code=200)
async def findDataFromDB(x:inDataset):
     try:
         dbName = "test"
         # SERVICE와 YEAR가 모두 포함되어 있는 테이블 찾기
         table_name_query = f"""
         SELECT TABLE_NAME 
         FROM information_schema.tables 
         WHERE TABLE_SCHEMA = '{dbName}' 
         AND TABLE_NAME LIKE '%{x.SERVICE}%'
         AND TABLE_NAME LIKE '%{x.YEAR}%'
         LIMIT 1;
         """
         with engine.connect() as conn:
             result = conn.execute(text(table_name_query)).fetchone()
         if result:
             table_name = result[0]
         else:
             return {"error": "No table found matching the criteria"}

         # SQL 쿼리 생성
         conditions = []
         if x.SIGUNGU_NM is not None:
             conditions.append(f"시군구명 = '{x.SIGUNGU_NM}'")
         if x.BJDONG_NM is not None:
             conditions.append(f"법정동명 = '{x.BJDONG_NM}'")
         if x.BONBEON is not None:
             conditions.append(f"본번 = {x.BONBEON}")
         if x.BUBEON is not None:
             conditions.append(f"부번 = {x.BUBEON}")
         if x.PILGI_CD is not None:
             conditions.append(f"필지구분코드 = '{x.PILGI_CD}'")

         #where 조건 없을 경우 예외처리 추가
         if conditions:
             where_clause = " AND ".join(conditions)
             query = f"SELECT * FROM {table_name} WHERE {where_clause};"
         else:
             query = f"SELECT * FROM {table_name};"

         #쿼리 실행
         print(query)
         with engine.connect() as conn:
             df = pd.read_sql(query, conn)
         
         # 결과 형식 변환
         if x.TYPE.lower() == "json":
             result = df.to_json(orient="records", force_ascii=False)
         elif x.TYPE.lower() == "xml":
             dict_data = df.to_dict(orient="records")
             result = xmltodict.unparse({"root": {"record": dict_data}}, pretty=True)
         else:
             return {"error": "Invalid TYPE value"}
         return result
         
     except Exception as e:
         print("[ERROR] : ", e)
         return {"error": str(e)}


# In[14]:


@app.get("/serving")
async def serving(
    TYPE: str = Query(..., description="요청파일타입"),
    SERVICE: str = Query(..., description="서비스명 : 공시지가"),
    SIGUNGU_NM: str = Query(..., description="시군구명"),
    YEAR: int = Query(..., description="연도"),
    BJDONG_NM: Optional[str] = Query(None, description="법정동명"),
    BONBEON: Optional[int] = Query(None, description="본번"),
    BUBEON: Optional[int] = Query(None, description="부번"),
    PILGI_CD: Optional[str] = Query(None, description="필지구분코드")
):
    try:
        # 입력 데이터를 inDataset 모델로 변환
        data = inDataset(
            TYPE=TYPE,
            SERVICE=SERVICE,
            SIGUNGU_NM=SIGUNGU_NM,
            YEAR=YEAR,
            BJDONG_NM=BJDONG_NM,
            BONBEON=BONBEON,
            BUBEON=BUBEON,
            PILGI_CD=PILGI_CD
        )

        # predict_tf 함수 호출
        result = await findDataFromDB(data)
        return result
    except Exception as e:
        print("[ERROR] : ", e)
        return {"error": str(e)}


# In[ ]:


### 서버 구동
if __name__ == "__main__":
    uvicorn.run("APIserving:app", host="0.0.0.0", port=9999, log_level="debug",
                proxy_headers=True, reload=True)


# In[ ]:


# TYPE: str = Field(..., description="요청파일타입")

# 이것은 Pydantic 모델 (예: BaseModel을 상속받는 클래스) 내에서 사용됩니다.
# Field는 Pydantic에서 제공하는 함수로, 모델 필드의 메타데이터와 검증 규칙을 정의합니다.
# 주로 요청 본문(request body)이나 응답 모델을 정의할 때 사용됩니다.
# ...는 해당 필드가 필수적(required)임을 나타냅니다.


# TYPE: str = Query(..., description="요청파일타입")

# 이것은 FastAPI 라우트 함수의 매개변수를 정의할 때 사용됩니다.
# Query는 FastAPI에서 제공하는 함수로, URL의 쿼리 파라미터를 정의하고 검증합니다.
# 주로 GET 요청의 쿼리 파라미터를 정의할 때 사용됩니다.
# 마찬가지로 ...는 해당 쿼리 파라미터가 필수적임을 나타냅니다.

