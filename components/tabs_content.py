import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify
from components.utils import Utils
import os
from datetime import datetime

card_style = {
    "height": 380,
    "marginTop": 5,
    "marginBottom": 20,
}


def show_tabs(disabled=False):
    config = Utils.read_config()

    tab1_content = dmc.TabsPanel(
        dmc.Card(
            [
                dmc.Text("Nastavení datových souborů"),
                dmc.Divider(labelPosition="center"),
                dmc.Space(h="20"),

                dmc.RadioGroup(
                    children=dmc.Group([dmc.Radio(l, value=k) for k, l in [["normal", "Již stažené datum"], ["jine", "Jiné datum"]]], my=10),
                    id="datum_radio",
                    value="normal",
                    label="Vyberte datum",
                    size="sm",
                    mb=10,
                    readOnly=disabled
                ),

                html.Div(
                    children=[
                        dmc.Select(
                            id={"type": "nastaveni_input", "index": "datum_input"},
                            data=Utils.get_dates_from_filenames("local"),
                            value=config.get("date"),
                            leftSection=DashIconify(icon="clarity:date-line"),
                            w=200,
                            mb=10,
                            disabled=disabled
                            
                        ),
                    ], id="datum_div"
                ),
                
                dmc.Space(h="20"),

                dmc.Checkbox(
                    id={"type": "nastaveni_checkbox", "index": "chbox_SSH"}, label="Stáhnout soubory přes SSH", checked=config.get('ssh'), mb=10, disabled=disabled
                ),

                dmc.Space(h="20"),



                # Slider with range 0-1439, representing 0:00 - 23:59, step of 10 minutes
                dmc.Switch(
                    label="Nastavit časové rozmezí vyhodnocení",
                    id={"type": "nastaveni_switch", "index": "range_switch"},
                    onLabel="ON",
                    offLabel="OFF",
                    checked=config.get('rangeSW'), disabled=disabled
                ),
                html.Div([
                dmc.RangeSlider(
                    id={"type": "nastaveni_inputSW", "index": 'time-range-slider'},
                    max=1439,
                    step=10,  # Step by 10 minutes
                    value=[config.get('rangeMin'), config.get('rangeMax')], 
                    # Show time every 2 hours (120 minutes)
                    marks=[{"value":i, "label":Utils.minutes_to_time(None,i)} for i in range(0, 1440, 120)],
                    w=800, disabled=disabled
                ),
                html.Div(id='output-time-range', style={'marginTop': 20}),
                ], id="time_range_div", hidden=True),

            ],withBorder=True,
        shadow="sm",
        radius="md",
        w=1000,
        style=card_style
        ),
        value="1"
    )

    tab2_content = dmc.TabsPanel(
        dmc.Card(
            [
                dmc.Space(h="5"),

                dmc.Divider(label="EKG", labelPosition="center"),

                dmc.NumberInput(id={"type": "nastaveni_input", "index":"arg_limit"}, label="Limit vyhodnocení píků", step=10, value=config.get('pik_limit'), w=385, disabled=disabled),
                
                dmc.Space(h=20),


                dmc.Grid(children=[
                    dmc.GridCol([
                        dmc.Switch(
                            id={"type": "nastaveni_switch", "index": "butter_switch"},
                            label="Butterworthův filtr",
                            onLabel="ON",
                            offLabel="OFF",
                            checked=config.get('butter_SW'), disabled=disabled
                        )
                    ], span = 6.5),
                    dmc.GridCol([
                        dmc.NumberInput(id={"type": "nastaveni_inputSW", "index": "arg_butter"}, step=0.1, value=config.get('butter_val'), darkHidden=True, disabled=disabled),
                    ], span=5.5),

                    dmc.GridCol([
                        dmc.Switch(
                        id={"type": "nastaveni_switch", "index": "vrub_switch"},
                        label="Vrubový filtr",
                        onLabel="ON",
                        offLabel="OFF",
                        checked=config.get('vrub_SW'), disabled=disabled
                        ),
                    ], span=6.5),

                    dmc.GridCol([
                        dmc.NumberInput(id={"type": "nastaveni_inputSW", "index": "arg_vrub"}, step=0.1, value=config.get('vrub_val'), darkHidden=True, disabled=disabled)
                    ], span=5.5),

                ], w=600),



                dmc.Space(h=20),

                ##################################################################################################################
                dmc.Divider(label="FLEX", labelPosition="center"),

                dmc.NumberInput(id={"type": "nastaveni_input", "index":"arg_flexprom"}, label="Prominence flex píků", step=1, value=config.get('flex_prom'), w=385, disabled=disabled),
                
                dmc.Space(h=20),

                dmc.Grid(children=[
                    dmc.GridCol([
                        dmc.Switch(
                            id={"type": "nastaveni_switch", "index": "butterflex_switch"},
                            label="Butterworthův filtr",
                            onLabel="ON",
                            offLabel="OFF",
                            checked=config.get('flexbutter_sw'), disabled=disabled
                        ),
                    ], span=6.5),
                    dmc.GridCol([
                        dmc.NumberInput(id={"type": "nastaveni_inputSW", "index": "arg_butterflex"}, step=0.1, value=config.get('flexbutter_val'), darkHidden=True, disabled=disabled)
                    ], span=5.5),
                ], w=600),
            ],withBorder=True,
        shadow="sm",
        radius="md",
        w=1000,
        style=card_style
        ),
        value="2"
    )

    tab3_content = dmc.TabsPanel(
        dmc.Card(
            [
                dmc.Divider(label="EXPORT", labelPosition="center", size="md"),
                dmc.Checkbox(
                    id={"type": "nastaveni_checkbox", "index": "chbox_export"}, label="Exportovat soubory pro EKG ANALYTIK", checked=config.get('exportEKG'), mb=10, disabled=disabled
                ),

            ],
        withBorder=True,
        shadow="sm",
        radius="md",
        w=1000,
        style=card_style
        ),
        value="3"
    )

    tab4_content = dmc.TabsPanel(
        dmc.Card(
            [
                

                dmc.Divider(label="Epoch analyzér", labelPosition="center"),
                dmc.SimpleGrid(cols=2,spacing="xs", verticalSpacing="lg", w=400, children=[
                    dmc.Switch(
                        id={"type": "nastaveni_switch", "index": "epoch_switch"},
                        label="Analýza epoch",
                        onLabel="ON",
                        offLabel="OFF",
                        checked=config.get('epoch_switch'), disabled=disabled
                    ),
                    dmc.NumberInput(id={"type": "nastaveni_inputSW", "index": "epoch_delka"}, label="Délka epochy [s]", step=1, value=config.get('epoch_delka'), w=150, disabled=disabled),
                ]),

                dmc.Space(h=20),
                dmc.Divider(label="Pík analyzér", labelPosition="center"),
                
                dmc.Switch(
                    id={"type": "nastaveni_switch", "index": "pik_switch"},
                    label="Analýza píků",
                    onLabel="ON",
                    offLabel="OFF",
                    checked=config.get('pik_switch'), disabled=disabled
                ),

                html.Div(children=[
                    dmc.Group(gap=50, children=[
                        
                        dmc.TextInput(
                            label="Čas začátku vyhodnocení",
                            value=config.get('pik_rangeStart'),
                            id={"type": "nastaveni_inputSW", "index": 'pik_time-start'},
                            w=250,
                            disabled=disabled
                        ),
                        dmc.TextInput(
                            label="Čas konce vyhodnocení",
                            value=config.get('pik_rangeEnd'),
                            id={"type": "nastaveni_inputSW", "index": 'pik_time-end'},
                            w=250,
                            disabled=disabled
                        ),
                    ]),

                    dmc.Space(h=20),
                    dmc.NumberInput(id={"type": "nastaveni_inputSW", "index":"arg_piklimit"}, label="Prominence P píků", step=10, value=config.get('pik_prominenceP'), w=385, disabled=disabled),
                ], id="pik_time_range_div", hidden=True),
                    
            ],withBorder=True,
        shadow="sm",
        radius="md",
        w=1000,
        style=card_style
        ),
        value="4"
    )


    tabs = dmc.Tabs(
        [
            dmc.TabsList([
                dmc.TabsTab("Soubory", value="1"),
                dmc.TabsTab("Filtry a limity", value="2"),
                dmc.TabsTab("Zobrazení a export", value="3"),
                dmc.TabsTab("Epochy a píky", value="4"),
            ]),
            tab1_content,
            tab2_content,
            tab3_content,
            tab4_content,

            dmc.Drawer(
            title="Log soubor",
            id="logfile_drawer",
            padding="md",
            size="50%",
            #position="right",
            ),

        ], value="1", color="blue", variant="pills",
    )

    return tabs