import streamlit as st
import pandas as pd

def apply_custom_css():
    st.markdown("""
    <style>
        .main-header {
            text-align: center;
            color: #1E3A8A;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin-bottom: 2rem;
        }
        .metric-card {
            background-color: #F8FAFC;
            padding: 24px;
            border-radius: 12px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            text-align: center;
            transition: transform 0.2s ease-in-out;
        }
        .metric-card:hover {
            transform: translateY(-5px);
        }
        .metric-title {
            color: #64748B;
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 8px;
            text-transform: uppercase;
        }
        .metric-value {
            color: #0F172A;
            font-size: 2.8rem;
            font-weight: 800;
        }
        .metric-value.highlight {
            color: #2563EB;
        }
    </style>
    """, unsafe_allow_html=True)

def display_dashboard(user_data_row):
    fullname = user_data_row.get('ADI SOYADI', 'Çalışan')
    izin_bakiye = user_data_row.get('IZIN BAKIYE', 0)
    
    yenileme_tarihi_raw = None
    for col in user_data_row.index:
        if 'Yenileme Tarihi' in col:
            yenileme_tarihi_raw = user_data_row[col]
            break
            
    st.markdown(f"<h1 class='main-header'>Hoş Geldiniz, {fullname} 👋</h1>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    formatted_date = "-"
    if pd.notna(yenileme_tarihi_raw):
        try:
            if isinstance(yenileme_tarihi_raw, str):
                dt = pd.to_datetime(yenileme_tarihi_raw)
            else:
                dt = yenileme_tarihi_raw
                
            aylar = {1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 
                     5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos", 
                     9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"}
            formatted_date = f"{dt.day} {aylar.get(dt.month, '')}"
        except Exception:
            formatted_date = "Geçersiz Tarih"
            
    st.markdown("### İzin Bilgileriniz")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Kalan Yıllık İzin</div>
            <div class="metric-value highlight">{izin_bakiye} <span style="font-size: 1.2rem; color: #64748B;">Gün</span></div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">İzin Yenileme Tarihi</div>
            <div class="metric-value">{formatted_date}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.info("💡 **Bilgi:** Bu veriler en son güncellenen izin tablosundan çekilmektedir. Herhangi bir uyumsuzluk durumunda lütfen İnsan Kaynakları departmanı ile iletişime geçiniz.")

def display_admin_dashboard(df_merge):
    st.markdown("<h1 class='main-header'>👑 Yönetici (Admin) Paneli</h1>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    if df_merge is None or df_merge.empty:
        st.warning("Gösterilecek veri bulunamadı.")
        return
        
    st.markdown("### 📋 Tüm Çalışan İzinleri ve Şifre Listesi")
    st.info("Bu sayfada sisteme kayıtlı tüm çalışanların oluşturulan güncel şifreleri ile birlikte kalan izin haklarını takip edebilirsiniz.")
    
    # Pre-process Dataframe for displaying properly
    display_df = pd.DataFrame()
    # Adı Soyadı comes from credentials dataset if we did a left join on it, so it might be named ADI SOYADI_x
    display_df['Adı Soyadı'] = df_merge['ADI SOYADI_x'] if 'ADI SOYADI_x' in df_merge.columns else df_merge.get('ADI SOYADI', '-')
    display_df['Kullanıcı Adı'] = df_merge['Kullanıcı Adı']
    display_df['Şifre'] = df_merge['Şifre']
    
    if 'IZIN BAKIYE' in df_merge.columns:
        display_df['Kalan İzin (Gün)'] = df_merge['IZIN BAKIYE']
    else:
        display_df['Kalan İzin (Gün)'] = None
        
    date_col = None
    for c in df_merge.columns:
        if 'Yenileme Tarihi' in c:
            date_col = c
            break
            
    if date_col:
        def fmt_date(d):
            if pd.isna(d) or str(d).strip() == '': return "-"
            try:
                dt = pd.to_datetime(d)
                aylar = {1:"Ocak", 2:"Şubat", 3:"Mart", 4:"Nisan", 5:"Mayıs", 6:"Haziran", 7:"Temmuz", 8:"Ağustos", 9:"Eylül", 10:"Ekim", 11:"Kasım", 12:"Aralık"}
                return f"{dt.day} {aylar.get(dt.month, '')}"
            except:
                return str(d)
        display_df['Yenileme Tarihi'] = df_merge[date_col].apply(fmt_date)
        
    # We remove 'admin' from the table list to keep it pure employee list
    display_df = display_df[display_df['Kullanıcı Adı'] != 'admin'].reset_index(drop=True)
    
    # Fill nan strictly (leaves missing data visually clean)
    display_df = display_df.fillna("-")
    
    st.dataframe(
        display_df, 
        use_container_width=True,
        hide_index=True
    )
    
    # Add a metric summary
    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns(2)
    with cols[0]:
        st.metric("Toplam Çalışan Sayısı", len(display_df))
    with cols[1]:
        # safely sum because it might contain "-"
        total_leave = pd.to_numeric(display_df['Kalan İzin (Gün)'], errors='coerce').sum()
        st.metric("Şirket Geneli Toplam İzin Hakları", f"{total_leave:g} Gün")
