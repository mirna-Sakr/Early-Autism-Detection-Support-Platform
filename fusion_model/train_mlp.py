import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, roc_auc_score

# load dataset
data = pd.read_csv("features.csv")

X = data.drop("label", axis=1)
y = data["label"]

# حفظ ترتيب الأعمدة
feature_columns = X.columns.tolist()
joblib.dump(feature_columns, "saved_model/feature_columns.pkl")

# cross validation
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("mlp", MLPClassifier(
        hidden_layer_sizes=(64, 32),
        max_iter=500,
        early_stopping=True,
        random_state=42
    ))
])

scores = cross_val_score(pipeline, X, y, cv=5)

print("Cross Validation Accuracy:", scores.mean())

# train test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

model = MLPClassifier(
    hidden_layer_sizes=(64, 32),
    max_iter=500,
    early_stopping=True,
    random_state=42
)

model.fit(X_train, y_train)

pred = model.predict(X_test)
prob = model.predict_proba(X_test)[:, 1]

print(classification_report(y_test, pred))
print("ROC AUC:", roc_auc_score(y_test, prob))

# save model
joblib.dump(model, "saved_model/mlp_model.pkl")
joblib.dump(scaler, "saved_model/scaler.pkl")

print("Model saved.")