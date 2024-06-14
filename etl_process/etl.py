import numpy as np
import pymysql
import pandas as pd
from datetime import datetime
import os 
# EXTRACTION
def extraction(csvfolder):
    location=pd.DataFrame()
    dates=pd.DataFrame()
    weathers=pd.DataFrame()
    for filepath in csvfolder:
        df=pd.read_csv(filepath,sep=",", encoding='cp1252')
        print("file= ",filepath)
        locationdf=df[['STATION', 'NAME', 'LATITUDE', 'LONGITUDE', 'ELEVATION']]#.drop_duplicates()
        # locationdf.insert(0,'LocationID',range(0,0+len(locationdf)))
        if 'SNWD' not in df.columns:
            df['SNWD'] = 0
        if 'WSFG' not in df.columns:
            df['WSFG'] = 0
        weatherfact= df[['STATION', 'DATE', 'PRCP', 'TAVG', 'TMAX', 'TMIN', 'SNWD','WSFG']]
        datedf=df[['DATE']].drop_duplicates()
        location=pd.concat([location, locationdf], ignore_index=True)
        dates=pd.concat([dates, datedf], ignore_index=True)
        weathers=pd.concat([weathers, weatherfact], ignore_index=True)
        
    return location,dates,weathers


csv_files1 = ["data/Algeria/Weather_1920-1929_ALGERIA.csv","data/Algeria/Weather_1930-1939_ALGERIA.csv",
            "data/Algeria/Weather_1940-1949_ALGERIA.csv","data/Algeria/Weather_1950-1959_ALGERIA.csv",
            "data/Algeria/Weather_1960-1969_ALGERIA.csv","data/Algeria/Weather_1970-1979_ALGERIA.csv",
            "data/Algeria/Weather_1980-1989_ALGERIA.csv","data/Algeria/Weather_1990-1999_ALGERIA.csv",
            "data/Algeria/Weather_2000-2009_ALGERIA.csv","data/Algeria/Weather_2010-2019_ALGERIA.csv","data/Algeria/Weather_2020-2022_ALGERIA.csv"]
csv_files2 =[
    "data/Tunisia/Weather_1920-1959_TUNISIA.csv",
    "data/Tunisia/Weather_1960-1989_TUNISIA.csv",
    "data/Tunisia/Weather_1990-2019_TUNISIA.csv",
    "data/Tunisia/Weather_2020-2022_TUNISIA.csv",
]
csv_files3 = ["data/Morocco/Weather_1920-1959_MOROCCO.csv",
            "data/Morocco/Weather_1960-1989_MOROCCO.csv",
            "data/Morocco/Weather_1990-2019_MOROCCO.csv",
            "data/Morocco/Weather_2020-2022_MOROCCO.csv"]



algerialocation,algeriadate,algeriaweather=extraction(csv_files1) #algeria datas
tunisialocation,tunisiadate,tunisiaweather=extraction(csv_files2) #tunisia data
moroccolocation,moroccodate,moroccoweather=extraction(csv_files3) #morocco weather
print('extraction has been succsseful')

#######transformation ########
def traitment(df):
    df2=df.copy()
    for e in df.columns:
        if df[e].dtypes==object:
            df2[e]=df[e].astype(str)
            df2[e]=df[e].fillna(',,E')
        elif df[e].dtypes==float:
            df2[e]=df[e].fillna(value=0)
    return df2

alllocation=pd.concat([algerialocation,tunisialocation,moroccolocation])
alldates=pd.concat([algeriadate,tunisiadate,moroccodate])
alldates=alldates.drop_duplicates()
allweathers=pd.concat([algeriaweather,tunisiaweather,moroccoweather])
alllocation=alllocation.drop_duplicates()
allweathers2=traitment(allweathers)

print("our fact table has been treatned")


###########LOAD################## 

#pour cree nos table
def create_table(CURSER, table_name, table_schema):
    
    sql = f"DROP TABLE IF EXISTS {table_name}"
    CURSER.execute(sql)
    sql = f"CREATE TABLE {table_name} ({table_schema})"
    CURSER.execute(sql)
    
def creatDB(cursor):
    sql='CREATE DATABASE IF NOT EXISTS Weather_DataWarehouse'
    cursor.execute(sql)
    # cursor.close()
def populate_location_table(co_cursor, df):
    columns = ['STATION', 'NAME', 'LATITUDE', 'LONGITUDE', 'ELEVATION']
    for _, row in df.iterrows():
        placeholders = ','.join(['%s'] * len(columns))
        sql = f"INSERT INTO Location ({','.join(columns)}) VALUES ({placeholders})"
        co_cursor.execute(sql, tuple(row[columns]))

def populate_date_table(co_cursor, df):
    columns = ['DATE']
    for _, row in df.iterrows():
        sql = f"INSERT INTO Date ({','.join(columns)}) VALUES (%s)"
        co_cursor.execute(sql, tuple(row[columns]))

def populate_weather_fact_table(co_cursor, df):
    columns = ['STATION', 'DATE', 'PRCP', 'TAVG', 
               'TMAX', 'TMIN', 'SNWD','WSFG']
    for _, row in df.iterrows():
        placeholders = ','.join(['%s'] * len(columns))
        sql = f"INSERT INTO WeatherFact ({','.join(columns)}) VALUES ({placeholders})"
        co_cursor.execute(sql, tuple(row[columns]))
    
connection = pymysql.connect(host='localhost',
                            user='root',
                            password='',
                            database="Weather_DataWarehouse",
                            #  charset='utf8mb4',
                            cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()

creatDB(cursor)
table_schema_location = """
    STATION VARCHAR(50) PRIMARY KEY,
    NAME VARCHAR(255),
    LATITUDE FLOAT,
    LONGITUDE FLOAT,
    ELEVATION FLOAT
"""
create_table(cursor, "Location",table_schema_location)
print("Table Location created")

#### Create Date Table  
create_table(cursor, "Date", """
    DATE DATE PRIMARY KEY
""")
print("Table Date created")

#### Create WeatherFact Table
create_table(cursor, "WeatherFact", """
    STATION VARCHAR(50),
    DATE DATE,
    PRCP FLOAT,
    TAVG FLOAT,
    TMAX FLOAT,
    TMIN FLOAT,
    SNWD FLOAT,
    WSFG FLOAT,
    PRIMARY KEY (STATION, DATE),
    FOREIGN KEY (STATION) REFERENCES Location(STATION),
    FOREIGN KEY (DATE) REFERENCES Date(DATE)
""")
print("Table WeatherFact created")

#### Create Date Algeria  
#create_table(cursor, "Algeria", """
#    STATION VARCHAR(255),
#    NAME VARCHAR(255), 
#    LATITUDE DOUBLE,
#    LONGITUDE DOUBLE, 
#    ELEVATION DOUBLE, 
#    DATE DATE, 
#    PRCP DOUBLE,    
#    TAVG DOUBLE, 
#    TMAX DOUBLE,    
#    TMIN DOUBLE, 
#""")
#print("Table Algeria created")

populate_location_table(co_cursor=cursor,df=alllocation)
print("location has been set")
populate_date_table(co_cursor=cursor,df=alldates)
print("date table has been created")
print("data has been set succesfuly")

populate_weather_fact_table(co_cursor=cursor,df=allweathers2)
print("the weather fact has been created succssfully")
