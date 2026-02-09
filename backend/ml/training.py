# import os
# import django
# import joblib
# import pandas as pd

# # ---------------------------------
# # Setup Django Environment
# # ---------------------------------
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")  
# django.setup()

# from assessment.models import DigitalAddictionAssessment
# from assessment.ml.preprocess import preprocess_assessment

# from sklearn.model_selection import train_test_split
# from sklearn.compose import ColumnTransformer
# from sklearn.pipeline import Pipeline

# from sklearn.preprocessing import OneHotEncoder, StandardScaler

# from sklearn.linear_model import LogisticRegression
# from sklearn.ensemble import RandomForestClassifier

# from xgboost import XGBClassifier

# from sklearn.metrics import accuracy_score, classification_report


# # ---------------------------------
# # 1️⃣ Load Data From DB
# # ---------------------------------
# assessments = DigitalAddictionAssessment.objects.all()

# if assessments.count() < 50:
#     raise Exception("⚠️ Need at least 50 records to train a reliable ML model.")


# rows = []
# for a in assessments:
#     df = preprocess_assessment(a)
#     rows.append(df)

# dataset = pd.concat(rows, ignore_index=True)

# print("\nDataset Shape:", dataset.shape)


# # ---------------------------------
# # 2️⃣ Split Features / Label
# # ---------------------------------
# X = dataset.drop(columns=["y"])
# y = dataset["y"]


# # ---------------------------------
# # 3️⃣ Detect Column Types Automatically
# # ---------------------------------
# categorical_features = [
#     "gender",
#     "primary_device",
#     "mobile_data_plan"
# ]

# numeric_features = [col for col in X.columns if col not in categorical_features]


# # ---------------------------------
# # 4️⃣ Preprocessing Pipelines
# # ---------------------------------
# numeric_transformer = Pipeline(
#     steps=[("scaler", StandardScaler())]
# )

# categorical_transformer = Pipeline(
#     steps=[("onehot", OneHotEncoder(handle_unknown="ignore"))]
# )

# preprocessor = ColumnTransformer(
#     transformers=[
#         ("num", numeric_transformer, numeric_features),
#         ("cat", categorical_transformer, categorical_features),
#     ]
# )


# # ---------------------------------
# # 5️⃣ Models
# # ---------------------------------
# models = {
#     "Logistic Regression": LogisticRegression(max_iter=2000),
#     "Random Forest": RandomForestClassifier(
#         n_estimators=300,
#         max_depth=12,
#         random_state=42
#     ),
#     "XGBoost": XGBClassifier(
#         n_estimators=300,
#         max_depth=8,
#         learning_rate=0.05,
#         subsample=0.9,
#         colsample_bytree=0.9,
#         eval_metric="mlogloss",
#         random_state=42
#     )
# }


# # ---------------------------------
# # 6️⃣ Train/Test Split
# # ---------------------------------
# X_train, X_test, y_train, y_test = train_test_split(
#     X, y,
#     test_size=0.2,
#     random_state=42,
#     stratify=y
# )


# best_model = None
# best_score = 0
# best_name = ""


# # ---------------------------------
# # 7️⃣ Train + Evaluate
# # ---------------------------------
# for name, model in models.items():

#     pipeline = Pipeline(
#         steps=[
#             ("preprocessor", preprocessor),
#             ("classifier", model)
#         ]
#     )

#     pipeline.fit(X_train, y_train)

#     preds = pipeline.predict(X_test)
#     acc = accuracy_score(y_test, preds)

#     print(f"\n{name} Accuracy: {acc:.4f}")
#     print(classification_report(y_test, preds))

#     if acc > best_score:
#         best_score = acc
#         best_model = pipeline
#         best_name = name


# # ---------------------------------
# # 8️⃣ Save Best Pipeline
# # ---------------------------------
# save_path = os.path.join(
#     os.path.dirname(__file__),
#     "digital_addiction_pipeline.pkl"
# )

# joblib.dump(best_model, save_path)

# print("\n✅ BEST MODEL:", best_name)
# print("✅ Accuracy:", best_score)
# print("✅ Saved to:", save_path)
