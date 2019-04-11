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
    inputlist.append([x.rank for x in G.players[0].cards] + [x.rank for x in G.board])
    labellist.append(int(G.players[0].chips >= 480))
sys.stdout = sys.__stdout__

train_inputs = np.array(inputlist)
train_labels = np.array(labellist)
class_names = ['Lose', 'Win']

#We scale these values to a range of 0 to 1 before feeding to the neural network model. For this, we divide the values by 255. It's important that the *training set* and the *testing set* are preprocessed in the same way:"""
train_inputs = (train_inputs - 2) / 12

# Build the model
model = keras.Sequential([
    keras.layers.Dense(64, activation=tf.nn.relu),
    keras.layers.Dense(128, activation=tf.nn.relu),
    keras.layers.Dense(2, activation=tf.nn.softmax)
])

# *Loss function* —This measures how accurate the model is during training. We want to minimize this function to "steer" the model in the right direction.
# *Optimizer* —This is how the model is updated based on the data it sees and its loss function.
# *Metrics* —Used to monitor the training and testing steps. The following example uses *accuracy*, the fraction of the images that are correctly classified.
model.compile(optimizer='adam', 
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

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
    testinputlist.append([x.rank for x in G.players[0].cards] + [x.rank for x in G.board])
    testlabellist.append(int(G.players[0].chips >= 480))
sys.stdout = sys.__stdout__

test_inputs = np.array(testinputlist)
test_labels = np.array(testlabellist)
test_inputs = (test_inputs - 2) / 12

test_loss, test_acc = model.evaluate(test_inputs, test_labels)
print('Test accuracy:', test_acc)

# Make predictions
predictions = model.predict((np.array([[14, 14, 2, 3, 5, 6, 9], [2, 3, 5, 6, 9, 14, 14]]) - 2 )/ 12)
print(predictions)