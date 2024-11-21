"""
This Module Trains a Rock, Paper, Scissors Machine Learning Model
"""

# pylint: disable=E1101
# pylint: disable=import-error
# pylint: disable=no-member
# pylint: disable=no-name-in-module

import os
import tensorflow as tf
import tensorflow_datasets as tfds
from tensorflow.keras.models import Sequential  # pylint: disable=no-member
from tensorflow.keras.layers import Dense, Dropout, Flatten # pylint: disable=no-member
from tensorflow.keras.layers import Conv2D, MaxPooling2D, AveragePooling2D # pylint: disable=no-member
from tensorflow.keras.callbacks import TensorBoard # pylint: disable=no-member

# Set hyper-parameters
BATCH_SIZE = 32
NUM_CLASSES = 3
EPOCHS = 3


# Function to load and preprocess the dataset
def load_data():
    """
    Loads and preprocesses the rock_paper_scissors dataset.

    Returns:
        ds_train: Preprocessed training dataset
        ds_test: Preprocessed test dataset
        info: Dataset metadata
    """

    def preprocess_image(image, label):
        # Convert [0, 255] range integers to [0, 1] range floats
        image = tf.image.convert_image_dtype(image, tf.float32)
        return image, label

    # Load the dataset and split into train and test sets
    ds_train, info = tfds.load(
        "rock_paper_scissors", with_info=True, split="train", as_supervised=True
    )
    ds_test = tfds.load("rock_paper_scissors", split="test", as_supervised=True)

    # Repeat, shuffle, preprocess, and batch the datasets
    ds_train = ds_train.repeat().shuffle(1024).map(preprocess_image).batch(BATCH_SIZE)
    ds_test = ds_test.repeat().shuffle(1024).map(preprocess_image).batch(BATCH_SIZE)
    return ds_train, ds_test, info


# Function to create the model
def create_model():
    """
    Creates and compiles the CNN model.

    Returns:
        model: Compiled CNN model
    """
    model = Sequential()
    model.add(AveragePooling2D(6, 3, input_shape=(300, 300, 3)))
    model.add(Conv2D(64, 3, activation="relu"))
    model.add(Conv2D(32, 3, activation="relu"))
    model.add(MaxPooling2D(2, 2))
    model.add(Dropout(0.5))
    model.add(Flatten())
    model.add(Dense(128, activation="relu"))
    model.add(Dense(NUM_CLASSES, activation="softmax"))

    # Print the summary of the model architecture
    model.summary()

    # Compile the model
    model.compile(
        loss="sparse_categorical_crossentropy", optimizer="adam", metrics=["accuracy"]
    )
    return model


# Load data
train_dataset, test_dataset, dataset_info = load_data()

# Create the model
cnn_model = create_model()

# Define callbacks for fitting the model
logdir = os.path.join("machine-learning-client/model/logs", "rps-model")
tensorboard = TensorBoard(log_dir=logdir)

# Train the model
cnn_model.fit(
    train_dataset,
    epochs=EPOCHS,
    validation_data=test_dataset,
    verbose=1,
    steps_per_epoch=dataset_info.splits["train"].num_examples // BATCH_SIZE,
    validation_steps=dataset_info.splits["test"].num_examples // BATCH_SIZE,
    callbacks=[tensorboard],
)

# Evaluate the model
rock_paper_scissors_test = tfds.load(
    name="rock_paper_scissors", split="test", batch_size=-1
)
rock_paper_scissors_test = tfds.as_numpy(rock_paper_scissors_test)

x_test, y_test = rock_paper_scissors_test["image"], rock_paper_scissors_test["label"]

cnn_model.evaluate(x_test, y_test)

# Save the model
cnn_model.save(
    "machine-learning-client/model/rps_model.h5",
    include_optimizer=False,
    save_format="h5",
)
