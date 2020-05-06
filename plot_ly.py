import plotly.graph_objects as go 
from ipywidgets import widgets

fig = go.Figure()

#### Make Plots ####
# Slider for date of projection
# Dropdown for projection (IHME, other if I find one with historical projections)
# Dropdown for deaths count source (covidtracker.com or CDC)
# [Optional] color forecasted line (based on slider date) in a different color

steps = []
for j in r:
    step = dict(
        method="restyle",
        args=["visible", [False] * test_len],
    )
    step["args"][1][j] = True  # Toggle i'th trace to "visible"
    steps.append(step)


atk_dice = widgets.IntSlider(
    value = 1.0,
    min = 1.0,
    max = 6.0,
    step = 1.0,
    description = 'Number of Attack Dice',
    continuous_update = False)

def_dice = widgets.IntSlider(
    value = 1.0,
    min = 1.0,
    max = 6.0,
    step = 1.0,
    description = 'Number of Defense Dice',
    continuous_update = False)

tgt_lk = widgets.Checkbox(
    description = 'Target Lock',
    value = False)

container = widgets.HBox(children = [atk_dice, def_dice, tgt_lk])

# j = 1
# row = df.iloc[j]
# M = (row['M_atk_dice'])
# mPhr = row.Phr
# mhits = np.arange(M+1)


trace1 = go.Bar(x = mhits, y = mPhr, opacity= 0.8, name = 'pdf')
g = go.FigureWidget(data = trace1, layout = go.Layout(
    title = dict(text = 'PDF')
))

widgets.VBox([container])


fig.show()

