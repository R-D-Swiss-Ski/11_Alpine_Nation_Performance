import streamlit as st
import pandas as pd
import plotly.express as px

from datetime import datetime

from helpers import data_functions as d
from helpers.constants import GENDER, DISCIPLINES, COLOR_NATIONS

def nations_view(color_mapping, top5):

    def details(nation, gender, discipline, df_results_wcpoints):
        st.session_state.details = True
        st.session_state.main=False
        st.session_state.df = df_results_wcpoints
        st.session_state.nation = nation
        st.session_state.gender=gender
        st.session_state.discipline=discipline


    filter1, filter2, filter3 = st.columns(3)

    gender_filter = filter1.selectbox(":blue[Gender]", options=GENDER) 
    discipline_filter = filter2.selectbox(":blue[Discipline]", options=DISCIPLINES)

    #get upcoming race and last race
    date_today = datetime.today()

    #!for testing
    # date_today = datetime.strptime("2025-02-28", "%Y-%m-%d")



    df_races_season = d.get_races(st.session_state.selected_season,[gender_filter], [discipline_filter])


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
    df_results_wcpoints = d.create_wc_points_df(season=st.session_state.selected_season, genders=[gender_filter], disciplines=[discipline_filter])
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
                            st.button("Details", on_click=details, args=(row['Nation'],'All', discipline_filter, df_results_wcpoints), key=f"details_{i}")

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
                            st.button("Details", on_click=details, args=(row['Nation'], row['Gender'], discipline_filter, df_results_wcpoints), key=f"details_{i}")


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