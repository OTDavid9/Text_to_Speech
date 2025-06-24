# import time
# import numpy as np
# import jax
# import jax.numpy as jnp
# from jax import jit

# # Regular Python function
# def simple_func(x):
#     return np.tanh(x) * 2 + x ** 2

# # JAX JIT-compiled version of the same function
# @jit
# def jax_simple_func(x):
#     return jnp.tanh(x) * 2 + x ** 2

# # Test data
# x_np = np.random.randn(1000000)  # 1 million elements
# x_jax = jnp.array(x_np)  # Convert to JAX array

# # Time regular function
# start = time.time()
# result_np = simple_func(x_np)
# print(result_np)
# numpy_time = time.time() - start

# # # Time JAX function (first run includes compilation)
# # start = time.time()
# # result_jax = jax_simple_func(x_jax).block_until_ready()  # Force completion
# # jax_first_time = time.time() - start

# # Time JAX function (subsequent runs are faster)
# start = time.time()
# result_jax = jax_simple_func(x_jax).block_until_ready()
# print(result_jax)
# jax_second_time = time.time() - start

# print(f"NumPy time: {numpy_time:.5f} sec")
# # print(f"JAX first run (with compilation): {jax_first_time:.5f} sec")
# print(f"JAX subsequent runs: {jax_second_time:.5f} sec")
# print(f"It is {numpy_time/(jax_second_time)} times faster")

import keras_core as keras
from keras_core import layers
import numpy as np

# Set Keras backend to JAX
# keras.backend.set_backend("jax")

# Generate some dummy data
num_samples = 1000
num_features = 20

x_train = np.random.randn(num_samples, num_features)
y_train = np.random.randint(0, 2, size=(num_samples, 1))

# Define a simple Sequential model
model = keras.Sequential([
    layers.Dense(64, activation='relu', input_shape=(num_features,)),
    layers.Dense(64, activation='relu'),
    layers.Dense(1, activation='sigmoid')
])

from sklearn.model_selection import train_test_split

# Simulate some non-random labels (for demo purpose)
y_train = (x_train.sum(axis=1) > 0).astype(int).reshape(-1, 1)

# Train/test split
x_train_split, x_test_split, y_train_split, y_test_split = train_test_split(x_train, y_train, test_size=0.2)

model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy'])


# Model training
model.fit(x_train_split, y_train_split, epochs=10, batch_size=32, validation_data=(x_test_split, y_test_split))

# Evaluate on test set
test_loss, test_accuracy = model.evaluate(x_test_split, y_test_split)
print(f"Test Accuracy: {test_accuracy}")
