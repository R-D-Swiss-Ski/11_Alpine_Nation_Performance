import streamlit as st
import pandas as pd

from datetime import datetime

from helpers import data_functions as d
from helpers.constants import COLOR_NATIONS, FIS_SEASON, RANKING_2025

from views.nations import nations_view
from views.nation_details import nation_details_view
from views.overall import overall_view

st.set_page_config(
    initial_sidebar_state="collapsed",
    page_title="Alpine Nation Performance",
    layout="wide",
    )


def details(nation, gender, discipline, df_results_wcpoints):
    st.session_state.details = True
    st.session_state.main=False
    st.session_state.df = df_results_wcpoints
    st.session_state.nation = nation
    st.session_state.gender=gender
    st.session_state.discipline=discipline

def go_back():
    st.session_state.details = False
    st.session_state.main =True


if "details" not in st.session_state:
    st.session_state.details = False

if 'main' not in st.session_state:
    st.session_state.main = True

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()

if 'nation' not in st.session_state:
    st.session_state.nation = ""

if 'gender' not in st.session_state:
    st.session_state.gender = ""

if 'discipline' not in st.session_state:
    st.session_state.discipline =""

if 'show_future' not in st.session_state:
    st.session_state.show_future = False
if 'hidden_feature' not in st.query_params:
    st.query_params.hidden_feature = ''

if 'selected_season' not in st.session_state:
    st.session_state.selected_season = "25/26"

#pick a season
default_season = d.get_season(datetime.today())
current_season = default_season
default_season = FIS_SEASON.get(default_season)
season_options = list(FIS_SEASON.values())
default_index = season_options.index(default_season)
season_col1, season_col2 = st.columns([0.3,0.7])
season_picker = season_col1.selectbox(label=":blue[Select Season]", options=season_options, index=default_index, key='season_selection')
selected_season = next(key for key, value in FIS_SEASON.items() if value == season_picker)
st.session_state.selected_season = selected_season

if selected_season == current_season:
    st.session_state.show_future = True
else:
    st.session_state.show_future = False

#*Set page title
if st.session_state.main:
    st.header(f"Alpine Nation Performance {season_picker}")


#get data overall
df_results_wcpoints_overall = d.create_wc_points_df(season=selected_season, genders=['All'], disciplines=['All'])

#get data for future events if selected season = current season
if st.session_state.show_future:
    df_future_races = d.get_races_upcoming(selected_season,['All'], ['All'], datetime.today().date())

if not df_results_wcpoints_overall.empty:
    df_nations_cup_overall = df_results_wcpoints_overall[['Nation', 'WCPoints']]
    df_nations_cup_overall_grp = df_nations_cup_overall.groupby(['Nation']).sum().reset_index().sort_values(by=['WCPoints'], ascending=False)

    #get top 5 nations
    top5_nations = df_nations_cup_overall_grp.head(5)
    top5 = top5_nations['Nation'].tolist()
    # Get unique nations
    nations = df_nations_cup_overall_grp["Nation"].unique()
    #only color top 5 nations, rest grey
    color_mapping = {nation: COLOR_NATIONS.get(nation, "#8D8D8D") if nation in top5_nations['Nation'].values else '#8D8D8D' for nation in nations}

    if st.session_state.main:
        tab1, tab2 = st.tabs(["By Gender and Discipline", "Overall"])
        with tab1:
            nations_view(color_mapping, top5)
            
        with tab2:
            overall_view(df_nations_overall=df_nations_cup_overall_grp, df_wcpoints_overall=df_results_wcpoints_overall, color_mapping=color_mapping, top5=top5)

    if st.session_state.details:
        nation_details_view()
else:
    st.warning("No data to show")

    
if st.query_params.hidden_feature == 'elena':
    # get upcoming events by searching for closest Racedate and getting the eventid and then show all rows with that eventid
    if not df_future_races.empty:
        closest_date = df_future_races['Racedate'].min()
        closest_event = df_future_races[df_future_races['Racedate'] == closest_date]['Eventid'].iloc[0]
        next_races = df_future_races[df_future_races['Eventid'] == closest_event]
    else:
        next_races = pd.DataFrame()
    st.subheader("Upcoming Events")
    
    for i, row in next_races.iterrows():    
        with st.container(border=True):
            cols = st.columns([0.2,0.2,0.2, 0.2, 0.2], vertical_alignment="center")
            with cols[0]:
                st.metric(
                    label=f"Date",
                    value=f"{pd.to_datetime(row['Racedate']).strftime('%d.%m.%Y')}"
                )
            with cols[1]:
                st.metric(
                    label=f"Place",
                    value=f"{row['Place']}",
                )
            with cols[2]:
                st.metric(
                    label=f"Discipline",
                    value=f"{row['Disciplinename']}",
                )
            with cols[3]:
                st.metric(
                    label=f"Gender",
                    value=f"{row['Gender']}"
                )
            with st.expander("Show Past Results"):
                #show table with past top 10 (4 years back)
                # get past races
                past_races_place = d.get_races_place(row['Place'], current_season, row['Gender'], row['Disciplinecode'])
                
                # get top5 athletes of each race
                past_results = d.get_results_topn(past_races_place['Raceid'].unique(), 8)
                past_results = past_results.sort_values(by=['Seasoncode','Position'])
                # show results next to each other; calculate columns needed for this (one column per season)
                count_season = len(past_races_place['Seasoncode'].unique())
                
                results_seasons = sorted(past_races_place['Seasoncode'].unique(), reverse=True)

                #highilght top5 last season race or discipline ranking
                select_highlight = st.radio('Highlighting', options=['Top 5 last season this race', 'Top 5 last season discipline ranking'], key=f'radio_buttion_{i}', horizontal=True)
                if select_highlight == "Top 5 last season this race":
                    #highlight Athletes in table that were in top5 last season for this race 
                    top5_athletes_last = past_results[past_results['Seasoncode'] == current_season-1]
                    top5_athletes_last = top5_athletes_last.sort_values(by=['Position']).head(5)[['Competitorid', 'Competitorname']]
                    #assign each athlete a color
                    
                elif select_highlight == "Top 5 last season discipline ranking":
                    # or highlight if top5 in discipline ranking last season
                    discipline_gender_key = f"{row['Disciplinecode']}_{row['Gender']}"
                    top5_ranking = RANKING_2025.get(discipline_gender_key, [])
                    top5_athletes_last = pd.DataFrame({'Competitorname':top5_ranking})
                    

                top5_athletes_last['color'] = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
                top5_names = top5_athletes_last['Competitorname'].unique()
                def highlighting(val):
                    color=top5_athletes_last[top5_athletes_last['Competitorname']==val]['color'].iloc[0] if val in top5_names else ''
                    return f'background-color: {color}'
        
        
                past_cols = st.columns(2)
                j = 0
                for season in results_seasons:
                    df = past_results[past_results['Seasoncode'] == season]
                    df = df.sort_values(by=['Position'])
                    with past_cols[j%2]:  
                        st.write(f"{FIS_SEASON.get(season)}, {df['Place'].iloc[0]}, {df['Gender'].iloc[0]}, {df['Disciplinecode'].iloc[0]}")
                        st.dataframe(
                            df[['Competitorname', 'Competitor_Nationcode', 'Position', 'Details']].style.applymap(highlighting, subset=['Competitorname']),
                            column_config={
                                "Competitorname": 'Athlete',
                                "Position": 'Rank',
                                "Details": 'Time',
                                "Competitor_Nationcode": 'Nation',
                            },
                            column_order=['Position', 'Competitorname', 'Competitor_Nationcode', 'Details'],
                            hide_index=True,

                        )
                    j +=1



            





footer="""<style>

.footer {
bottom: 0;
width: 100%;
color: rgb(177,179,181);
text-align: center;
}
</style>
<div class="footer">
<p style="font-size: 12px">Problems or Feedback? <a href="mailto:forschung+ld-tr-app@swiss-ski.ch?subject=Feedback Advanced Training Statistics App">Contact Us!</a></p>
<p style="font-size: 12px">Created by Swiss-Ski R&D - 2025</p>
</div>
"""

st.markdown(footer,unsafe_allow_html=True)
placeholder_col_1, placeholder_col_2, placeholder_col_3 = st.columns([0.46,0.08,0.46])
#!Change for production/development
# for production use: FIS_List_Dashboard-main/images/logo_rd_500.png
# placeholder_col_2.image("SwissSki_Tool/images/logo_rd_500.png")
# for development use: images/logo_rd_500.png
placeholder_col_2.image("images/logo_rd_500.png")