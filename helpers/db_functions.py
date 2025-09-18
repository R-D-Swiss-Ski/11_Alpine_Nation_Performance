import streamlit as st
import pandas as pd

from google.oauth2 import service_account
from google.cloud import bigquery

# Loads query results from Datapool
def load_datapool(query):
    
    credentials = service_account.Credentials.from_service_account_info(st.secrets["datapool_service_account"])
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)

    query_job = client.query(query)
    rows_raw = query_job.result()
    rows = [dict(row) for row in rows_raw]
    return pd.DataFrame(rows)

@st.cache_data(ttl='2h', show_spinner='Fetching new data...')
def get_races_dp(season, gender, discipline):
    query_races = f"""
    SELECT Raceid, Eventid, Seasoncode, Disciplinecode, Catcode, Gender, Racedate, Place, Nationcode, Sectorcode, Disciplinename, Catname, Livestatus1, Webcomment  
    FROM swissski-production.raw_fis.fis_races
    WHERE Catcode="WC" AND Sectorcode="AL" AND Seasoncode = {season} AND Gender = '{gender}' AND Disciplinecode = '{discipline}';
    """

    df = load_datapool(query_races)

    return df


def get_fis_results():
    query_races = """
    SELECT competitionId, athleteId, disciplineCode, position, rank, name, nationCode, genderCode, result, resultFisPoints,cupPoints, fisPoints, rankFisPoints 
    FROM swissski-production.raw_fis.fisapi_results;
    """

    df = load_datapool(query_races)

    return df
    
def get_results(season = 2026, discipline = "", gender=""):
    query_races = f"""
    SELECT Raceid, Seasoncode, Sectorcode, Disciplinecode, Catcode, Racedate, Place, Nationcode, Gender, Competitorname, Competitorid, Competitor_Nationcode, Status, Racepoints, Position, Details, Webcomment 
    FROM swissski-production.raw_fis.fis_results
    WHERE Sectorcode="AL" AND Catcode="WC" AND Seasoncode = {season} AND Disciplinecode= "{discipline}" AND Gender="{gender}";
    """

    df = load_datapool(query_races)

    return df
def get_result(race_id):
    query_races = f"""
    SELECT Raceid, Seasoncode, Sectorcode, Disciplinecode, Catcode, Racedate, Place, Nationcode, Gender, Competitorname, Competitorid, Competitor_Nationcode, Status, Racepoints, Position, Details 
    FROM swissski-production.raw_fis.fis_results
    WHERE Raceid={race_id};
    """

    df = load_datapool(query_races)
    return df
