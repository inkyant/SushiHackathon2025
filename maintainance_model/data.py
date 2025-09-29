import pandas as pd

df = pd.read_csv("engine_data.csv")

df.info()
print(df.describe())

X = df.iloc[:, 0:6]
y = df["Engine Condition"]

print("\n\nStarting Logistic Reg test\n")
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LogisticRegression(solver='liblinear')
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

print(f"Accuracy: {accuracy_score(y_test, y_pred)}")


print("\n\nChecking PCA\n")
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import numpy as np

# Scale the data (important for PCA)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df)

pca = PCA(n_components=6)

# Fit PCA to the scaled data and transform it
X_pca = pca.fit_transform(X_scaled)

print("Original data shape:", X.shape)
print("Transformed data shape:", X_pca.shape)
print("Explained variance ratio:", pca.explained_variance_ratio_)
print("Explained variance ratio sum:", sum(pca.explained_variance_ratio_))


print("\n\nChecking correlation matrix")
import seaborn as sns
import matplotlib.pyplot as plt

# Calculate the correlation matrix
correlation_matrix = df.corr()
print("Correlation Matrix:\n", correlation_matrix)

# Visualize the correlation matrix using a heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlation Matrix of Independent Variables')
plt.savefig("fig.png")


print("\n\n Testing KNN algorithm\n")

from sklearn.neighbors import KNeighborsClassifier

# Scale features (important for KNN)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Create and train the KNN classifier
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train_scaled, y_train)

# Make predictions
y_pred = knn.predict(X_test_scaled)

# Evaluate
accuracy = knn.score(X_test_scaled, y_test)
print(f"Accuracy: {accuracy}")


print("\n\n Testing NB algorithm\n")
from sklearn.naive_bayes import GaussianNB
model = GaussianNB()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Gaussian Naive Bayes Accuracy: {accuracy}")