import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
from sklearn.utils.class_weight import compute_class_weight
import joblib
import tensorflow as tf
from tensorflow.keras import layers, models, callbacks

EXCEL_PATH = "heart_disease_health_indicators_BRFSS2015.xlsx"
TRAIN_SHEET = None
VAL_SHEET = None
RANDOM_STATE = 42
OUT_DIR = "./outputs"
os.makedirs(OUT_DIR, exist_ok=True)

xls = pd.ExcelFile(EXCEL_PATH, engine='openpyxl')
print("Sheets found:", xls.sheet_names)

if TRAIN_SHEET is None:
    for s in xls.sheet_names:
        cols = pd.read_excel(EXCEL_PATH, sheet_name=s, nrows=0, engine='openpyxl').columns.tolist()
        if 'HeartDisease' in cols:
            TRAIN_SHEET = s
            break
    if TRAIN_SHEET is None:
        TRAIN_SHEET = xls.sheet_names[0]
if VAL_SHEET is None:
    for s in xls.sheet_names:
        if 'validation' in s.lower() or s.lower().startswith('val'):
            VAL_SHEET = s
            break

print("Using TRAIN sheet:", TRAIN_SHEET)
print("Using VAL sheet:", VAL_SHEET)

train_df = pd.read_excel(EXCEL_PATH, sheet_name=TRAIN_SHEET, engine='openpyxl')
val_df = pd.read_excel(EXCEL_PATH, sheet_name=VAL_SHEET, engine='openpyxl') if VAL_SHEET else None

print(train_df.columns)

print("Train shape:", train_df.shape)
if val_df is not None:
    print("Validation shape:", val_df.shape)

TARGET = 'HeartDiseaseorAttack'
if TARGET not in train_df.columns:
    raise RuntimeError("Não encontrei a coluna 'HeartDisease' na(s) aba(s). Verifique o arquivo.")

train_df = train_df.dropna(subset=[TARGET]).copy()

feature_cols = [c for c in train_df.columns if c != TARGET]

known_numeric = {'BMI','PhysicalHealth','MentalHealth','SleepTime'}
numeric_cols = []
categorical_cols = []
for c in feature_cols:
    vals = set(train_df[c].dropna().unique())
    if c in known_numeric or pd.api.types.is_numeric_dtype(train_df[c]) or vals.issubset({0,1}):
        numeric_cols.append(c)
    else:
        categorical_cols.append(c)

print("Numeric cols:", numeric_cols)
print("Categorical cols:", categorical_cols)

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_cols)
    ],
    remainder='drop'
)

X = train_df[feature_cols].copy()
y = train_df[TARGET].astype(int).copy()

X_train, X_hold, y_train, y_hold = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y)

X_train_processed = preprocessor.fit_transform(X_train)
X_hold_processed  = preprocessor.transform(X_hold)

joblib.dump(preprocessor, os.path.join(OUT_DIR, "preprocessor.joblib"))
print("Saved preprocessor to", os.path.join(OUT_DIR, "preprocessor.joblib"))

classes = np.unique(y_train)
class_weights = compute_class_weight(class_weight='balanced', classes=classes, y=y_train)
class_weight_dict = {int(c): float(w) for c,w in zip(classes, class_weights)}
print("Class weights:", class_weight_dict)

input_dim = X_train_processed.shape[1]
def make_model(input_dim):
    model = models.Sequential([
        layers.Input(shape=(input_dim,)),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(32, activation='relu'),
        layers.Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy', tf.keras.metrics.AUC(name='auc')])
    return model

model = make_model(input_dim)
model.summary()

es = callbacks.EarlyStopping(monitor='val_auc', patience=8, mode='max', restore_best_weights=True, verbose=1)
mc = callbacks.ModelCheckpoint(os.path.join(OUT_DIR, 'best_model.h5'), monitor='val_auc', mode='max', save_best_only=True, verbose=1)

history = model.fit(
    X_train_processed, y_train.values,
    validation_data=(X_hold_processed, y_hold.values),
    epochs=200,
    batch_size=256,
    class_weight=class_weight_dict,
    callbacks=[es, mc],
    verbose=2
)

model.save(os.path.join(OUT_DIR, "final_model.h5"))
print("Saved model to", os.path.join(OUT_DIR, "final_model.h5"))

joblib.dump(history.history, os.path.join(OUT_DIR, "history.joblib"))

y_pred_prob = model.predict(X_hold_processed).ravel()
y_pred = (y_pred_prob >= 0.5).astype(int)

print("Classification report (hold-out):")
print(classification_report(y_hold, y_pred))
print("ROC AUC (hold-out):", roc_auc_score(y_hold, y_pred_prob))
print("Confusion matrix:\n", confusion_matrix(y_hold, y_pred))

if val_df is not None:
    val_X = val_df.copy()
    if TARGET in val_X.columns:
        val_X = val_X.drop(columns=[TARGET])
    for c in feature_cols:
        if c not in val_X.columns:
            val_X[c] = np.nan
    val_X = val_X[feature_cols]
    val_processed = preprocessor.transform(val_X)
    val_probs = model.predict(val_processed).ravel()
    val_preds = (val_probs >= 0.5).astype(int)
    out = val_df.copy()
    out['Pred_HeartDisease'] = val_preds
    out['Pred_Prob_HeartDisease'] = val_probs
    out_path = os.path.join(OUT_DIR, "predictions_nn.csv")
    out.to_csv(out_path, index=False)
    print("Saved predictions to", out_path)
else:
    print("Nenhuma aba de validação detectada; nenhuma predição gerada.")

print("Arquivos gerados em:", OUT_DIR)