
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Load credentials from Streamlit secrets
creds_dict = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(creds_dict, scopes=[
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
])

# Google Sheet details
SHEET_ID = st.secrets["SHEET_ID"]
FORMULA_WS = st.secrets.get("FORMULA_WS", "FORMULA")
INVENTORY_WS = st.secrets.get("INVENTORY_WS", "INVENTORY")

# Connect to Google Sheets
gc = gspread.authorize(creds)
sh = gc.open_by_key(SHEET_ID)
formula_ws = sh.worksheet(FORMULA_WS)
inventory_ws = sh.worksheet(INVENTORY_WS)

# Load data
formula_df = pd.DataFrame(formula_ws.get_all_records())
inventory_df = pd.DataFrame(inventory_ws.get_all_records())

st.title("📦 Shotcraft Inventory Tracker (Google Sheets Live Sync)")

st.subheader("Formula (Per Case)")
st.dataframe(formula_df)

st.subheader("Current Inventory")
edited_inventory = st.data_editor(inventory_df, num_rows="dynamic")

if st.button("💾 Sync On_Hand to Google Sheets"):
    inventory_ws.clear()
    inventory_ws.update([edited_inventory.columns.values.tolist()] + edited_inventory.values.tolist())
    st.success("Inventory updated in Google Sheets!")

st.subheader("Calculate Inventory After Sales")
cases_sold = st.number_input("Enter cases sold", min_value=0, step=1)

if st.button("📉 Calculate Remaining Inventory"):
    result_df = formula_df.copy()
    result_df["Used"] = result_df["Per_Case"] * cases_sold
    merged = pd.merge(edited_inventory, result_df[["Component", "Used"]], on="Component", how="left")
    merged["Remaining"] = merged["On_Hand"] - merged["Used"]
    st.dataframe(merged[["Component", "On_Hand", "Used", "Remaining"]])
