import tensorflow as tf
import numpy as np
import pandas as pd
import os

DATA_DIR = "ml-1m"
movies = pd.read_csv(os.path.join(DATA_DIR, "movies_processed.csv"))
ratings = pd.read_csv(os.path.join(DATA_DIR, "u.data"), sep="\t", header=None)
ratings.columns = ["UserID", "MovieID", "Rating", "Timestamp"]

ratings = ratings.merge(movies[["MovieID", "List Index"]], on="MovieID")

user_groups = ratings.groupby("UserID")

trX = []
for uid, group in user_groups:
    temp = np.zeros(len(movies))
    for _, row in group.iterrows():
        temp[int(row["List Index"])] = row["Rating"] / 5
    trX.append(temp)

trX = np.array(trX)

visible_units = len(movies)
hidden_units = 80

W = tf.Variable(tf.random.normal([visible_units, hidden_units], 0.01))
vb = tf.Variable(tf.zeros([visible_units]))
hb = tf.Variable(tf.zeros([hidden_units]))

optimizer = tf.keras.optimizers.Adam(0.01)

def rbm_step(v0):
    with tf.GradientTape() as tape:
        h_prob = tf.nn.sigmoid(tf.matmul(v0, W) + hb)
        h_sample = tf.nn.relu(tf.sign(h_prob - tf.random.uniform(tf.shape(h_prob))))

        v_prob = tf.nn.sigmoid(tf.matmul(h_sample, tf.transpose(W)) + vb)
        v_sample = tf.nn.relu(tf.sign(v_prob - tf.random.uniform(tf.shape(v_prob))))

        h1_prob = tf.nn.sigmoid(tf.matmul(v_sample, W) + hb)

        CD = tf.matmul(tf.transpose(v0), h_prob) - tf.matmul(tf.transpose(v_sample), h1_prob)
        loss = tf.reduce_mean(tf.square(v0 - v_prob))

    grads = tape.gradient(loss, [W, vb, hb])
    optimizer.apply_gradients(zip(grads, [W, vb, hb]))
    return loss

for epoch in range(15):
    loss = rbm_step(trX.astype(np.float32))
    print(f"Epoch {epoch+1} - Loss: {loss.numpy():.4f}")

model = {
    "W": W.numpy(),
    "vb": vb.numpy(),
    "hb": hb.numpy()
}

np.save("rbm_model.npy", model)
print("Model saved as rbm_model.npy")