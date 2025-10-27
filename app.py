import streamlit as st
import pandas as pd
import plotly.express as px

from datetime import datetime
from st_aggrid import AgGrid

from helpers import data_functions as d
from helpers.constants import GENDER, DISCIPLINES, COLOR_NATIONS, FIS_SEASON, RANKING_2025
from helpers.ag_grid_options import custom_css, grid_options, grid_options_1, grid_options_2

st.set_page_config(
    initial_sidebar_state="collapsed",
    page_title="Alpine Nation Performance",
    layout="wide",
    )



def details(nation, gender, discipline):
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

#pick a season
default_season = d.get_season(datetime.today())
current_season = default_season
default_season = FIS_SEASON.get(default_season)
season_options = list(FIS_SEASON.values())
default_index = season_options.index(default_season)
season_col1, season_col2 = st.columns([0.3,0.7])
season_picker = season_col1.selectbox(label=":blue[Select Season]", options=season_options, index=default_index, key='season_selection')
selected_season = next(key for key, value in FIS_SEASON.items() if value == season_picker)

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
    df_future_races = d.get_races(selected_season,['All'], ['All'])

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
            filter1, filter2, filter3 = st.columns(3)

            gender_filter = filter1.selectbox(":blue[Gender]", options=GENDER) 
            discipline_filter = filter2.selectbox(":blue[Discipline]", options=DISCIPLINES)

            #get upcoming race and last race
            date_today = datetime.today()

            #!for testing
            # date_today = datetime.strptime("2025-02-28", "%Y-%m-%d")
    


            df_races_season = d.get_races(selected_season,[gender_filter], [discipline_filter])
        

            #last race
            past_races = df_races_season[df_races_season['Racedate'] < date_today.date()]
            if not past_races.empty:
                last_race = past_races[past_races['Racedate'] == max(past_races['Racedate'])]
            else:
                last_race = pd.DataFrame()

            #next race
            future_races = df_races_season[df_races_season['Racedate'] >= date_today.date()]
            if not future_races.empty:
                next_race = future_races[future_races['Racedate'] == min(future_races['Racedate'])]
            else:
                next_race = pd.DataFrame()



            # Get results and wc points of selected discipline and gender
            df_results_wcpoints = d.create_wc_points_df(season=selected_season, genders=[gender_filter], disciplines=[discipline_filter])
            if df_results_wcpoints.empty:
                st.info("No data yet")
            else:
                # create nations cup df
                df_nations_cup = d.create_nation_cup_df(df_results_wcpoints)
                
                # only nations that have points
                df_nations_cup_points = df_nations_cup[df_nations_cup['WCPoints'] != 0].reset_index(drop=True)

                #create nation-gender column
                df_nations_cup_points["Nation_Gender"] = df_nations_cup_points["Nation"] + "-" + df_nations_cup_points["Gender"]

                # Build Nation-Gender colormap
                color_nation_gender_mapping = {}
                for nation, base_color in color_mapping.items():
                    if base_color != "#8D8D8D":
                        color_nation_gender_mapping[f"{nation}-M"] = d.adjust_lightness(base_color, 0.8)  # darker
                        color_nation_gender_mapping[f"{nation}-W"] = d.adjust_lightness(base_color, 1.2)  # lighter
                    else:
                        color_nation_gender_mapping[f"{nation}-M"] = "#8D8D8D"  # darker
                        color_nation_gender_mapping[f"{nation}-W"] = "#CCCCCC"  # lighter

                nation_order = (
                    df_nations_cup_points.groupby("Nation")["WCPoints"]
                    .sum()
                    .sort_values(ascending=False)
                    .index.tolist()
                )
                nation_cup_fig = px.bar(
                    df_nations_cup_points,
                    x="Nation",
                    y="WCPoints",
                    color="Nation_Gender",
                    barmode="stack",
                    facet_col="Discipline",
                    facet_col_wrap=2,
                    category_orders={
                        "Nation": nation_order,
                        "Gender": ["M", "F"]
                    },
                    color_discrete_map=color_nation_gender_mapping,
                    text="WCPoints",
                    hover_data={'Nation_Gender': False, "Gender": True}
                )

                nation_cup_fig.update_layout(
                    height=600,
                    xaxis_title="Nation",
                    yaxis_title="WCPoints",
                    showlegend=False,
                )

                st.subheader("Nations Ranking per Discipline")
                st.plotly_chart(nation_cup_fig, use_container_width=True)

                #*Card views (1st View)
                ##Nation, Points, Points by gender, delta to last race
                past_races_ids = past_races['Raceid'].unique()
                past_races_wc_points = df_results_wcpoints[df_results_wcpoints['Raceid'].isin(past_races_ids)]
                
                past_races_wc_points_grp = past_races_wc_points[['Nation', 'WCPoints']].groupby(['Nation'], as_index=False).sum()
                past_races_wc_points_grp = past_races_wc_points_grp.rename(columns={"WCPoints": "points_past"})
                
                all_races_wc_points_grp = df_results_wcpoints[['Nation', 'Gender', 'WCPoints']].groupby(['Nation', 'Gender'], as_index=False).sum()
                
                if gender_filter == "All":
                    df_metrics = all_races_wc_points_grp.pivot_table(index='Nation', columns='Gender', values='WCPoints', aggfunc='sum', fill_value=0).reset_index()
                    df_metrics = df_metrics.rename(columns={"M": "points_m", "W": "points_w"})
                    df_metrics['points_all'] = df_metrics['points_m']+df_metrics['points_w']
                else:
                    df_metrics = all_races_wc_points_grp
                    df_metrics = df_metrics.rename(columns={"WCPoints": "points_all"})
            

                df_results_wcpoints_delta = pd.merge(df_metrics, past_races_wc_points_grp, how='right', on=['Nation'], suffixes=('_current', '_past'))
                df_results_wcpoints_delta['delta']=df_results_wcpoints_delta['points_all']-df_results_wcpoints_delta['points_past']
                df_results_wcpoints_delta = df_results_wcpoints_delta.sort_values(by=['points_all'], ascending=False, ignore_index=True)
                df_results_wcpoints_delta["rank"] = df_results_wcpoints_delta["points_all"].rank(method='dense', ascending=False).astype(int)        

                with st.container(height=600):
                    for i, row in df_results_wcpoints_delta.iterrows():
            
                        with st.container(border=True):
                            cols = st.columns([0.2,0.2,0.4, 0.2], vertical_alignment="center")
                            if gender_filter == "All":
                                with cols[0]:
                                    st.metric(
                                        label=f"Position",
                                        value=f"{row['rank']}",
                                    )
                                with cols[1]:
                                    st.metric(
                                        label=f"Nation",
                                        value=f"{row['Nation']}",
                                    )
                                with cols[2]:
                                    st.metric(
                                        label=f"M: {row['points_m']}, W: {row['points_w']}",
                                        value=f"{row['points_all']}",
                                        delta=row['delta'],
                                    )
                                with cols[3]:
                                    st.button("Details", on_click=details, args=(row['Nation'],'All', discipline_filter), key=f"details_{i}")

                            else:
                                with cols[0]:
                                    st.metric(
                                        label=f"Position",
                                        value=f"{row['rank']}",
                                    )
                                with cols[1]:
                                    st.metric(
                                        label=f"Nation",
                                        value=f"{row['Nation']}",
                                    )
                                with cols[2]:
                                    st.metric(
                                        label="WC Points",
                                        value=f"{row['points_all']}",
                                        delta=row['delta'],
                                    )
                                with cols[3]:
                                    st.button("Details", on_click=details, args=(row['Nation'], row['Gender'], discipline_filter), key=f"details_{i}")


                #*Line Charts (2nd View)
                st.subheader("Points per Raceweek Top 5 Nations")

                ##get top 5 nations
                
                df_top5 = df_results_wcpoints[(df_results_wcpoints['Nation'].isin(top5)) & (df_results_wcpoints['WCPoints']!=0)][['Raceid', 'Racedate', 'Place', 'Nation', 'Discipline', 'WCPoints']]
                df_top5_grp = df_top5.groupby(by=['Raceid', 'Racedate', 'Place', 'Nation', 'Discipline']).sum().reset_index()
                
                df_top5_grp['Racedate'] = pd.to_datetime(df_top5_grp['Racedate'])

                # Get calendar week
                df_top5_grp["CalendarWeek"] = df_top5_grp["Racedate"].dt.isocalendar().week
                # create Raceweeks
                week_order = (
                    df_top5_grp.groupby("CalendarWeek")['Racedate'].min().sort_values().reset_index()
                )
                week_order['Raceweek'] = range(1, len(week_order)+1)
                df_top5_grp = df_top5_grp.merge(week_order[["CalendarWeek", "Raceweek"]], on="CalendarWeek", how="left")
            
                fig_points_per_week = px.line(
                    df_top5_grp[['Nation', 'Raceweek', 'Raceid', 'WCPoints', 'Discipline']].groupby(['Raceweek', 'Nation'], as_index=False).aggregate({
                        "Raceid": "count",
                        "WCPoints": "sum",
                        "Discipline": list
                    }).rename(columns={"Raceid": "Race(s)"}),
                    x='Raceweek',
                    y='WCPoints',
                    color='Nation',
                    hover_data=['Race(s)', 'Discipline'],
                    color_discrete_map=COLOR_NATIONS
                )
                fig_points_per_week.update_traces(mode="markers+lines")
                st.plotly_chart(fig_points_per_week, use_container_width=True)
            
        with tab2:
                st.subheader("Overall Points Nations")
                
                overall_nation_cup_fig = px.bar(
                    df_nations_cup_overall_grp,
                    x="Nation",
                    y="WCPoints",
                    color="Nation",
                    text="WCPoints", 
                    color_discrete_map=color_mapping
                )
                overall_nation_cup_fig.update_traces(textposition="outside")
                overall_nation_cup_fig.update_layout(
                    yaxis_title="WC Points",
                    xaxis_title="Nation",
                )

                st.plotly_chart(overall_nation_cup_fig, use_container_width=True)

                #Wins, 2nd, 3rd, 4-15, 16-30 per nation and discipline AND points per nation and discipline AND % Points
                st.subheader("Summary Table")

                df_summary_table = df_results_wcpoints_overall[['Nation', 'Position', 'Discipline', 'WCPoints', 'Gender']]
                df_summary_table = df_summary_table[(df_summary_table['Position'] != 0) & (df_summary_table['WCPoints']!= 0)]
                df_summary_table['rank_group'] = df_summary_table['Position'].apply(lambda x: "Wins" if x == 1 else ("2nd" if x== 2 else ("3rd" if x==3 else ( "[4-15]" if x in [4,5,6,7,8,9,10,11,12,13,14,15] else ("[16-30]" if x in [16,17,18,19,20,21,22,23,24,25,26,27,28,29,30] else "")))))
                
                df_summary_wc_points = df_summary_table[['Nation', 'Discipline', 'WCPoints']].groupby(['Nation', 'Discipline']).sum().reset_index()
                df_summary_wc_points_gender = df_summary_table[['Nation', 'Discipline', 'WCPoints', 'Gender']].groupby(['Nation', 'Discipline', 'Gender']).sum().reset_index()
                total_points = df_summary_wc_points['WCPoints'].sum()

                dh_points = df_summary_wc_points[df_summary_wc_points['Discipline']=="DH"]['WCPoints'].sum()
                sg_points = df_summary_wc_points[df_summary_wc_points['Discipline']=="SG"]['WCPoints'].sum()
                gs_points = df_summary_wc_points[df_summary_wc_points['Discipline']=="GS"]['WCPoints'].sum()
                sl_points = df_summary_wc_points[df_summary_wc_points['Discipline']=="SL"]['WCPoints'].sum()


                #discipline totals
                discipline_totals = {
                    "DH": dh_points,
                    "SG": sg_points,
                    "GS": gs_points,
                    "SL": sl_points,
                    "Overall": total_points
                }
                df_overall_nation = df_nations_cup_overall_grp
                df_overall_nation['Discipline'] = "Overall"

                df_summary_wc_points_with_overall = pd.concat([df_summary_wc_points, df_overall_nation], ignore_index=True)
                df_summary_wc_points_perc=df_summary_wc_points_with_overall.copy() 
                # Map each discipline to its total
                df_summary_wc_points_perc['TotalPoints'] = df_summary_wc_points_perc['Discipline'].map(discipline_totals)

                # Compute percentage
                df_summary_wc_points_perc['Percentage'] = (
                    df_summary_wc_points_perc['WCPoints'] / df_summary_wc_points_perc['TotalPoints'] * 100
                ).fillna(0).round(1)

                # compute percentage of women/men; How much points did women/men generate for a nation in one discipline
                # total points of nation for discipline, points by gender 
                df_nations_cup_overall_gender_grp = df_summary_wc_points_gender[['Nation', 'Gender', 'WCPoints']].groupby(['Nation', 'Gender']).sum().reset_index()
                df_nations_cup_overall_gender_grp['Discipline'] = 'Overall'
                df_summary_wc_points_gender_perc = pd.concat([df_summary_wc_points_gender, df_nations_cup_overall_gender_grp], ignore_index=True)
                df_summary_wc_points_gender_perc = pd.merge(df_summary_wc_points_gender_perc, df_summary_wc_points_with_overall, how='left', on=['Nation', 'Discipline'], suffixes=['_gender', '_discipline_total'])
                df_summary_wc_points_gender_perc['Percentage'] = (df_summary_wc_points_gender_perc['WCPoints_gender'] / df_summary_wc_points_gender_perc['WCPoints_discipline_total']*100).fillna(0).round(1)
                                
                #unpivot df_summary_wc_points without percentages
                df_summary_wc_points_unpivot = df_summary_wc_points_gender[['Nation', 'Discipline', 'WCPoints', 'Gender']].rename(columns={'WCPoints': 'value'})
                df_summary_wc_points_unpivot['column_name'] = 'WCPoints'
                #unpivot df_summary_wc_points_perc with percentages
                df_summary_percentage_unpivot = df_summary_wc_points_perc[['Nation', 'Discipline', 'Percentage']].rename(columns={'Percentage': 'value'})
                df_summary_percentage_unpivot['value'] = df_summary_percentage_unpivot['value'].round(1)
                df_summary_percentage_unpivot['column_name'] = '% Points'
                #unpivot df_summary_wc_points_gender_perc
                df_summary_gender_perc_unpivot = df_summary_wc_points_gender_perc[['Nation', 'Discipline', 'Gender', 'Percentage']].rename(columns={'Percentage': 'value'})
                df_summary_gender_perc_unpivot['column_name'] = df_summary_gender_perc_unpivot['Gender'].apply(lambda x: '% Points M' if x == 'M' else '% Points W')
                
                df_summary_percentage_unpivot = pd.concat([df_summary_percentage_unpivot, df_summary_gender_perc_unpivot[['Nation', 'Discipline', 'value', 'column_name']]], ignore_index=True)
                
                df_nation_summary = df_summary_table[['Nation', 'Discipline', 'Gender', 'rank_group']]
                df_nation_summary = df_nation_summary.groupby(['Nation', 'Discipline', 'Gender', 'rank_group']).size().reset_index(name='count')
                df_nation_summary = df_nation_summary.rename(columns={'rank_group': 'column_name', 'count': 'value'})
                df_nation_summary = pd.concat([df_nation_summary, df_summary_wc_points_unpivot], ignore_index=True)
                df_nation_summary = df_nation_summary.sort_values(by=['value'], ascending=False, ignore_index=True)
                
                AgGrid(df_nation_summary, gridOptions=grid_options, height = 350, custom_css=custom_css, allow_unsafe_jscode=True)

                #* Percentage Points Tables
                ##* Percentage Points by each Nation with Gender Contribution
                # Define the custom nation order
                nation_order = df_nations_cup_overall_grp['Nation']
                # Create a mapping for sorting
                nation_sort_map = {nation: i for i, nation in enumerate(nation_order)}

                # Sort by nation order first, then by value descending
                df_summary_percentage_unpivot['nation_sort_key'] = df_summary_percentage_unpivot['Nation'].map(nation_sort_map).fillna(999)
                df_summary_percentage_unpivot = df_summary_percentage_unpivot.sort_values(by=['nation_sort_key', 'value'], ascending=[True, False], ignore_index=True)
                df_summary_percentage_unpivot = df_summary_percentage_unpivot.drop('nation_sort_key', axis=1)
                
                st.subheader("Percentage of Points by each Nation with Gender Contribution")
                AgGrid(df_summary_percentage_unpivot, gridOptions=grid_options_1, height = 350, custom_css=custom_css, allow_unsafe_jscode=True)

                ##* Percentage Points by Nation per Race Week
                # create race weeks
                df_percentage_per_raceweek = df_results_wcpoints_overall[df_results_wcpoints_overall['WCPoints']!=0].copy()
                df_percentage_per_raceweek["CalendarWeek"] = pd.to_datetime(df_percentage_per_raceweek["Racedate"]).dt.isocalendar().week
                week_order = (
                    df_percentage_per_raceweek.groupby("CalendarWeek")['Racedate'].min().sort_values().reset_index()
                )
                week_order['Raceweek'] = range(1, len(week_order)+1)
                df_percentage_per_raceweek_general = df_percentage_per_raceweek.merge(week_order[["CalendarWeek", "Raceweek"]], on="CalendarWeek", how="left")
                df_percentage_per_raceweek = df_percentage_per_raceweek_general[['Nation', 'Discipline', 'WCPoints','Gender', 'Raceweek']].groupby(['Nation', 'Discipline', 'Gender', 'Raceweek']).sum().reset_index()
                df_percentage_per_raceweek_all = df_percentage_per_raceweek_general[['Nation', 'Discipline', 'WCPoints', 'Raceweek']].groupby(['Nation', 'Discipline', 'Raceweek']).sum().reset_index()
                
                #how many percentages of the achievable pints did a nation get in one raceweek?
                df_total_points_per_raceweek_overall = df_percentage_per_raceweek[['Raceweek', 'WCPoints']].groupby('Raceweek').sum().reset_index()
                df_total_points_per_raceweek = df_percentage_per_raceweek[['Raceweek', 'WCPoints', 'Discipline', 'Gender']].groupby(['Raceweek', 'Discipline', 'Gender']).sum().reset_index()
                df_total_points_per_raceweek = df_total_points_per_raceweek.rename(columns={'WCPoints': 'TotalPoints'})
                
                df_total_points_per_raceweek_all = df_percentage_per_raceweek_all[['Raceweek', 'WCPoints', 'Discipline']].groupby(['Raceweek', 'Discipline']).sum().reset_index()
                df_total_points_per_raceweek_all = df_total_points_per_raceweek_all.rename(columns={'WCPoints': 'TotalPoints'})
                
                
                df_percentage_per_raceweek = df_percentage_per_raceweek.merge(df_total_points_per_raceweek, on=['Raceweek', 'Discipline', 'Gender'], how='left')
                df_percentage_per_raceweek['Percentage'] = df_percentage_per_raceweek['WCPoints'] / df_percentage_per_raceweek['TotalPoints'] *100
                df_percentage_per_raceweek_all = df_percentage_per_raceweek_all.merge(df_total_points_per_raceweek_all, on=['Raceweek', 'Discipline'], how='left')
                df_percentage_per_raceweek_all['Percentage'] = df_percentage_per_raceweek_all['WCPoints'] / df_percentage_per_raceweek_all['TotalPoints'] *100
                
                df_percentage_per_raceweek_unpivot = df_percentage_per_raceweek[['Nation', 'Discipline', 'Gender', 'Raceweek', 'Percentage']]
                df_percentage_per_raceweek_unpivot = df_percentage_per_raceweek_unpivot.rename(columns={'Percentage':'value'})
                df_percentage_per_raceweek_unpivot['column_name'] = df_percentage_per_raceweek_unpivot['Gender'].apply(lambda x: '% Points M' if x == 'M' else '% Points W')
                
                
                df_percentage_per_raceweek_all_unpivot = df_percentage_per_raceweek_all[['Nation', 'Discipline', 'Raceweek', 'Percentage']]
                df_percentage_per_raceweek_all_unpivot = df_percentage_per_raceweek_all_unpivot.rename(columns={'Percentage':'value'})
                df_percentage_per_raceweek_all_unpivot['column_name'] = '% Points'
                
                
                df_percentage_per_raceweek_everything_unpivot = pd.concat([df_percentage_per_raceweek_all_unpivot, df_percentage_per_raceweek_unpivot[['Nation', 'Discipline', 'Raceweek', 'value', 'column_name']]], ignore_index=True)
                # Sort by nation order first, then by value descending
                df_percentage_per_raceweek_everything_unpivot['nation_sort_key'] = df_percentage_per_raceweek_everything_unpivot['Nation'].map(nation_sort_map).fillna(999)
                df_percentage_per_raceweek_everything_unpivot = df_percentage_per_raceweek_everything_unpivot.sort_values(by=['nation_sort_key', 'value'], ascending=[True, False], ignore_index=True)
                df_percentage_per_raceweek_everything_unpivot = df_percentage_per_raceweek_everything_unpivot.drop('nation_sort_key', axis=1)
                st.subheader("Percentage of Points by each Nation per Raceweek")
                st.write("wiht Gender Contribution")
                AgGrid(df_percentage_per_raceweek_everything_unpivot, gridOptions=grid_options_2, height = 350, custom_css=custom_css, allow_unsafe_jscode=True)


                only_top5 = st.toggle("Top 5", key="show_top5")
                if only_top5:
                    df_percentage_per_raceweek = df_percentage_per_raceweek[df_percentage_per_raceweek['Nation'].isin(top5)]
                    
                
                df_percentage_per_raceweek['Nation_Gender'] = df_percentage_per_raceweek['Nation'] + "-" + df_percentage_per_raceweek['Gender']
                # Build Nation-Gender colormap
                color_nation_gender_mapping = {}
                for nation, base_color in color_mapping.items():
                    if base_color != "#8D8D8D":
                        color_nation_gender_mapping[f"{nation}-M"] = d.adjust_lightness(base_color, 0.8)  # darker
                        color_nation_gender_mapping[f"{nation}-W"] = d.adjust_lightness(base_color, 1.2)  # lighter
                    else:
                        color_nation_gender_mapping[f"{nation}-M"] = "#8D8D8D"  # darker
                        color_nation_gender_mapping[f"{nation}-W"] = "#CCCCCC"  # lighter


            
                ##* Percentage Points by Nation per Raceweek plot
                df_percentage_per_raceweek['Percentage'] = df_percentage_per_raceweek_all['Percentage'].round(1) 
                
                percentage_nation_raceweek_fig = px.bar(
                    df_percentage_per_raceweek,
                    x='Raceweek',
                    y='Percentage',
                    color="Nation_Gender",
                    barmode="stack",
                    facet_col="Discipline",
                    facet_col_wrap=2,
                    color_discrete_map=color_nation_gender_mapping,
                    hover_data={'Nation_Gender': False, "Gender": True, 'Nation': True}
                    
                )
                percentage_nation_raceweek_fig.update_layout(
                    showlegend=False,
                    height=600
                    
                )
                percentage_nation_raceweek_fig.for_each_annotation(lambda a: a.update(text=f"<b>{a.text.split('=')[-1]}</b>"))

                st.plotly_chart(percentage_nation_raceweek_fig)

                # perc_nation_raceweek_line_fig = px.line(
                #     df_percentage_per_raceweek_all,
                #     x='Raceweek',
                #     y='Percentage',
                #     color='Nation',
                #     color_discrete_map= color_mapping,
                #     facet_row='Discipline',
                   
                # )
                # perc_nation_raceweek_line_fig.update_traces(mode="markers+lines")
                # perc_nation_raceweek_line_fig.update_layout(
                #     height=600,
                #     showlegend=False,
                # )
                # perc_nation_raceweek_line_fig.for_each_annotation(lambda a: a.update(text=a.text.split('=')[-1]))

                # st.plotly_chart(perc_nation_raceweek_line_fig)

    if st.session_state.details:
        st.button("Go Back", on_click=go_back)
        df_details = st.session_state.df.copy()
        df_details = df_details[df_details['WCPoints']!=0]
        #*Points per Race Week
        # st.subheader(f"{st.session_state.nation} Points per Race Week")
        # df_detail_nation = st.session_state.df.copy()
        # df_detail_nation = df_detail_nation[df_detail_nation['Nation'] == st.session_state.nation][['Raceid', 'Racedate', 'Place', 'Nation', 'Discipline', 'WCPoints']]
        # df_detail_nation_grp = df_detail_nation.groupby(by=['Raceid', 'Racedate', 'Place', 'Nation', 'Discipline']).sum().reset_index()
            
        # df_detail_nation_grp['Racedate'] = pd.to_datetime(df_detail_nation_grp['Racedate'])

        # # Get calendar week
        # df_detail_nation_grp["CalendarWeek"] = df_detail_nation_grp["Racedate"].dt.isocalendar().week

        # # Map calendar weeks to sequential race weeks
        # week_map = {cw: i+1 for i, cw in enumerate(sorted(df_detail_nation_grp["CalendarWeek"].unique()))}
        # df_detail_nation_grp["Raceweek"] = df_detail_nation_grp["CalendarWeek"].map(week_map)


        # fig_points_per_week_single = px.line(
        #     df_detail_nation_grp[['Nation', 'Raceweek', 'Raceid', 'WCPoints', 'Discipline']].groupby(['Raceweek', 'Nation'], as_index=False).aggregate({
        #         "Raceid": "count",
        #         "WCPoints": "sum",
        #         "Discipline": list
        #     }).rename(columns={"Raceid": "Race(s)"}),
        #     x='Raceweek',
        #     y='WCPoints',
        #     color='Nation',
        #     hover_data=['Race(s)', 'Discipline']
        # )
        # fig_points_per_week_single.update_traces(mode="markers+lines")
        # st.plotly_chart(fig_points_per_week_single, use_container_width=True)


        df_athletes = df_details[(df_details['Nation'] == st.session_state.nation)& (df_details['Position']!=0)][["Gender", "Racedate", "Place", "Discipline", "Position", "Competitorname", "WCPoints"]]
        df_athletes = df_athletes.sort_values(by=['Racedate', 'Position'])
        
        #*Bar Chart Race with scoring athletes and points scored
        df_athletes_bar_chart = df_athletes.copy()
        df_athletes_bar_chart['Race'] = df_athletes_bar_chart['Racedate'].astype(str) + " " + df_athletes_bar_chart['Place']

        st.subheader(f"Points per Race")
        discipline_title = DISCIPLINES.get(st.session_state.discipline)
        gender_title = GENDER.get(st.session_state.gender)
        st.write(f"{st.session_state.nation} {discipline_title} {gender_title}")

        fig_athlete_points_per_race = px.bar(
            df_athletes_bar_chart,
            x="Race",
            y="WCPoints",
            color="Competitorname",
            text="WCPoints",
            hover_data={
                "Discipline":True,
                "Race":False,
                "Racedate": True,
                "Place": True
            },
            labels={
                "Competitorname": "Athlete",
                "Racedate": "Date"
            }
        )
        fig_athlete_points_per_race.update_xaxes(
            tickangle = -45,

            title_standoff = 25)
        fig_athlete_points_per_race.update_layout(
            height=600
        )
        st.plotly_chart(fig_athlete_points_per_race, use_container_width=True)


        #* Total Points per Athlete
        df_points_per_athlete = df_athletes[['Competitorname', 'WCPoints']].groupby('Competitorname').sum().reset_index()
        df_points_per_athlete = df_points_per_athlete.sort_values(by=['WCPoints'], ascending=False)
        st.subheader("Points per Athlete")
        st.dataframe(
            df_points_per_athlete,
            column_config={
                'Competitorname': 'Athlete'
            },
            hide_index=True
        )
        
        #*Scoring athletes table
        st.subheader("Scoring Athletes")
        st.dataframe(
            df_athletes,
            column_config={
                "Racedate": "Date", 
                "Position": "Rank",
                "Competitorname": "Athlete",
            },
            hide_index=True
        )

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