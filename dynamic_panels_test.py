'''
import dash
from dash import Input, Output, State, ClientsideFunction, html, dcc, ctx

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Button("Undo-Button", id="undoButton"),
    html.Button("Redo-Button", id="redoButton"),
    html.Div(id='output')
])

app.clientside_callback(
    """
        function(id) {
            document.addEventListener("keydown", function(event) {
                
                if (event.key == 'z') {
                    document.getElementById('undoButton').click()
                }
                if (event.key == 'x') {
                    document.getElementById('redoButton').click()
                }
                
            });
            return window.dash_clientside.no_update       
        }
    """,
    Output("undoButton", "id"),
    Input("undoButton", "id")
)

@app.callback(
    Output("output", "children"),
    Input("undoButton", "n_clicks"),
    Input("redoButton", "n_clicks"),
    prevent_initial_call=True
)
def show_value(n1, n2):
    return ctx.triggered_id


if __name__ == "__main__":
    app.run_server(debug=True)



from dash import Dash, dcc, html, Input, Output, State, ctx
import dash_ag_grid as dag
import pandas as pd

app = Dash(__name__)

# Sample DataFrame with 500 rows
df = pd.DataFrame({
    'id': range(1, 501),
    'data': [f'Data {i}' for i in range(1, 501)],
    'category': [''] * 500  # Empty column for category notes
})

# AG Grid configuration
column_defs = [
    {'headerName': 'ID', 'field': 'id', 'editable': False},
    {'headerName': 'Data', 'field': 'data', 'editable': False},
    {'headerName': 'Category', 'field': 'category', 'editable': True}
]

app.layout = html.Div([
    dag.AgGrid(
        id='ag-grid',
        columnDefs=column_defs,
        rowData=df.to_dict('records'),
        dashGridOptions = {'rowSelection': 'single', 'animateRows': False}
    ),
    html.Div([
        html.Button("Set Category A", id="epochy_category_a", n_clicks=0),
        html.Button("Set Category S", id="epochy_category_s", n_clicks=0),
        html.Button("Set Category N", id="epochy_category_n", n_clicks=0),
    ]),
])


app.clientside_callback(
    """
        function(id) {
            document.addEventListener("keydown", function(event) {
                
                if (event.key == 'a') {
                    document.getElementById('epochy_category_a').click()
                }
                if (event.key == 's') {
                    document.getElementById('epochy_category_s').click()
                }
                if (event.key == 'n') {
                    document.getElementById('epochy_category_n').click()
                }
                
            });
            return window.dash_clientside.no_update       
        }
    """,
    Output("epochy_category_a", "id"),
    Input("epochy_category_a", "id")
)




# Callback to handle button clicks and update the category
@app.callback(
    Output('ag-grid', 'rowData'),  # Update the grid data
    Input('epochy_category_a', 'n_clicks'),
    Input('epochy_category_s', 'n_clicks'),
    Input('epochy_category_n', 'n_clicks'),
    State('ag-grid', 'selectedRows'),  # Get selected row data
    State('ag-grid', 'rowData'),  # Get current data of the grid
    prevent_initial_call=True
    
)
def set_category(n_clicks_a, n_clicks_s, n_clicks_n, selected_rows, row_data):

    if not selected_rows:
        return row_data  # No row selected, return current data unchanged

    # Determine which button was clicked
    category = None
    if ctx.triggered_id == "epochy_category_a":
        category = 'A'
    elif ctx.triggered_id == "epochy_category_s":
        category = 'S'
    elif ctx.triggered_id == "epochy_category_n":
        category = 'N'

    # Get the selected row ID
    selected_row_id = selected_rows[0]['id'] if selected_rows else None

    # Update the category in the selected row
    if category and selected_row_id is not None:
        for row in row_data:
            if row['id'] == selected_row_id:
                row['category'] = category  # Set the category
                break

    return row_data  # Return updated row data

if __name__ == '__main__':
    app.run_server(debug=True)
'''

from dash import Dash, dcc, html, Input, Output, State, ClientsideFunction
import dash_ag_grid as dag
import pandas as pd
import random

app = Dash(__name__)

# Sample DataFrame with 500 rows of random data
df = pd.DataFrame({
    'id': range(1, 501),
    'data': [f'Data {i}' for i in range(1, 501)],
    'random_value': [random.randint(1, 1000) for _ in range(500)],
    'category': [''] * 500  # Empty column for category notes
})

# AG Grid configuration
column_defs = [
    {'headerName': 'ID', 'field': 'id', 'editable': False},
    {'headerName': 'Data', 'field': 'data', 'editable': False},
    {'headerName': 'Random Value', 'field': 'random_value', 'sortable': True, 'editable': False},
    {'headerName': 'Category', 'field': 'category', 'editable': True}
]

app.layout = html.Div([
    dag.AgGrid(
        id='ag-grid',
        columnDefs=column_defs,
        rowData=df.to_dict('records'),
    ),
    html.Div([
        html.Button("Set Category A", id="set-category-a", n_clicks=0),
        html.Button("Set Category S", id="set-category-s", n_clicks=0),
        html.Button("Set Category N", id="set-category-n", n_clicks=0),
    ]),
    dcc.Store(id='sorted-order-store')  # Store to manage the sorted row order
])

# Clientside callback to get the sorted row order from the grid
app.clientside_callback(
    ClientsideFunction(
        namespace="clientside",
        function_name="getSortedOrder"
    ),
    Output('sorted-order-store', 'data'),
    Input('ag-grid', 'virtualRowData')  # Triggers when grid data changes
)

# Python callback to handle button clicks, update category, and move to the next visual row
@app.callback(
    Output('ag-grid', 'rowData'),        # Update the grid data
    Output('ag-grid', 'selectedRows'),   # Update the selected row
    Input('set-category-a', 'n_clicks'),
    Input('set-category-s', 'n_clicks'),
    Input('set-category-n', 'n_clicks'),
    State('ag-grid', 'selectedRows'),    # Get selected row data
    State('ag-grid', 'rowData'),         # Get current data of the grid
    State('sorted-order-store', 'data')  # Sorted row order from clientside
)
def set_category_and_move(n_clicks_a, n_clicks_s, n_clicks_n, selected_rows, row_data, sorted_order):
    if not selected_rows or not sorted_order:
        return row_data, []  # No row selected or no sorted order, return unchanged data

    # Determine which button was clicked
    category = None
    if n_clicks_a > 0:
        category = 'A'
    elif n_clicks_s > 0:
        category = 'S'
    elif n_clicks_n > 0:
        category = 'N'

    # Find the index of the selected row in the sorted order
    selected_row = selected_rows[0]
    selected_index = next((i for i, row in enumerate(sorted_order) if row['id'] == selected_row['id']), None)

    # Update the category for the selected row and move to the row below in the sorted view
    if category is not None and selected_index is not None:
        for row in row_data:
            if row['id'] == selected_row['id']:
                row['category'] = category  # Update the category in rowData

        # Move to the next row in the sorted order if it exists
        new_selected_index = selected_index + 1 if selected_index + 1 < len(sorted_order) else selected_index
        new_selected_row = [sorted_order[new_selected_index]]

        return row_data, new_selected_row  # Return updated data and the new selection

    return row_data, selected_rows  # If no category was set, return unchanged data


# JavaScript to retrieve sorted rows order
app.clientside_callback("""
window.clientside = {
    getSortedOrder: function(rowData) {
        // Extracts the current visible/sorted order of the rows
        return rowData;
    }
}
""")

if __name__ == '__main__':
    app.run_server(debug=True)
