from pokersim import *
import tensorflow as tf
from tensorflow import keras
import io
import sys
import numpy as np

text_trap = io.StringIO()
sys.stdout = text_trap
inputlist = []
labellist = []
for _ in range(500):
    G = Game(4, 480, 50)
    gameround(G, reset=False)
    inputlist.append([(x.rank - 2)/12 for x in G.players[0].cards] + [(x.rank - 2)/12 for x in G.board] + [G.players[0].currentbet / 480])
    labellist.append(G.players[0].chips / 1920)
sys.stdout = sys.__stdout__
print(inputlist[0])
train_inputs = np.array(inputlist)
train_labels = np.array(labellist)

# Build the model
model = keras.Sequential([
    keras.layers.Dense(64, activation=tf.nn.relu),
    keras.layers.Dense(128, activation=tf.nn.relu),
    keras.layers.Dense(1)
])

# *Loss function* —This measures how accurate the model is during training. We want to minimize this function to "steer" the model in the right direction.
# *Optimizer* —This is how the model is updated based on the data it sees and its loss function.
# *Metrics* —Used to monitor the training and testing steps. The following example uses *accuracy*, the fraction of the images that are correctly classified.

model.compile(optimizer='adam', 
              loss='mse')

# Train the model
model.fit(train_inputs, train_labels, epochs=4)

# As the model trains, the loss and accuracy metrics are displayed. This model reaches an accuracy of about 0.88 (or 88%) on the training data.
# Evaluate accuracy

# Next, compare how the model performs on the test dataset:
text_trap = io.StringIO()
sys.stdout = text_trap
testinputlist = []
testlabellist = []
for _ in range(1000):
    G = Game(4, 480, 50)
    gameround(G, reset=False)
    testinputlist.append([(x.rank - 2)/12 for x in G.players[0].cards] + [(x.rank - 2)/12 for x in G.board] + [G.players[0].currentbet / 480])
    testlabellist.append(G.players[0].chips / 1920)
sys.stdout = sys.__stdout__

test_inputs = np.array(testinputlist)
test_labels = np.array(testlabellist)

test_loss = model.evaluate(test_inputs, test_labels)
print('Test loss:', test_loss)

# Make predictions
# predictions = model.predict((np.array([[14, 14, 2, 3, 5, 6, 9], [2, 3, 5, 6, 9, 14, 14]]) - 2 )/ 12)
# print(predictions)