import pandas as pd
from sklearn.preprocessing import OneHotEncoder

def normalize_time_string(s):
    if not s or pd.isna(s):
        return ""
    # Replace en dash and em dash with normal dash
    s = s.replace("–", "-").replace("—", "-").strip()
    return s


def preprocess_assessment(assessment, encoder=None, fit=False):
    # ✅ Map Yes/No to boolean
    own_smartphone_map = {"Yes": True, "No": False}

    # ✅ Map ranges to numeric midpoints
    screen_map = {"<2h": 2, "2–3h": 2.5, "3–4h": 3.5, "4–6h": 5, ">6h": 6}
    night_map = {"Never": 0, "<30m": 0.25, "30–60m": 0.75, "1–2h": 1.5, ">2h": 3}
    notif_map = {"<5 times": 4, "5–10 times": 7, "11–20 times": 15, ">20 times": 21}
    gaming_map = {"None": 0, "<30m": 0.25, "30-60m": 0.75, "1-2h": 1.5, ">2h": 3}
    social_map = {"<1h": 0.5, "1-2h": 1.5, "2-3h": 2.5, "3-4h": 3.5, ">4h": 5}

    gaming_time_str = normalize_time_string(assessment.gaming_time)
    social_time_str = normalize_time_string(assessment.social_time)

    # 1️⃣ Raw features
    X_raw = {
        "age": int(assessment.age),
        "gender": assessment.gender,
        "primary_device": assessment.primary_device,
        "own_smartphone": own_smartphone_map.get(assessment.own_smartphone, False),
        "mobile_data_plan": assessment.mobile_data,
        "screen_time_weekdays": screen_map.get(assessment.screen_weekdays, 0),
        "screen_time_weekends": screen_map.get(assessment.screen_weekends, 0),
        "night_phone_use": night_map.get(assessment.night_phone_use, 0),
        "notif_per_hour": notif_map.get(assessment.notif_per_hour, 0),
        "social_media_time": social_map.get(social_time_str, 0),
        "gaming_time": gaming_map.get(gaming_time_str, 0),
        "da1_time_loss": assessment.da1,
        "da2_restless": assessment.da2,
        "da3_failed_cut": assessment.da3,
        "da4_skip_tasks": assessment.da4,
        "da5_negative_emotions": assessment.da5,
        "da6_morning_check": assessment.da6,
        "da7_class_check": assessment.da7,
        "da8_family_comment": assessment.da8,
        "DAS_weighted": sum([
            assessment.da1, assessment.da2, assessment.da3, assessment.da4,
            assessment.da5, assessment.da6, assessment.da7, assessment.da8
        ]) / 8
    }

    # 2️⃣ Encode platforms as separate columns
    all_platforms = [
        'youtube','facebook','tiktok','instagram','linkedin',
        'whatsapp','x','snapchat','live streaming','gaming'
    ]
    used_platforms = [p.lower().replace(" ", "") for p in (assessment.platforms or [])]
    for p in all_platforms:
        key = f"use_{p}"
        X_raw[key] = int(p in used_platforms)  # ensures numeric 0/1

    df = pd.DataFrame([X_raw])

    # 3️⃣ One-hot encode categorical columns
    cat_cols = ["gender", "primary_device", "own_smartphone", "mobile_data_plan"]
    if fit or encoder is None:
        encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
        cat_encoded = encoder.fit_transform(df[cat_cols])
    else:
        cat_encoded = encoder.transform(df[cat_cols])

    df_cat = pd.DataFrame(cat_encoded, columns=encoder.get_feature_names_out(cat_cols))
    df_final = pd.concat([df.drop(columns=cat_cols), df_cat], axis=1)

    # 4️⃣ Ensure final column order matches model training
    TRAINING_COLUMNS = [
        'gender_Female','gender_Male',
        'primary_device_Desktop','primary_device_Laptop','primary_device_Shared devices',
        'primary_device_Smartphone','primary_device_Tablet',
        'own_smartphone_True',
        'mobile_data_plan_Always','mobile_data_plan_No','mobile_data_plan_Rarely','mobile_data_plan_Sometimes',
        'age','screen_time_weekdays','screen_time_weekends','night_phone_use','notif_per_hour',
        'social_media_time','gaming_time','da1_time_loss','da2_restless','da3_failed_cut',
        'da4_skip_tasks','da5_negative_emotions','da6_morning_check','da7_class_check','da8_family_comment',
        'use_youtube','use_facebook','use_tiktok','use_instagram','use_linkedin','use_whatsapp',
        'use_x','use_snapchat','use_live streaming','use_gaming','DAS_weighted'
    ]
    for col in TRAINING_COLUMNS:
        if col not in df_final.columns:
            df_final[col] = 0
    df_final = df_final[TRAINING_COLUMNS]

    return df_final, encoder

