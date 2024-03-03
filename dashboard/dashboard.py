import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import matplotlib
matplotlib.use('TkAgg')

sns.set(style="dark")

def create_season_review(df):
    season_df = all_df.groupby(by="season_x").agg({
      "casual_x" : "sum",
      "registered_x" :"sum",
      "cnt_x" : "sum"
    })
    season_df = season_df.reset_index()
    season_df.rename(columns={
       "casual_x" : "unregistered",
       "registered_x" : "registered",
       "cnt_x" : "total"
     },inplace=True)
    return season_df

def create_monthly_review(df):
    monthly_review_df = all_df.groupby(by='mnth_x').agg({
       "casual_x" : "sum",
       "registered_x" :"sum",
       "cnt_x" :"sum"
     })
    monthly_review_df.rename(columns={
       "casual_x" : "unregistered",
       "registered_x" : "registered",
       "cnt_x" : "total"
     },inplace=True)
    return monthly_review_df

def create_rfm_df(df):
    rfm_df = all_df.groupby(by="instant", as_index=False).agg({
       "dteday_x": "max", #mengambil tanggal order terakhir
       "holiday_x": "nunique",
       "casual_x": "sum"
    })
    rfm_df.columns = ["index", "max_date", "frequency", "monetary"]
    #rfm_df["max_date"]=pd.to_datetime(rfm_df['max_date'])
    rfm_df["max_date"] = rfm_df["max_date"].dt.date
    recent_date = all_df["dteday_y"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_date"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_date", axis=1, inplace=True)
    return rfm_df

#Import dataset and formatting dataset
all_df = pd.read_csv("all_data.csv")
all_df["dteday_y"]=pd.to_datetime(all_df['dteday_y'])
all_df["dteday_x"]=pd.to_datetime(all_df['dteday_x'])
datetime_columns = ["dteday_x", "dteday_y"]
all_df.sort_values(by="dteday_x", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Filter data
min_date = all_df["dteday_x"].min()
max_date = all_df["dteday_x"].max()

with st.sidebar:
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Timeline',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["dteday_x"] >= str(start_date)) & 
                (all_df["dteday_x"] <= str(end_date))]

#Prepare dataset for dashboarding
season_df = create_season_review(main_df)
monthly_review_df = create_monthly_review(main_df)
rfm_df = create_rfm_df(main_df)

#Visualize data by season
st.header("Bike Sharing Data Review")
st.subheader("Seasonly Bike Rent Review")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))

colors = ["#D3D3D3", "#D3D3D3","#72BCD4", "#D3D3D3"]

sns.barplot(x="season_x", y="total", data=season_df.head(5), hue=colors, ax=ax[0], legend=False)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Total Bike Sharing", loc="center", fontsize=18)
ax[0].tick_params(axis ='y', labelsize=15)

sns.barplot(x="season_x", y="registered", data=season_df.head(5), hue=colors, ax=ax[1], legend=False)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Best Registered Bike Sharing", loc="center", fontsize=18)
ax[1].tick_params(axis='y', labelsize=15)

plt.suptitle("Best Total and Registered Bike Sharing by Season", fontsize=20)
st.pyplot(plt.gcf())
#plt.show()


#Visualize data by month
st.subheader("Bike Rent Monthly Review")
fig, ax = plt.subplots(nrows = 1, ncols = 1, figsize=(10,5))
monthly_review_df['total'].plot(kind='line', title='Total Bike Sharing Monthly', marker = 'o', linewidth=2)
plt.gca().spines[['top', 'right']].set_visible(False)
st.pyplot(plt.gcf())

#Visualise RFM Analyse
st.subheader("RFM Analysis")
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))

colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

sns.barplot(y="recency", x="index", data=rfm_df.sort_values(by="recency", ascending=True).head(5), hue=colors, ax=ax[0], legend=False)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis ='x', labelsize=15)

sns.barplot(y="frequency", x="index", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), hue=colors, ax=ax[1], legend=False)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15)

sns.barplot(y="monetary", x="index", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), hue=colors, ax=ax[2], legend=False)
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[2].tick_params(axis='x', labelsize=15)

plt.suptitle("Most Casual Renters Based on RFM Parameters (instant)", fontsize=20)
st.pyplot(plt.gcf())
#plt.show()