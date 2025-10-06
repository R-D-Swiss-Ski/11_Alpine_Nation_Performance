import pandas as pd
import colorsys

from helpers import db_functions as dbf
from helpers.constants import WORLDCUP_FINALS, WORLDCUP_POINTS_FINALS, WORLDCUP_POINTS



def create_wc_points_df(season, genders, disciplines):
    results = pd.DataFrame()
    if 'All' in disciplines:
         disciplines = ['GS', 'SL', 'DH', 'SG']
    if 'All' in genders:
        genders = ['M', 'W']
    for discipline in disciplines:
        for gender in genders:
            result = dbf.get_results(season=season, discipline=discipline, gender=gender)
            results = pd.concat([result, results], ignore_index=True)
    if not results.empty:
        results = results.rename(columns={"Competitor_Nationcode": "Nation", 'Disciplinecode': 'Discipline'})
        # drop cancelled races
        results = results[results['Webcomment'] != "Cancelled"]
        ## map world cup points
        results['isFinal'] = results['Raceid'].apply(lambda x: True if x in WORLDCUP_FINALS else False)
        results['WCPoints'] = 0
        mask = results['isFinal']
        results.loc[mask, 'WCPoints'] = results.loc[mask, 'Position'].map(WORLDCUP_POINTS_FINALS).fillna(0)
        results.loc[~mask, 'WCPoints'] = results.loc[~mask, 'Position'].map(WORLDCUP_POINTS).fillna(0)
    return results


def create_nation_cup_df(wc_points_df):
    #Nation Cup Standing 
    df = wc_points_df[['Nation', 'WCPoints', 'Discipline', 'Gender']]
    df_grp = df.groupby(['Nation', 'Discipline', 'Gender']).sum().reset_index()
    return df_grp

def get_races(season, gender, discipline):
    races = pd.DataFrame()
    if 'All' in discipline:
        discipline = ['GS', 'SL', 'DH', 'SG']
    if 'All' in gender:
        gender = ['M', 'W']
    for d in discipline:
        for g in gender:
            race = dbf.get_races_dp(season=season, discipline=d, gender=g)
            races = pd.concat([race, races], ignore_index=True)
    # drop cancelled races
    races = races[races['Webcomment'] != "Cancelled"]
    
    return races

def get_season(date):
    month = date.month
    if month >= 5:
        season = date.year +1
    else:
        season = date.year
    return season


def adjust_lightness(hex_color, factor=1.0):
    """
    Lighten or darken a hex color.
    factor > 1.0 => lighter
    factor < 1.0 => darker
    """
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    l = max(0, min(1, l * factor))  # adjust lightness
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"