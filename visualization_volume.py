# File: visualization_volume.py
# Aim: Visualize volume interactively

# Imports
import numpy as np
import os
import plotly
import plotly.graph_objs as go
import plotly.express as px
import scipy.io as sio

# Loading volume
fname = 's19880813-0001-00360-000000.nii.mat'
fpath = os.path.join('parsed_raw_data', fname)
loaded = sio.loadmat(fpath)
volume = loaded.get('mat', None)
# volume = volume[150:250, 150:250, 150:250]
dim = loaded.get('dim', None)[0]
dim = volume.shape
print(volume.shape, dim)

# Parse dim
r, c, nb_slices = dim


def get_slice(j):
    # Get j-th slice from the volume
    if j not in range(nb_slices):
        print('!!!!!!!! Getting non-exist slice.')
        return np.zeros((r, c))
    return volume[:, :, j]


fig = go.Figure(
    frames=[
        go.Frame(
            data=go.Surface(
                z=(nb_slices - 1 - k) * np.ones((r, c)),
                surfacecolor=np.flipud(volume[:, :, nb_slices - 1 - k]),
                # cmin=0, cmax=200
            ),
            # you need to name the frame for the animation to behave properly
            name=str(k)
        )
        for k in range(nb_slices)])

# Add data to be displayed before animation starts
fig.add_trace(
    go.Surface(
        z=(nb_slices - 1) * np.ones((r, c)),
        surfacecolor=np.flipud(volume[67]),
        colorscale='Gray',
        # cmin=0, cmax=200,
        colorbar=dict(thickness=20,
                      ticklen=4)
    )
)


def frame_args(duration):
    return {
        'frame': {'duration': duration},
        'mode': 'immediate',
        'fromcurrent': True,
        'transition': {'duration': duration, 'easing': 'linear'},
    }


sliders = [
    {
        'pad': {'b': 10, 't': 60},
        'len': 0.9,
        'x': 0.1,
        'y': 0,
        'steps': [
            {
                'args': [[f.name], frame_args(0)],
                'label': str(k),
                'method': 'animate',
            }
            for k, f in enumerate(fig.frames)
        ],
    }
]

# Layout
fig.update_layout(
    title='Slices in volumetric data',
    width=600,
    height=600,
    scene=dict(
        zaxis=dict(range=[-1, nb_slices], autorange=False),
        aspectratio=dict(x=1, y=1, z=1),
    ),
    updatemenus=[
        {
            'buttons': [
                {
                    'args': [None, frame_args(50)],
                    'label': '&#9654;',  # play symbol
                    'method': 'animate',
                },
                {
                    'args': [[None], frame_args(0)],
                    'label': '&#9724;',  # pause symbol
                    'method': 'animate',
                },
            ],
            'direction': 'left',
            'pad': {'r': 10,
                    't': 70},
            'type': 'buttons',
            'x': 0.1,
            'y': 0,
        }
    ],
    sliders=sliders
)

fig.show()
