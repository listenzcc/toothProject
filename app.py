# File: visualization_volume.py
# Aim: Visualize volume interactively

# Imports

import dash
import dash_html_components as html
import dash_core_components as dcc
import numpy as np
import os
import plotly
import plotly.graph_objs as go
import plotly.express as px
import scipy.io as sio

from dash.dependencies import Input, Output

# Loading volume
fname = 's19880813-0001-00360-000000.nii.mat'
fname = 'sanon-0001-00486-000000.nii.mat'
fname = 'sd516427-0001-00486-000000.nii.mat'
fpath = os.path.join('parsed_raw_data', fname)
loaded = sio.loadmat(fpath)
volume = loaded.get('mat', None)
# volume = volume[150:250, 150:250, 150:250]
# dim = loaded.get('dim', None)[0]
# dim = volume.shape
# print(volume.shape, dim)
#
# cmax = np.max(volume)
# cmin = np.min(volume)
# xx = np.array(range(dim[0]))
# yy = np.array(range(dim[1]))
# zz = np.array(range(dim[2]))


class VolumeFig(object):
    def __init__(self, volume, downsampling=5):
        # Volume
        self.raw_volume = volume
        self.volume = volume[::downsampling, ::downsampling, ::downsampling]

    def create_fig(self):
        # Create figure
        fig = go.Figure(data=self.create_traces(),
                        layout=self.create_layout())
        self.fig = fig
        return fig

    def create_layout(self, width=800, height=800):
        # Create layout of the 3-D scene
        dim = self.volume.shape
        m = np.max(dim)
        layout = go.Layout(
            title='Slices in volumetric data',
            scene=dict(
                xaxis=dict(range=[-1, dim[0]], autorange=False),
                yaxis=dict(range=[-1, dim[1]], autorange=False),
                zaxis=dict(range=[-1, dim[2]], autorange=False),
                aspectratio=dict(x=dim[0] / m,
                                 y=dim[1] / m,
                                 z=dim[2] / m),
            ),
            width=width,
            height=height,
            clickmode='event+select'
        )
        self.layout = layout
        return layout

    def update_traces(self, r, c, s):
        # ------------------------------------
        z, y = np.meshgrid(self.zz, self.yy)
        x = z * 0 + r
        face = self.volume[r, :, :]
        self.fig['data'][0]['surfacecolor'] = face
        self.fig['data'][0]['x'] = x
        self.fig['data'][0]['y'] = y
        self.fig['data'][0]['z'] = z

        # ------------------------------------
        z, x = np.meshgrid(self.zz, self.xx)
        y = x * 0 + c
        face = self.volume[:, c, :]
        self.fig['data'][1]['surfacecolor'] = face
        self.fig['data'][1]['x'] = x
        self.fig['data'][1]['y'] = y
        self.fig['data'][1]['z'] = z

        # ------------------------------------
        y, x = np.meshgrid(self.yy, self.xx)
        z = y * 0 + s
        face = self.volume[:, :, s]
        self.fig['data'][2]['surfacecolor'] = face
        self.fig['data'][2]['x'] = x
        self.fig['data'][2]['y'] = y
        self.fig['data'][2]['z'] = z

        self.fig.update_layout(uirevision='constant')
        return self.fig

    def create_traces(self):
        # Create traces of the volume
        # Projection starts at (r, c, s)
        r, c, s = 0, 0, 0
        volume = self.volume
        dim = volume.shape

        xx = np.array(range(dim[0]))
        yy = np.array(range(dim[1]))
        zz = np.array(range(dim[2]))

        cmax = np.max(volume)
        cmin = np.min(volume)
        kwargs_trace = dict(
            colorscale='Gray',
            cmax=cmax,
            cmin=cmin,
            opacity=0.8,
        )

        # ------------------------------------
        z, y = np.meshgrid(zz, yy)
        x = z * 0 + r
        face = volume[r, :, :]
        tracex = go.Surface(
            x=x,
            y=y,
            z=z,
            surfacecolor=face,
            **kwargs_trace,
        )

        # ------------------------------------
        z, x = np.meshgrid(zz, xx)
        y = x * 0 + c
        face = volume[:, c, :]
        tracey = go.Surface(
            x=x,
            y=y,
            z=z,
            surfacecolor=face,
            **kwargs_trace,
        )

        # ------------------------------------
        y, x = np.meshgrid(yy, xx)
        z = y * 0 + s
        face = volume[:, :, s]
        tracez = go.Surface(
            x=x,
            y=y,
            z=z,
            surfacecolor=face,
            **kwargs_trace,
        )

        traces = [tracex,
                  tracey,
                  tracez]

        self.xx = xx
        self.yy = yy
        self.zz = zz
        self.traces = traces
        return traces


volume_fig = VolumeFig(volume)
fig = volume_fig.create_fig()


app = dash.Dash(__name__)

kwargs_slider = dict(
    min=0,
    value=0,
    step=1,
    updatemode='drag'
)
dim = volume_fig.volume.shape
slider1 = dcc.Slider(
    id='slider1',
    max=dim[0] - 1,
    **kwargs_slider,
)
slider2 = dcc.Slider(
    id='slider2',
    max=dim[1] - 1,
    **kwargs_slider,
)
slider3 = dcc.Slider(
    id='slider3',
    max=dim[2] - 1,
    **kwargs_slider,
)
graph1 = dcc.Graph(
    id='graph1',
    figure=fig,
    # animate=True,
)

app.layout = html.Div(
    [slider1,
     slider2,
     slider3,
     graph1]
)


def latest_changed():
    # Get latest changed context
    context = [e for e in dash.callback_context.triggered][0]
    prop_id = context['prop_id']
    value = context['value']
    print(
        f'Latest prop_id is "{prop_id}" with value of "{value}"')
    return prop_id, value


@app.callback(
    Output('graph1', 'figure'),
    Input('slider1', 'value'),
    Input('slider2', 'value'),
    Input('slider3', 'value'),
    Input('graph1', 'clickData'),
)
def update_on_sliders(slider1_value, slider2_value, slider3_value, d):
    r, c, s = 0, 0, 0
    prop_id, _ = latest_changed()
    if prop_id.startswith('graph1.'):
        point = d['points'][0]
        r = point['x']
        c = point['y']
        s = point['z']

    if any([prop_id.startswith(e)
            for e in ['slider1.',
                      'slider2.',
                      'slider3.']]):
        r, c, s = slider1_value, slider2_value, slider3_value

    print(r, c, s)
    return volume_fig.update_traces(r, c, s)


if __name__ == '__main__':
    app.run_server(debug=True, port=8000)
