import streamlit as st
from src.auth import load_authenticator
from src.data import load_processed_data, get_user_data, load_admin_data
from src.ui import apply_custom_css, display_dashboard, display_admin_dashboard

st.set_page_config(
    page_title="Çalışan İzin Paneli",
    page_icon="📅",
    layout="centered"
)

# 1. Apply UI Styles
apply_custom_css()

# 2. Setup Authentication
authenticator = load_authenticator()
try:
    authenticator.login()
except Exception as e:
    st.error(e)

# 3. Handle Application State
if st.session_state.get('authentication_status'):
    # Show Logout in Sidebar
    authenticator.logout('Çıkış Yap', 'sidebar')
    st.sidebar.markdown("### Giriş Yapan")
    st.sidebar.markdown(f"**{st.session_state['name']}**")
    
    # Route Logic based on active username
    if st.session_state['username'] == 'admin':
        # Admin Route
        df_merge = load_admin_data()
        display_admin_dashboard(df_merge)
    else:
        # Standard User Route
        df = load_processed_data()
        user_data = get_user_data(df, st.session_state['username'])
        
        if user_data is None:
            st.error("Size ait izin verisi bulunamadı. Lütfen IK ile iletişime geçiniz.")
        else:
            display_dashboard(user_data.iloc[0])
            
elif st.session_state.get('authentication_status') is False:
    st.error('Kullanıcı adı veya şifre hatalı. Lütfen tekrar deneyiniz.')
elif st.session_state.get('authentication_status') is None:
    st.info('Lütfen size iletilen kullanıcı adı ve şifrenizle giriş yapınız.')
