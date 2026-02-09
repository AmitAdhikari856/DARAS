import pandas as pd
from sklearn.preprocessing import OrdinalEncoder


def preprocess_assessment(assessment, encoder=None, fit=False):
    """
    Convert DigitalAddictionAssessment into ML-ready numeric dataframe.
    
    Args:
        assessment : model instance
        encoder    : pretrained sklearn encoder
        fit        : True when training, False during prediction
        
    Returns:
        df, encoder
    """

    # ----------------------------
    # 1️⃣ Range → numeric midpoints
    # ----------------------------
    screen_map = {"<2h": 2, "2–3h": 3.5, "3–4h": 3.5, "4–6h": 5, ">6h": 6}
    night_map = {"Never": 0, "<30m": 0.25, "30–60m": 0.75, "1–2h": 1.5, ">2h": 3}
    notif_map = {"<5 times": 4, "5–10 times": 7, "11–20 times": 15, ">20 times": 21}
    social_map = {"<1h": 0.5, "1–2h": 1.5, "2–3h": 2.5, "3–4h": 3.5, ">4h": 5}
    gaming_map = {"None": 0, "<30m": 0.25, "30–60m": 0.75, "1–2h": 1.5, ">2h": 3}

    # ----------------------------
    # 2️⃣ Raw Features
    # ----------------------------
    X_raw = {
        "age": assessment.age,
        "gender": assessment.gender,
        "primary_device": assessment.primary_device,
        "own_smartphone": int(assessment.own_smartphone),
        "mobile_data_plan": assessment.mobile_data,

        "screen_time_weekdays": screen_map.get(assessment.screen_weekdays, 0),
        "screen_time_weekends": screen_map.get(assessment.screen_weekends, 0),
        "night_phone_use": night_map.get(assessment.night_phone_use, 0),
        "notif_per_hour": notif_map.get(assessment.notif_per_hour, 0),
        "social_media_time": social_map.get(assessment.social_time, 0),
        "gaming_time": gaming_map.get(assessment.gaming_time, 0),

        "da1_time_loss": assessment.da1,
        "da2_restless": assessment.da2,
        "da3_failed_cut": assessment.da3,
        "da4_skip_tasks": assessment.da4,
        "da5_negative_emotions": assessment.da5,
        "da6_morning_check": assessment.da6,
        "da7_class_check": assessment.da7,
        "da8_family_comment": assessment.da8,
    }

    # ----------------------------
    # 3️⃣ DA Summary Features
    # ----------------------------
    das_sum = sum([
        assessment.da1, assessment.da2, assessment.da3, assessment.da4,
        assessment.da5, assessment.da6, assessment.da7, assessment.da8
    ])

    X_raw["DAS_sum"] = das_sum
    X_raw["DAS_normalized"] = das_sum / 40 * 100
    X_raw["DAS_weighted"] = das_sum / 8
    X_raw["DAS_weighted_normalized"] = (das_sum / 8) / 5 * 100

    # ----------------------------
    # 4️⃣ Platform Encoding
    # ----------------------------
    platforms = [
        'youtube','facebook','tiktok','instagram','linkedin',
        'whatsapp','x','snapchat','livestreaming','gaming'
    ]

    used = [p.lower().replace(" ", "") for p in (assessment.platforms or [])]

    for p in platforms:
        X_raw[f"use_{p}"] = int(p in used)

    df = pd.DataFrame([X_raw])

    # ----------------------------
    # 5️⃣ Sklearn Categorical Encoding
    # ----------------------------
    cat_cols = ["gender", "primary_device", "mobile_data_plan"]

    if fit or encoder is None:
        encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
        df[cat_cols] = encoder.fit_transform(df[cat_cols])
    else:
        df[cat_cols] = encoder.transform(df[cat_cols])

    # ----------------------------
    # 6️⃣ Label Mapping
    # ----------------------------
    label_map = {
        "Not at Risk": 0,
        "Mild": 1,
        "Moderate": 2,
        "Severe": 3
    }

    df["y"] = label_map.get(assessment.self_rated_da, -1)

    return df, encoder
