import plotly.graph_objects as go
from plotly.offline import plot


def bar_graphic(labels, values, options):
    """Options fields are: title, height"""
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=labels,
            y=values,
            name=options["title"],
        )
    )

    # Customize aspect
    fig.update_traces(
        marker_line_color="rgb(8,48,107)",
        marker_line_width=1.5,
        opacity=0.8,
    )
    fig.update_layout(
        title="Numero de voluntarios por actividad",
        title_font_color="green",
        title_font_size=20,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_tickangle=-45,
        yaxis=dict(title=options["yaxis"]),
        margin=dict(l=0, r=0, t=30, b=0),
        height=options["height"],
        width=options["width"],
    )

    plot_div = plot(fig, output_type="div", config={"displaylogo": False})

    return plot_div


def pie_graphic(labels, values, options, show_legend=True):

    colors = [
        "#0099ff",
        "#66ff33",
        "#ffa348",
        "#ffff00",
        "#ff1a1a",
        "#e600e6",
        "#66ffcc",
        "#ffb3b3",
        "#cccc00",
        "#99c1f1",
        "#1a53ff",
        "#669999",
    ]
    fig = go.Figure(
        data=go.Pie(
            labels=labels,
            values=values,
        )
    )
    if len(labels) > len(colors):
        marker_opts = dict(line=dict(color="darkblue", width=1))
    else:
        marker_opts = dict(colors=colors, line=dict(color="darkblue", width=1))
    fig.update_traces(
        hoverinfo="label+percent",
        textinfo="value",
        textfont_size=16,
        title_font=dict(size=18, family="Verdana", color="darkgreen"),
        marker=marker_opts,
        opacity=0.7,
    )

    fig.update_layout(
        height=370,
        width=420,
        showlegend=show_legend,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title=options["title"],
        title_font_color="blue",
        title_font_size=20,
        margin=dict(l=0, r=0, t=30, b=0),
    )

    plot_div = plot(fig, output_type="div", config={"displaylogo": False})
    return plot_div


def conversion_data(input_data, label_key=None, label_value=None, list=None):
    if list is not None:
        data = {"label": [], "value": []}
    else:
        data = []
    if isinstance(input_data, dict):
        for key, values in input_data.items():
            data_dict = {}
            data_dict["label"] = key
            data_dict["value"] = values
            data.append(data_dict)
    # converting data when is a list of dictionnary
    else:
        if label_key is None:
            # process dictionnary when each item in list contains only
            # key / value
            for dict_item in input_data:
                for key, values in dict_item.items():
                    data_dict = {}
                    if isinstance(values, float):
                        values = round(values, 2)
                    data_dict["label"] = key
                    data_dict["value"] = values
                    data.append(data_dict)
        else:
            # process dictionary when item list contains 2 dictionnaries
            # one for the key and the other for the value
            # label_key and label_value are used to map correctly

            for dict_item in input_data:
                if list is None:
                    data_dict = {}
                values = dict_item[label_value]
                if isinstance(values, float):
                    values = round(values, 2)
                if list is None:
                    data_dict["label"] = dict_item[label_key]
                    data_dict["value"] = values
                    data.append(data_dict)
                else:
                    data["label"].append(dict_item[label_key])
                    data["value"].append(values)
    return data
