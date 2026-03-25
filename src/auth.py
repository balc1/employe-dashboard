import streamlit as st
import streamlit_authenticator as stauth

def load_authenticator():
    """Loads credentials directly from secure Streamlit Secrets and returns the Authenticate object."""
    try:
        # Load dictionaries correctly handling AttrDict nesting
        credentials = st.secrets["credentials"].to_dict()
        cookie = st.secrets["cookie"].to_dict()
    except KeyError as e:
        st.error(f"Güvenlik Konfigürasyonu (Secrets) bulunamadı. Lütfen Streamlit Cloud ayarlarını kontrol edin. Kayıp: {e}")
        st.stop()
    except AttributeError:
        # Works perfectly on local testing and standard Streamlit dictionaries fallback
        credentials = st.secrets["credentials"]
        cookie = st.secrets["cookie"]

    authenticator = stauth.Authenticate(
        credentials,
        cookie['name'],
        cookie['key'],
        cookie['expiry_days']
    )
    return authenticator
