import streamlit as st
import pandas as pd
import plotly.express as px

from st_aggrid import AgGrid

from helpers import data_functions as d
from helpers.ag_grid_options import custom_css, grid_options, grid_options_1, grid_options_2

def overall_view(df_nations_overall, df_wcpoints_overall, color_mapping, top5):
    st.subheader("Overall Points Nations")
                
    overall_nation_cup_fig = px.bar(
        df_nations_overall,
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

    df_summary_table = df_wcpoints_overall[['Nation', 'Position', 'Discipline', 'WCPoints', 'Gender']]
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
    df_overall_nation = df_nations_overall
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
    nation_order = df_nations_overall['Nation']
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
    df_percentage_per_raceweek = df_wcpoints_overall[df_wcpoints_overall['WCPoints']!=0].copy()
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