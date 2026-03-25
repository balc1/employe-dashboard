import pandas as pd
import random
import toml
import json
from pathlib import Path
from unidecode import unidecode
import streamlit_authenticator as stauth

def generate_username(name):
    if pd.isna(name):
        return "unknown"
    name_str = str(name).strip()
    safe_name = unidecode(name_str).lower()
    username = ''.join(e for e in safe_name if e.isalnum())
    return username

def generate_password():
    return f"{random.randint(10000000, 99999999)}"

def main():
    data_path = Path("data/Yıllık İzin Bakiye.xlsx")
    if not data_path.exists():
        print(f"File not found: {data_path}")
        return

    print("Reading original excel file...")
    # Read the data, treat blank values securely
    df = pd.read_excel(data_path)
    df = df.fillna("")
    
    processed_data = df.copy()
    credentials_export = []
    
    secrets_dict = {
        "credentials": {
            "usernames": {}
        },
        "cookie": {
            "expiry_days": 30,
            "key": "some_random_signature_key",
            "name": "employee_dashboard_cookie"
        },
        "pre-authorized": {
            "emails": []
        }
    }

    # -- ADD ADMIN USER FIRST --
    admin_password = generate_password()
    credentials_export.append({
        "ADI SOYADI": "Sistem Yöneticisi",
        "Kullanıcı Adı": "admin",
        "Şifre": admin_password
    })
    
    secrets_dict["credentials"]["usernames"]["admin"] = {
        "email": "admin@example.com",
        "failed_login_attempts": 0,
        "logged_in": False,
        "name": "Sistem Yöneticisi",
        "password": admin_password
    }

    usernames_seen = {}
    processed_usernames = []

    for index, row in df.iterrows():
        fullname = row.get("ADI SOYADI", "Bilinmeyen Kullanıcı")
        base_username = generate_username(fullname)
        
        if base_username in usernames_seen:
            usernames_seen[base_username] += 1
            username = f"{base_username}{usernames_seen[base_username]}"
        else:
            usernames_seen[base_username] = 0
            username = base_username

        password = generate_password()
        
        credentials_export.append({
            "ADI SOYADI": fullname,
            "Kullanıcı Adı": username,
            "Şifre": password
        })
        
        secrets_dict["credentials"]["usernames"][username] = {
            "email": f"{username}@example.com",
            "failed_login_attempts": 0,
            "logged_in": False,
            "name": fullname,
            "password": password
        }

        processed_usernames.append(username)

    print("Hashing passwords...")
    raw_passwords = [v["password"] for k, v in secrets_dict["credentials"]["usernames"].items()]
    hashed_passwords = stauth.Hasher.hash_list(raw_passwords)
    
    for (k, v), hashed in zip(secrets_dict["credentials"]["usernames"].items(), hashed_passwords):
        v["password"] = hashed

    # Configure dataset for UI reading internally via Secrets JSON Database
    processed_data["username"] = processed_usernames
    
    # Process Datatime columns inside pandas back to strings so JSON won't crash
    for c in processed_data.columns:
        if pd.api.types.is_datetime64_any_dtype(processed_data[c]):
            processed_data[c] = processed_data[c].dt.strftime('%Y-%m-%d')
            
    db_json = processed_data.to_dict(orient="records")
    secrets_dict["database_json"] = json.dumps(db_json, ensure_ascii=False)
    
    creds_json = pd.DataFrame(credentials_export).to_dict(orient="records")
    secrets_dict["credentials_json"] = json.dumps(creds_json, ensure_ascii=False)

    secrets_path = Path(".streamlit/secrets.toml")
    secrets_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(secrets_path, "w", encoding="utf-8") as f:
        toml.dump(secrets_dict, f)
    print(f"Created: {secrets_path}")
    
    # Create the text file for the user to securely copy entirely for Streamlit Cloud
    with open("STREAMLIT_SECRETS_KOPYALA.txt", "w", encoding="utf-8") as f:
        f.write("# BU METNI STREAMLIT CLOUD'DAKI ADVANCED SETTINGS -> SECRETS ALANINA KOPYALAYIN\n")
        f.write("# DIKKAT: BU DOSYAYI KIMSE GORMEMELIDIR VE GITHUB'A YUKLENMEMELIDIR!\n\n")
        f.write(toml.dumps(secrets_dict))
    print("Created: STREAMLIT_SECRETS_KOPYALA.txt")

    # Keep a local static file strictly for the offline HR supervisor locally!
    export_df = pd.DataFrame(credentials_export)
    export_path = Path("data/Kullanici_Sifreleri.xlsx")
    export_path.parent.mkdir(parents=True, exist_ok=True)
    export_df.to_excel(export_path, index=False)
    print(f"Created: {export_path}")

if __name__ == "__main__":
    main()
