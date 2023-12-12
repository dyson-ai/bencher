import panel as pn

markdown_text = "This is a Markdown pane with a blue background."
markdown_pane = pn.pane.Markdown(markdown_text, style={'background-color': 'blue', 'color': 'white'})

app = pn.Column(markdown_pane)
app.show()
