import numpy as np
import tensorflow as tf
# import math
import pandas as pd
# from sklearn import model_selection
# import glob
import os
# import datetime
import logging
import json

tf.get_logger().setLevel(logging.ERROR)
import warnings
warnings.filterwarnings("ignore")


config = {
    'input_size': (160, 160, 3),
    'n_classes': 1049,
}

def read_image(image_path):
    image = tf.io.read_file(image_path)
    return tf.image.decode_jpeg(image, channels=3)

def preprocess_input(image, target_size, augment=False):
    
    image = tf.image.resize(
        image, target_size, method='bilinear')

    image = tf.cast(image, tf.uint8)
    if augment:
        image = _spatial_transform(image)
        image = _pixel_transform(image)
    image = tf.cast(image, tf.float32)
    image /= 255.
    return image

def pred_image(image_path):
    interpreter = tf.lite.Interpreter(model_path="./trained_models/mobile_98%_converted.tflite")
    interpreter.allocate_tensors()
    # Get input and output tensors.
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # input image
    image = read_image(image_path)
    image = preprocess_input(image, config['input_size'][:2])
    # image = np.reshape(image, (1, 135,240, 3))
    image = np.reshape(image, (1,160, 160, 3))
    
    print('start pred')
    interpreter.set_tensor(input_details[0]['index'], image)
    interpreter.invoke()
    pred = interpreter.get_tensor(output_details[0]['index'])

    probs_argsort = tf.argsort(pred, direction='DESCENDING')
    probs = pred[0][probs_argsort][:1]

    category = pd.read_csv('category.csv')
    probs = []
    classes = []
    for i in range(5):
        probs.append(round(pred[0][[probs_argsort[0][i]]]))
        idx = probs_argsort[0][i]
        classes.append(category['landmark_name'][category['landmark_id'] == int(idx)].values[0])        
        
    return classes, probs
    