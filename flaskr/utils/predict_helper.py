import tensorflow as tf
import numpy as np

class Predicter:
    __instance = None

    @staticmethod
    def get_instance():
        if Predicter.__instance is None:
            Predicter()
        return Predicter.__instance
    
    def __init__(self):
        if Predicter.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Predicter.__instance = self
    
    def loadModel(self, path):
        data_augmentation = tf.keras.Sequential(
            [
                tf.keras.layers.RandomFlip("horizontal", input_shape=(224, 224, 3)),
                tf.keras.layers.RandomRotation(0.2),
                tf.keras.layers.RandomZoom(0.2),
                tf.keras.layers.RandomBrightness(factor=0.2),
            ]
        )
        base_model = tf.keras.applications.ResNet152V2(
            weights=None, include_top=False, input_shape=(224, 224, 3)
        )
        base_model.trainable = False

        inputs = tf.keras.layers.Input(shape=(224, 224, 3))
        x = data_augmentation(inputs)
        x = tf.keras.applications.resnet_v2.preprocess_input(x)
        x = base_model(x, training=False)
        x = tf.keras.layers.GlobalAveragePooling2D()(x)
        x = tf.keras.layers.Dense(512, activation="relu")(x)
        x = tf.keras.layers.Dropout(0.3)(x)
        output = tf.keras.layers.Dense(46 , name="ouput")(x)
        model = tf.keras.models.Model(inputs=inputs, outputs=output)

        base_model.trainable = True

        base_learning_rate = 0.0001
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=base_learning_rate/2.0),
                    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                    metrics="accuracy")

        model.load_weights(path)
        
        self.model = model
        
    def __decode_img(self, img):
        img = tf.io.decode_jpeg(img, channels=3)
        return tf.image.resize(img, [224, 224])

    def predict(self, image_url):
        # img = tf.io.read_file('/content/1699602827587.jpg')
        img = tf.io.read_file(tf.keras.utils.get_file(origin=image_url))
        img = self.__decode_img(img)
        img_batch = tf.expand_dims(img, 0)

        prediction = self.model.predict(img_batch)[0]
        score = tf.nn.softmax(prediction)
        
        top_indices = np.argsort(score)[-5:][::-1]
        
        print(top_indices)
        
        return [float(i + score[i]) for i in top_indices]