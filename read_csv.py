# File: read_csv.py
# Aim: Demo of reading .mat file into 3-D array
# %%
import matplotlib.pyplot as plt
import numpy as np
import os
import plotly.graph_objs as go
import plotly.express as px
import scipy.io as sio
from tqdm.auto import tqdm

fname = os.path.join('parsed_raw_data',
                     's19880813-0001-00360-000000.nii.mat')
# %%
loaded = sio.loadmat(fname)
array = loaded.get('mat')
array.shape
# %%
plt.imshow(array[200])
# %%
plt.imshow(array[:, 200, :])
# %%
plt.imshow(array[:, :, 200])

# %%
fig = px.imshow(array[200], color_continuous_scale='gray')
fig.show()

# %%
