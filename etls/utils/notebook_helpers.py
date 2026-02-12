from IPython.display import HTML


def scrollable_table(dataframe, height="20em"):
    """
    Wraps a pandas DataFrame in a scrollable HTML div.
    Adjust the 'height' parameter to change the size of the window.
    """
    html = (
        f'<div style="height:{height}; overflow:auto;">'
        + dataframe.to_html()
        + "</div>"
    )
    return HTML(html)
