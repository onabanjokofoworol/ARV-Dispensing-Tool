import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title='DLT Refill Calculator App',page_icon='💊')
st.title('🏥DLT Refill Assistant')
st.subheader('Dolutegravir/Lamivudine/Tenofovir')
st.sidebar.header('Patient Data Entry')
name = st.sidebar.text_input('Patient Full Name')
pills_left = st.sidebar.number_input('Pills left at home', min_value=0, value=0)
supply = st.sidebar.number_input('No. of pills dispensed', min_value=0, value=30)
taken = st.sidebar.radio("Has today's dose been taken?",('No', 'Yes'))
if taken == 'No':
    st.error(f"🚨ACTION REQUIRED: Counsel {name} to take today's dose")

today = datetime.now()
start_calc = today + timedelta(days=1) if taken == 'Yes' else today
start_date_new = start_calc + timedelta(days=pills_left)
end_date_new = start_date_new + timedelta(days=supply)

if st.sidebar.button('Generate Dispensing Label'):
    today = datetime.now()

if supply ==0:
    st.error('🚨ERROR: You cannot dispense 0 tablets. Please enter the new supply amount.')
elif name == '':
    st.warning("⚠Please enter your patient's full name.")
else:
    today = datetime.now()
    start_calc = today + timedelta(days=1)
if taken == "Yes":
    start_date_new = start_calc + timedelta(days=pills_left)
end_date_new = start_date_new + timedelta(days=supply)

if pills_left > 0:
    finish_old_by = (today + timedelta(days=pills_left)).strftime('%d/%b/%y')
    med_instructions = f"FINISH OLD STOCK BY: {finish_old_by}\nSTART THIS BOTTLE ON: {start_date_new.strftime('%d/%b%y')}"
else:
    med_instructions = f"START THIS BOTTLE IMMEDIATELY"


label = f""" 
{'='*30}
{'DOSAGE & REFILL GUIDE':^30}
{'='*30}
Name: {name}
Date of Visit: {today.strftime('%d/%b/%y')}
{'-'*30}
{med_instructions}
FINISH NEW BOTTLE BY: {end_date_new.strftime('%d/%b/%y')}
{'-'*30}
Keep Silica gel inside always
Take only one tablet daily
{'='*30}
"""

st.subheader('Generate Dispensing Label')
st.code(label, language='text')
st.download_button(
    label='Download Label for Printing',
    data= label,
    file_name= f'Label_{name}.txt',
    mime= 'text/plain')

import pandas as pd
import os

new_entry = {
    "Date": today.strftime('%d/%b/%y'),
    "Patient Full Name": name,
    "Pills Left": pills_left,
    "Supply": supply,
    "Start Date": start_date_new.strftime('%d/%b/%y'),
    "End Date": end_date_new.strftime('%d/%b/%y')
}
log_file = "dispensing_history.csv"
df_new = pd.DataFrame(new_entry, index=[0])
if not os.path.isfile(log_file):
    df_new.to_csv(log_file, index=False)
else:
    df_new.to_csv(log_file, mode='a', header=False, index=False)

st.markdown("---")
st.header("📑Dispensing History")
if os.path.isfile(log_file):
    df_history = pd.read_csv(log_file)
    df_history['Date']= pd.to_datetime(df_history['Date'])
    with st.container(border=True):
        filter_col1, filter_col2 = st.columns(2)
    with (filter_col1):
        period = st.selectbox('📆Period', ["All Time", "Today", "This Week", "This Month"])
        with filter_col2:
            search_query = st.text_input('🔍Search Patient Name', placeholder='Type name to search...')

        today_date= datetime.now().date()
        filtered_df = df_history
        if period == "Today":
            filtered_df = df_history[df_history['Date'].dt.date ==today_date]
        elif period == "This Week":
            start_of_week = today_date - timedelta(days=today_date.weekday())
            filtered_df = df_history[df_history['Date'].dt.date >= start_of_week]
        elif period == "This Month":
            filtered_df = df_history[(df_history['Date'].dt.month == today_date.month) &
            (df_history['Date'].dt.year == today_date.year)]
        else:
            filtered_df= df_history

        if search_query:
            filtered_df = filtered_df[filtered_df['Patient Full Name'].str.contains(search_query, case=False, na=False)]
            if not filtered_df.empty:
                st.dataframe(filtered_df.sort_values(by="Date", ascending=False),
                             use_container_width=True, hide_index= True)
                st.write(f"📊 **Total Patients in View:** {len(filtered_df)}")
            else:
                st.warning('No records found for this search/period.')

            st.download_button('📤Export Current view to CSV',
                               data = filtered_df.to_csv(index=False),
                               file_name='pharmacy_export.csv',
                               mime = 'text/csv')
        else:
            st.info ('No records found yet. Generate your first label to start the log!')
