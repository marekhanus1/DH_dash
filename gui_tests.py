from dash import _dash_renderer, Dash
import dash_mantine_components as dmc

_dash_renderer._set_react_version("18.2.0")

# NESAHAT
#################################################################################
#################################################################################


from dash import html, dcc, Input, Output, State, no_update
import dash_mantine_components as dmc
from datetime import datetime
import os
from dash_iconify import DashIconify


app = Dash(__name__, external_stylesheets=dmc.styles.ALL, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=2"},])


# Dictionary to map month numbers to Czech month names
month_names = {
    1: "Leden", 2: "Únor", 3: "Březen", 4: "Duben",
    5: "Květen", 6: "Červen", 7: "Červenec", 8: "Srpen",
    9: "Září", 10: "Říjen", 11: "Listopad", 12: "Prosinec"
}

def get_dates_from_filenames(folder_path):
    dates = {}

    for filename in os.listdir(folder_path):
        # Check if the filename matches the expected format
        if filename.startswith("Holter_"):
            # Extract the YYMMDD part
            try:
                date_part = filename.split("_")[1]
                date_obj = datetime.strptime(date_part, "%y%m%d").date()
                
                # Format date for display
                label = date_obj.strftime("%d. %-m. %Y")
                month_name = month_names[date_obj.month]
                
                # Create the month group if it doesn't exist
                if month_name not in dates:
                    dates[month_name] = []
                
                # Add the date entry to the month's list if it's unique
                select_obj = {"label": label, "value": date_part}
                if select_obj not in dates[month_name]:
                    dates[month_name].append(select_obj)
            except ValueError:
                # If filename format doesn't match, skip it
                pass
    
    # Convert to desired grouped format
    grouped_dates = [{"group": month, "items": items} for month, items in dates.items()]
    
    return grouped_dates

# Example usage
folder_path = "holter_vysledky"
dates = get_dates_from_filenames(folder_path)
print(dates)


opt = [
            {'label': 'New York City', 'value': 'New York City', 'disabled': True},
            {'label': 'Montreal', 'value': 'Montreal'},
            {'label': 'San Francisco', 'value': 'San Francisco'},
        ]

layout = html.Div(
    [
        
        dmc.RadioGroup(
            children=[
                dmc.Radio("Již stažené datum", value="normal"),
                dmc.Radio("Jiné datum", value="jine")
            ],
            id="datum_radio",
            value="normal",
            label="Vyberte datum",
            size="sm",
            mb=10,
            readOnly=True  # Disables the entire RadioGroup
        ),

        html.Div(
            children=[
                dmc.Select(
                    id="datum_input",
                    data=dates,
                    w=200,
                    mb=10,
                ),
            ], id="datum_div"
        ),

        dmc.Button("Potvrdit", id="submit_button", n_clicks=0, color="green"),
        html.Div(id='output-div'),
    ]
)



@app.callback(Output("datum_div", "children"), Input("datum_radio", "value"))
def choose_framework(value):
    datum_content = []
    if value == "normal":
        datum_content = dmc.Select(
                    id="datum_input",
                    data=dates,
                    leftSection=DashIconify(icon="clarity:date-line"),
                    w=300,
                    mb=10),
    
        return datum_content
    elif value == "jine":
        datum_content = dmc.DatePicker(
                    id="datum_input",
                    value=datetime.today(), leftSection=DashIconify(icon="clarity:date-line"), w=300
                ),
        return datum_content
    
    else:
        return no_update
    

@app.callback(
    Output("output-div", "children"),
    Input("submit_button", "n_clicks"),
    State("datum_radio", "value"),
    State("datum_input", "value")
)
def display_selected_date(n_clicks, selected_radio, datepicker_value):
    if n_clicks == 0:
        return no_update  # Do nothing if the button hasn't been clicked yet
    
    if len(datepicker_value) > 6:
        datepicker_value = datepicker_value[2:].replace("-", "")
    print(datepicker_value)



#################################################################################
#################################################################################
# NESAHAT



app.layout = dmc.MantineProvider(
        forceColorScheme="dark",
        theme=dmc.DEFAULT_THEME,
        children=html.Div([
            layout
        ], id="main-div")
    )



if __name__ == "__main__":
    app.run_server(debug=True)
