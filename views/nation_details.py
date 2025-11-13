import streamlit as st
import plotly.express as px


from helpers.constants import GENDER, DISCIPLINES



def nation_details_view():  

    def go_back():
        st.session_state.details = False
        st.session_state.main =True

    def ranking_race(race_name):
        st.session_state.is_ranking = True
        st.session_state.details = False
        st.session_state.main = False
        st.session_state.race = race_name


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
    
    #*Bar Chart Race with points scored
    df_nation_points = df_details[(df_details['Nation'] == st.session_state.nation)& (df_details['Position']!=0)][["Gender", "Racedate", "Place", "Discipline", "WCPoints"]]
    df_nation_points['Race'] = df_nation_points['Racedate'].astype(str) + " " + df_nation_points['Place']
    df_nation_points = df_nation_points.groupby(['Race', 'Gender', 'Racedate', 'Place', 'Discipline']).sum().reset_index()
    st.subheader(f"Points per Race")
    discipline_title = DISCIPLINES.get(st.session_state.discipline)
    gender_title = GENDER.get(st.session_state.gender)
    st.write(f"{st.session_state.nation} {discipline_title} {gender_title}")

    fig_points_per_race = px.bar(
        df_nation_points,
        x="Race",
        y="WCPoints",
        text="WCPoints",
        hover_data={
            "Discipline":True,
            "Race":False,
            "Racedate": True,
            "Place": True
        },
        labels={
            "Racedate": "Date"
        }
    )
    fig_points_per_race.update_xaxes(
        tickangle = -45,

        title_standoff = 25)
    fig_points_per_race.update_layout(
        height=600
    )
    st.plotly_chart(fig_points_per_race, width='stretch')

    #*Bar Chart Race with scoring athletes and points scored
    df_athletes_bar_chart = df_athletes.copy()
    df_athletes_bar_chart['Race'] = df_athletes_bar_chart['Racedate'].astype(str) + " " + df_athletes_bar_chart['Place']

    st.subheader(f"Points per Race per Athelte")

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

    st.plotly_chart(fig_athlete_points_per_race, width='stretch')

    #* Race Selection
    st.markdown("**Select Race to see ranking**")
    races = df_athletes_bar_chart['Race'].unique()
    cols = None
    for i, race in enumerate(races):
        if i % 5 == 0:
            cols = st.columns(5)
        col = cols[i % 5]
        with col:
            st.button(label=race, key=f"race_btn_{i}", on_click=ranking_race, args=(race,), use_container_width=True)

    

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

