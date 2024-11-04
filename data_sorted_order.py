import dash
from dash import html, dcc, Input, Output, State, no_update
import dash_ag_grid as dag
import pandas as pd

# Sample data
data = {
    "Name": ["Alice", "Bob", "Charlie", "David"],
    "Age": [24, 30, 22, 35],
    "City": ["New York", "Los Angeles", "Chicago", "Houston"]
}
df = pd.DataFrame(data)

# Define column definitions
columnDefs = [
    {"headerName": "Name", "field": "Name", "sortable": True},
    {"headerName": "Age", "field": "Age", "sortable": True},
    {"headerName": "City", "field": "City", "sortable": True}
]

# Initialize the Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    dag.AgGrid(
        id='my-grid',
        columnDefs=columnDefs,
        rowData=df.to_dict('records'),
        defaultColDef={'sortable': True},
        dashGridOptions={
            'onSortChanged': {'function': 'function(event) { dash_clientside.callback(event.api.getSortModel()); }'}
        }
    ),
    html.Div(id='sorted-data')
])

# Clientside callback to handle sorting event
app.clientside_callback(
    """
    function(sortModel) {
        // Get the sorted data order
        const sortedData = sortModel.map(sort => sort.colId);
        // Return the sorted data order
        return sortedData;
    }
    """,
    Output('my-grid', 'sortedData'),
    Input('my-grid', 'sortChanged')
)

# Serverside callback to update the sorted data
@app.callback(
    Output('sorted-data', 'children'),
    Input('my-grid', 'sortedData'),
    State('my-grid', 'rowData'),
    prevent_initial_call=True
)
def update_sorted_data(sorted_data, row_data):
    if not sorted_data:
        return no_update

    # Sort the row_data based on the sorted_data order
    sorted_row_data = sorted(row_data, key=lambda x: [x[col] for col in sorted_data])
    return html.Pre(str(sorted_row_data))

if __name__ == '__main__':
    app.run_server()