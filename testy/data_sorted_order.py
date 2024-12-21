from dash import Dash, dcc, html, Input, Output, callback_context, ctx, no_update
from dash_ag_grid import AgGrid
import dash_ag_grid as dag
import pandas as pd
import random

app = Dash(__name__)

# Sample DataFrame
df = pd.DataFrame({
    'id': [1, 2, 3, 4],
    'name': ['John', 'Doe', 'Alice', 'Bob'],
    'age': [25, 30, 22, 35]
})

# AG Grid Layout
grid = dag.AgGrid(
    id='grid',
    rowData=df.to_dict('records'),
    columnDefs=[
        {'headerName': "ID", 'field': "id"},
        {'headerName': "Name", 'field': "name"},
        {'headerName': "Age", 'field': "age"},
    ],
    dashGridOptions={"rowSelection": "single"},
    getRowId="params.data.id"
)

app.layout = html.Div([
    grid,
    html.Button("Update Age", id="update-button"),
])

@app.callback(
    Output("grid", "rowTransaction"),
    Input("update-button", "n_clicks"),
    Input("grid", "selectedRows"),
)
def update_selected_cells(n_clicks, selected_rows):
    if ctx.triggered_id == "update-button":

        if n_clicks is None or not selected_rows:
            return no_update

        # Example: Update 'age' to 40 for selected rows
        updated_rows = []

        updated_row = selected_rows[0].copy()
        updated_row['age'] = random.randint(1,50)  # Set age to 40 or any desired value
        updated_rows.append(updated_row)

        print(updated_rows)

        return {'update': updated_rows}
    else:
        return no_update

if __name__ == "__main__":
    app.run_server(debug=True)





