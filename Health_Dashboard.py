###################################### LIBRARIES ##########################################################
#%%
import streamlit as st
import pandas as pd
import numpy as np
import datetime
#import matplotlib.pyplot as plt
import altair as alt

#%%

st.set_page_config(
        page_title="Health-App",
        page_icon="🧊",
        #layout="wide",
        initial_sidebar_state="expanded")

####### Add the padding
padding = 0
st.markdown(f""" <style>
    .reportview-container .main .block-container{{
        padding-top: {padding}rem;
        padding-right: {padding}rem;
        padding-left: {padding}rem;
        padding-bottom: {padding}rem;
    }} </style> """, unsafe_allow_html=True)
    
#%%

########################################## TITLE HEADER ############################################
col1, col2 = st.beta_columns([0.3,1])
with col2:
    st.title('My Health Dashboard')
#st.text("")
#st.text("")
st.markdown("------------------")

last_year = datetime.date(2020, 3, 16)

###################################### LOAD DATA 

@st.cache
def load_data():
    workout_df = pd.read_json('/Users/ziadNader/Desktop/Personal Projects/Apple Health /streamlit-app/workouts_processed.json')
    return workout_df

workout_df = load_data()

################# ADD BUTTONS FOR WALKING AND choosing a metric ################

walking = st.sidebar.checkbox('Exclude Walking workout')
metric = st.sidebar.radio('Choose a metric to compare:',
                          ['calories', 'duration', 'distance'])

if walking:
    workout_df = workout_df[workout_df['workout'] != 'Walking'].copy()

########## Display total metrics on everything ##############################

#TOP 3 ALL TIME
#TOP 3 LAST 30 DAYS
col1, col2 = st.beta_columns(2)
with col1:
    st.text("All time")
    st.bar_chart(workout_df.groupby('workout')[metric].mean()[:10], 
                 width=700, height=300)
    #st.bar_chart(workout_df.groupby('workout')[metric].sum()[:10],  
                 #width=300, height=300)
    

with col2:
    st.text("Last 30 days")
    st.bar_chart(workout_df.loc[datetime.date(2021, 1, 16):]
                .groupby('workout')[metric].mean()[:10], 
                width=700, height=300)
    #st.bar_chart(workout_df.loc[datetime.date(2021, 1, 16):].groupby('workout')[metric].sum()[:10])
    
    


################################
df_year = workout_df.groupby(['workout', 'year'])[metric]\
                       .sum()\
                       .reset_index()\
                       .pivot(index='year',
                              columns='workout',
                              values=metric).fillna(0).copy()
df_year.columns.name = None               #remove categories


#st.text(workout_df.workout.unique().index('Walking')) 
# create the sidebar multiselect to select workouts                                                                          
selected_workouts = st.multiselect('Select the workouts',
                                   list(workout_df.workout.unique()),
                                    default=['Running'])
##############
# add the the date range for days where there hasn't been all workouts
dtr = pd.date_range('15.12.2017', '03.09.2021', freq='D')
s = pd.Series(index=dtr)
df = pd.concat([workout_df,s[~s.index.isin(workout_df.index)]]).sort_index()
############
# drop the 0 axis from the dataframe
df = df.drop([0],axis=1).fillna(0)
#st.dataframe(df[df['workout']=='Running'])
df_workout = df[df['workout'].isin(selected_workouts)]
#df_rolling_workout = df[df['workout']=='RPM'][metric].rolling(30).sum()
df_rolling_workout = pd.concat([df_workout,s[~s.index.isin(df_workout.index)]]).sort_index()
df_rolling_workout = df_rolling_workout.drop([0],axis=1).fillna(0)
#st.dataframe(df_rolling_workout[metric].rolling(63).sum())
df_rolling_pivot = df_rolling_workout.pivot(columns='workout', values=metric).fillna(0).copy()
#st.dataframe(df_rolling_pivot)
df_rolling_pivot.columns.name = None
df_rolling_pivot = df_rolling_pivot.drop([0],axis=1)
#df_rolling_pivot = df_rolling_pivot.reset_index() 
#st.dataframe(df_rolling_pivot)
st.line_chart(df_rolling_pivot.loc[last_year:].resample('W').sum())
#st.line_chart(df_rolling_pivot.ewm(com=60).mean())

#st.line_chart(df.groupby(['year', 'week'])[metric].sum())

#######
with st.beta_expander("More details"):
   st.write("""
        The chart above explains the trends for each workout selected 
        during the years
     """)
######### Calculate performance

#st.text(str(calories_pre/duration_pre))
#st.text(str(calories_post/duration_post))
    

st.markdown("----")



st.subheader("Weekly Analysis ")
#################################### DATE SELECTION ##################################

col1, col2, col3 = st.beta_columns([0.1,1,1])

with col3:
   
    end_date1 = st.date_input("End date:", 
                              datetime.date(2020, 3, 16),
                              help='Start date of the first period')
    end_date2 = st.date_input("End date if second period:", 
                              datetime.date(2021, 3, 16),
                              help='End date of the second period')
with col2:
    start_date1 = st.date_input("Start date:", 
                                datetime.date(2019, 3, 16),
                                help='Start date of the first period')

    start_date2 = st.date_input("Start date of second period:", 
                                end_date1,
                                help='Start date of the second period')

    


if start_date1 <= end_date1:
    workout_df_time = workout_df.loc[start_date1:end_date1].copy()
    workout_df_time2 = workout_df.loc[start_date2:end_date2].copy()
else:
    st.warning('Start date must be less than end date')
    st.stop()
    workout_df_time = workout_df 


################### PRE COVID POST COVID
pre_covid = st.sidebar.checkbox("Pre-Covid")

precovid_start_date = datetime.date(2019, 3, 16)
precovid_end_date = datetime.date(2020, 3, 16) #Used also for post covid start
postcovid_end_date = datetime.date(2021, 3, 16)

@st.cache
def split_data(workout_df):
    workout_df_precovid = workout_df.loc[precovid_start_date:precovid_end_date]
    workout_df_postcovid = workout_df.loc[precovid_end_date:postcovid_end_date]
    return workout_df_precovid, workout_df_postcovid


workout_df_precovid = split_data(workout_df)[0]
workout_df_postcovid = split_data(workout_df)[1]



############################### Metric chosen #################################

workout_pre_metric = workout_df_precovid.groupby('workout')[metric].sum()
workout_post_metric = workout_df_postcovid.groupby('workout')[metric].sum()
workout_versus = pd.merge(workout_pre_metric, workout_post_metric, 
                          how="outer", left_index=True, right_index=True,
                          suffixes=(" pre", " post")).reset_index()
workout_versus = workout_versus.fillna(0)

st.text("")
st.text("")
st.text("")

workout_versus['sum_metric'] = workout_versus[metric + ' pre'] + \
                               workout_versus[metric + ' post']

workout_vs_sorted = workout_versus.sort_values(by='sum_metric', 
                                               ascending=False)


workout_vs_melt = workout_vs_sorted.drop(columns='sum_metric', 
                                         axis=1)\
                                         .melt('workout')

if metric == 'calories:':
    col_value = 'calories (Kcal)'
elif metric == 'distance':
    col_value = 'distance (Km)'
else:
    col_value = 'duration (Minutes)'

workout_vs_melt = workout_vs_melt.rename(columns={"value": col_value,
                                                  "variable": 'period'})


with st.beta_container():
    click = alt.selection_multi(encodings=['x'])
    #st.text(brush)
    c = alt.Chart(workout_vs_melt).mark_circle().encode(
             x=alt.X('workout', sort=None),
             y=col_value,
             #color='variable',
             color=alt.condition(click, 'period', alt.value('lightblue')),
             size=alt.Size(col_value, scale=alt.Scale(range=[10, 3000])),
             tooltip=['workout', col_value, 'period']
    ).add_selection(
    click).properties(
    width=600,
    height=300
)
    #st.altair_chart(c, use_container_width=True)
    #st.text(metric)
    bars = alt.Chart(workout_vs_melt).mark_bar().encode(
    y='period',
    color='period',
    x=alt.X(col_value, aggregate='sum', 
            type='quantitative')
    #text='sum(str((metric))'
    ).transform_filter(
    click
    ).properties(
    width=600,
    height=50
)


    st.altair_chart(c & bars, use_container_width=True)



with st.beta_expander("More details"):
   st.write("""
        The above charts measure thte total for each metric of calories,
        distance and duration for the selected workouts
     """)

############ Create the bar chart for day of week
st.text("")
st.text("")
st.text("")

################################### METRIC ###############################


st.markdown("----")

st.subheader('Select a type of workout')
st.text("")


####### Add a feature on per year


    
####################### EVOLUTION OVER TIME #####################################

##################### Detailed Analysis ########
st.subheader("Detailed Analysis")


############# Extract the date #################
workout_df_time['startDate'] = workout_df_time['startDate']\
                                .apply(lambda x: x[:10])


workout_df_time2['startDate'] = workout_df_time2['startDate']\
                                .apply(lambda x: x[:10])


#########
frequency = st.sidebar.radio('Select a type of analysis:',
                 ['Weekly', 'Monthly'])



############### Create the chart for Weekly ###################

if frequency == 'Weekly':
    st.write("Weekly analysis")
    date_indexes = workout_df_time.groupby(by=['week', 'year'])['startDate']\
                                  .first()\
                                  .reset_index(drop=True)

    date_indexes2 = workout_df_time2.groupby(by=['week', 'year'])['startDate']\
                                .first()\
                                .reset_index(drop=True)

    metrics_df = pd.DataFrame(workout_df_time.groupby(by=['week', 'year'])\
                        ['calories']\
                        .sum()\
                        .reset_index(drop=True))

    metrics_df2 = pd.DataFrame(workout_df_time2.groupby(by=['week', 'year'])\
                        ['calories']\
                        .sum()\
                        .reset_index(drop=True))

elif frequency == 'Monthly':
    st.write("Monthly analysis")
    date_indexes = workout_df_time.groupby(by=['month', 'year'])['startDate']\
                                  .first()\
                                  .reset_index(drop=True)

    date_indexes2 = workout_df_time2.groupby(by=['month', 'year'])['startDate']\
                                .first()\
                                .reset_index(drop=True)

    metrics_df = pd.DataFrame(workout_df_time.groupby(by=['month', 'year'])\
                        ['calories']\
                        .sum()\
                        .reset_index(drop=True))

    metrics_df2 = pd.DataFrame(workout_df_time2.groupby(by=['month', 'year'])\
                        ['calories']\
                        .sum()\
                        .reset_index(drop=True))


# col1, col2 = st.beta_columns(2)
# with col1:
#     st.bar_chart(metrics_df.set_index(date_indexes).sort_index(),
#                  use_container_width=True)
# with col2:
#     st.bar_chart(metrics_df2.set_index(date_indexes2).sort_index(),
#                  use_container_width=True)

with st.beta_container():

    st.bar_chart(metrics_df.set_index(date_indexes).sort_index(),
                 use_container_width=True)
    st.bar_chart(metrics_df2.set_index(date_indexes2).sort_index(),
                 use_container_width=True)



    # st.write("""
    #     The chart above shows some numbers I picked for you.
    #     I rolled actual dice for these, so they're *guaranteed* to
    #      be random.
    #  """)

############ Create the bar chart for day of week
with st.beta_expander("Peak Hour of the day"):
    st.text("")

    #st.write("Hourly analysis")
    hour_indexes = workout_df_time.groupby(by=['hour'])['hour']\
                                .first()\
                                .reset_index(drop=True)

    hour_df1 = pd.DataFrame(workout_df_time.groupby(by='hour')\
                            ['calories']\
                            .sum()\
                            .reset_index(drop=True))

    hour_df2 = pd.DataFrame(workout_df_time2.groupby(by='hour')\
                            ['calories']\
                            .sum()\
                            .reset_index(drop=True))


    hour_df = pd.merge(hour_df1, hour_df2, how='left', 
                    left_index=True, right_index=True,
                    suffixes=(' pre-covid', ' during covid'))

    peak_hour = hour_df2
    st.bar_chart(hour_df.set_index(hour_indexes))    
    st.write("")  
    # st.bar_chart(hour_df2.set_index(hour_indexes).sort_index())   


with st.beta_expander("Peak day of the week"):
    st.write("""
            The chart above shows some numbers I picked for you.
            I rolled actual dice for these, so they're *guaranteed* to
            be random.
        """)

    ############ Create the bar chart for day of week
  
    day_indexes = workout_df_time.groupby(by=['day_of_week'])['day_of_week']\
                                .first()\
                                .reset_index(drop=True)

    days_of_week = {0:'Mon', 
                    1:'Tue', 
                    2:'Wed',
                    3:'Thu', 
                    4:'Fri', 
                    5:'Sat',
                    6:'Sun'}

    day_indexes_map = day_indexes.map(days_of_week)

    day_of_week_df1 = pd.DataFrame(workout_df_time.groupby(by='day_of_week')\
                                                ['calories']\
                                                .sum()\
                                                .reset_index(drop=True))


    day_of_week_df2 = pd.DataFrame(workout_df_time2.groupby(by='day_of_week')\
                                                    ['calories']\
                                                    .sum()\
                                                    .reset_index(drop=True))


    day_of_week_df = pd.merge(day_of_week_df1, day_of_week_df2, 
                              how='left', left_index=True, 
                              right_index=True, 
                              suffixes=(' pre-covid', ' during covid'))

    st.bar_chart(data= (day_of_week_df.set_index(day_indexes_map)), 
                 width=10, height=400)  
