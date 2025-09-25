import cv2
import numpy as np
import os
import sys
import tensorflow as tf

from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test,  y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """
    images = []
    labels = []

    for category in range(NUM_CATEGORIES):
        # Si no existe subdirectorio continuar al siguiente
        category_dir = os.path.join(data_dir, str(category))
        if not os.path.isdir(category_dir):
            continue
        # Recorrer todos los archivos dentro del subdirectorio
        for filename in os.listdir(category_dir):
            filepath = os.path.join(category_dir, filename)
            if not os.path.isfile(filepath):
                continue
            # Leer cada archivo como imagen a color, y si no existe imagen a color saltar al siguiente archivo
            img = cv2.imread(filepath, cv2.IMREAD_COLOR)
            if img is None:
                continue
            # Redimensionar imagen
            img = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT), interpolation=cv2.INTER_AREA)
            # Si está en escala de grises pasar a color
            if img.ndim == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            # Añadir imagenes al array
            images.append(img)
            labels.append(category)
        
    return (images, labels)

def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """

    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(IMG_WIDTH, IMG_HEIGHT, 3)),    # 30x30 RGB images
        tf.keras.layers.Rescaling(1./255), # Normalizar valores que llegan entre 0-255 (enteros) y salen como 0-1 (flotantes). En primera capa queda ya integrada y optimiza coste operacional

        tf.keras.layers.Conv2D(32, (3,3), padding="same", activation="relu"), # Capturan bordes y texturas simples
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling2D((2,2)), # Escoge el máximo valor de la ventana 2x2

        tf.keras.layers.Conv2D(64, (3,3), padding="same", activation="relu"), # Capturan patrones compuestos como curvas y esquinas
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling2D((2,2)),

        tf.keras.layers.Conv2D(128, (3,3), padding="same", activation="relu"), # capturan rasgos específicos del signo
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling2D((2,2)),

        tf.keras.layers.Flatten(), # Sirve para aplanar. Pasa mapas 2D/3D de las convoluciones a vector 1D para pasarlo a capas densas. Alternativa: GlobalAveragePooling2D
        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.Dropout(0.5),

        tf.keras.layers.Dense(NUM_CATEGORIES, activation="softmax")

        # Entrada: 30x30x3
        # Bloque 1: Conv(32) -> 30x30x32 -> Pool -> 15x15x32
        # Bloque 2: Conv(64) -> 15x15x64 -> Pool -> 7x7x64
        # Bloque 3: Conv(128) -> 7x7x128 -> Pool -> 3x3x128
        # Flatten: 1152
        # A más filtros (64-128-256) más capacidad pero más riesgo de overfitting y más tiempo de entrenamiento
    ])
    
    model.compile(
        optimizer = "adam",
        loss = "categorical_crossentropy",
        metrics = ["accuracy"]
    )
    return model


if __name__ == "__main__":
    main()
