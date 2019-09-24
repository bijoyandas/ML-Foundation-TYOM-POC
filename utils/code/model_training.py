import pandas as pd
import logging
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.externals import joblib

logger=logging.getLogger(__name__)

def get_data():
    df = pd.read_csv("SocialMediaAdv.csv")
    return df

def train_model():
    df = get_data()
    X = df.iloc[:, 2:4].values
    y = df.iloc[:, 4].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.25, random_state = 0)
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)
    classifier = LogisticRegression(random_state = 0, solver = 'lbfgs')
    classifier.fit(X_train, y_train)
    accuracies = cross_val_score(estimator = classifier, X = X_train, y = y_train, cv = 10)
    mean_accuracy = accuracies.mean()*100
    logger.error("Model Accuracy is {:0.2f}".format(mean_accuracy))
    return classifier, sc

logger.error("Model Training Execution Started")
classifier, sc = train_model()

model_path = "model.pkl"
scaler_path = "scaler.pkl"

joblib.dump(classifier, model_path, compress = 1)
joblib.dump(sc, scaler_path, compress = 1)
