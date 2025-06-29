# from tensorflow.keras.models import load_model
# from tensorflow.keras.layers import DepthwiseConv2D
# from PIL import Image, ImageOps
# import numpy as np

# # Disable scientific notation for clarity
# np.set_printoptions(suppress=True)



# # Сохраним оригинальный from_config
# original_from_config = DepthwiseConv2D.from_config

# # Переопределим from_config, чтобы убрать 'groups' из конфигурации

# def custom_from_config(cls, config):
#     if 'groups' in config:
#         config.pop('groups')
#     return original_from_config(cls, config)


# # def custom_from_config(config):
# #     if 'groups' in config:
# #         config.pop('groups')
# #     return original_from_config(config)

# DepthwiseConv2D.from_config = classmethod(custom_from_config)

# # # Теперь загружаем модель
# # model = load_model("keras_Model.h5", compile=False)


# class DepthwiseConv2DFixed(DepthwiseConv2D):
#     @classmethod
#     def from_config(cls, config):
#         config = dict(config)  # копируем конфиг, чтобы не менять исходный
#         if 'groups' in config:
#             config.pop('groups')
#         return super().from_config(config)

# # Теперь загрузим модель, указав, что DepthwiseConv2D надо заменять на DepthwiseConv2DFixed
# model = load_model("keras_Model.h5", compile=False, custom_objects={'DepthwiseConv2D': DepthwiseConv2DFixed})
# # Load the model
# # model = load_model("keras_Model.h5", compile=False)

# # Load the labels
# class_names = open("labels.txt", "r").readlines()

# # Create the array of the right shape to feed into the keras model
# # The 'length' or number of images you can put into the array is
# # determined by the first position in the shape tuple, in this case 1
# data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

# # Replace this with the path to your image
# image = Image.open("<IMAGE_PATH>").convert("RGB")

# # resizing the image to be at least 224x224 and then cropping from the center
# size = (224, 224)
# image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

# # turn the image into a numpy array
# image_array = np.asarray(image)

# # Normalize the image
# normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

# # Load the image into the array
# data[0] = normalized_image_array

# # Predicts the model
# prediction = model.predict(data)
# index = np.argmax(prediction)
# class_name = class_names[index]
# confidence_score = prediction[0][index]

# # Print prediction and confidence score
# print("Class:", class_name[2:], end="")
# print("Confidence Score:", confidence_score)




from keras.models import load_model
from tensorflow.keras.layers import DepthwiseConv2D
from PIL import Image, ImageOps
import numpy as np

np.set_printoptions(suppress=True)

class DepthwiseConv2DFixed(DepthwiseConv2D):
    @classmethod
    def from_config(cls, config):
        config = dict(config)
        if 'groups' in config:
            config.pop('groups')
        return super().from_config(config)





# Create the array of the right shape to feed into the keras model
# The 'length' or number of images you can put into the array is
# determined by the first position in the shape tuple, in this case 1


model = load_model("keras_Model.h5", compile=False, custom_objects={'DepthwiseConv2D': DepthwiseConv2DFixed})

class_names = open("labels.txt", "r").readlines()

data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

image = Image.open("your_image.jpg").convert("RGB")
size = (224, 224)
image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
image_array = np.asarray(image)
normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
data[0] = normalized_image_array

prediction = model.predict(data)
index = np.argmax(prediction)
class_name = class_names[index]
confidence_score = prediction[0][index]

print("Class:", class_name[2:], end="")
print("Confidence Score:", confidence_score)
