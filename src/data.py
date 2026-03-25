import pandas as pd
import streamlit as st
import json

@st.cache_data
def load_processed_data():
    """Loads the main dataset from Streamlit Secrets JSON memory internally."""
    try:
        db_json_str = st.secrets["database_json"]
        data_list = json.loads(db_json_str)
        df = pd.DataFrame(data_list)
        return df
    except Exception as e:
        st.error(f"Veri yüklenirken bir güvenlik hatası oluştu: {e}")
        st.stop()

def get_user_data(df, username):
    """Filters the memory dataset to match the specific user."""
    user_data = df[df['username'] == username]
    return user_data if not user_data.empty else None

@st.cache_data
def load_admin_data():
    """Builds the admin data merge completely from secure Secrets strings."""
    try:
        db_json_str = st.secrets["database_json"]
        creds_json_str = st.secrets["credentials_json"]
        
        df_processed = pd.DataFrame(json.loads(db_json_str))
        df_creds = pd.DataFrame(json.loads(creds_json_str))
        
        df_merge = pd.merge(
            df_creds,
            df_processed, 
            left_on='Kullanıcı Adı',
            right_on='username',
            how='left'
        )
        return df_merge
    except Exception as e:
        st.error(f"Admin verileri yüklenirken güvenlik hatası oluştu: {e}")
        return None
