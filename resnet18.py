import tensorflow as tf
import numpy as np
import math
from tensorflow import keras
from tensorflow.keras.layers import Dense, Conv2D, BatchNormalization, Activation
from tensorflow.keras.layers import AveragePooling2D, GlobalAveragePooling2D, Input, Flatten
from tensorflow.keras.regularizers import l2
from tensorflow.keras import backend as K
from tensorflow.keras.models import Model
import os


def resnet_block(inputs, num_filters=16, kernel_size=3, strides=1, activation='relu', dilation_rate=1):
    x = Conv2D(num_filters,
               kernel_size=kernel_size,
               strides=strides,
               padding='same',
               dilation_rate=dilation_rate,
               kernel_initializer='he_normal',
               kernel_regularizer=l2(1e-4))(inputs)
    x = BatchNormalization()(x)
    if (activation):
        x = Activation('relu')(x)
    return x


def resnet_v1(input_shape, num_classes=10, use_downsampling=False):
    #input_shape should be (width,height,channel)
    inputs = Input(shape=input_shape)

    dilation_rate = 1
    strides = 1
    x = resnet_block(inputs, dilation_rate=dilation_rate, strides=strides)
    for i in range(6):
        a = resnet_block(inputs=x, dilation_rate=dilation_rate)
        b = resnet_block(inputs=a, activation=None, dilation_rate=dilation_rate)
        x = keras.layers.Add()([x, b])
        x = Activation('relu')(x)

    for i in range(6):
        if i == 0:
            if not use_downsampling:
                dilation_rate *= 2
            else:
                strides = 2
            a = resnet_block(inputs=x, num_filters=32, dilation_rate=dilation_rate, strides=strides)
        else:
            a = resnet_block(inputs=x, num_filters=32, dilation_rate=dilation_rate)
        b = resnet_block(inputs=a, activation=None, num_filters=32)
        if i == 0:
            if not use_downsampling:
                dilation_rate *= 2
            else:
                strides = 2
            x = Conv2D(32,
                       kernel_size=3,
                       strides=strides,
                       padding='same',
                       dilation_rate=dilation_rate,
                       kernel_initializer='he_normal',
                       kernel_regularizer=l2(1e-4))(x)
        x = keras.layers.Add()([x, b])
        x = Activation('relu')(x)

    for i in range(6):
        if i == 0:
            if not use_downsampling:
                dilation_rate *= 2
            else:
                strides = 2
            a = resnet_block(inputs=x, strides=strides, dilation_rate=dilation_rate, num_filters=64)
        else:
            a = resnet_block(inputs=x, num_filters=64, dilation_rate=dilation_rate)

        b = resnet_block(inputs=a, activation=None, num_filters=64, dilation_rate=dilation_rate)
        if i == 0:
            if not use_downsampling:
                dilation_rate *= 2
            else:
                strides = 2
            x = Conv2D(64,
                       kernel_size=3,
                       strides=strides,
                       padding='same',
                       dilation_rate=dilation_rate,
                       kernel_initializer='he_normal',
                       kernel_regularizer=l2(1e-4))(x)
        x = keras.layers.Add()([x, b])
        x = Activation('relu')(x)

    x = GlobalAveragePooling2D()(x)
    y = Flatten()(x)
    outputs = Dense(num_classes, activation='softmax', kernel_initializer='he_normal')(y)

    model = Model(inputs=inputs, outputs=outputs)
    return model