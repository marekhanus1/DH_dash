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
                            id="datum_input",
                            data=Utils.get_dates_from_filenames(),
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
                    id="chbox_SSH", label="Stáhnout soubory přes SSH", checked=config.get('ssh'), mb=10, disabled=disabled
                ),

                dmc.Space(h="20"),



                # Slider with range 0-1439, representing 0:00 - 23:59, step of 10 minutes
                dmc.Switch(
                    label="Nastavit časové rozmezí vyhodnocení",
                    id="range_switch",
                    onLabel="ON",
                    offLabel="OFF",
                    checked=config.get('rangeSW'), disabled=disabled
                ),
                html.Div([
                dmc.RangeSlider(
                    id='time-range-slider',
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

                dmc.NumberInput(id="arg_limit", label="Limit vyhodnocení píků", step=10, value=config.get('pik_limit'), w=385, disabled=disabled),
                
                dmc.Space(h=20),

                
                dmc.SimpleGrid(cols=2,spacing="xs", verticalSpacing="lg", w=600, children=[
                    dmc.Switch(
                        id="butter_switch",
                        label="Butterworthův filtr",
                        onLabel="ON",
                        offLabel="OFF",
                        checked=config.get('butter_SW'), disabled=disabled
                    ),
                    dmc.NumberInput(id="arg_butter", step=0.1, value=config.get('butter_val'), darkHidden=True, disabled=disabled),

                    dmc.Switch(
                        id="vrub_switch",
                        label="Vrubový filtr",
                        onLabel="ON",
                        offLabel="OFF",
                        checked=config.get('vrub_SW'), disabled=disabled
                    ),
                    dmc.NumberInput(id="arg_vrub", step=0.1, value=config.get('vrub_val'), darkHidden=True, disabled=disabled)
                ]),
                dmc.Space(h=20),

                ##################################################################################################################
                dmc.Divider(label="FLEX", labelPosition="center"),

                dmc.NumberInput(id="arg_flexprom", label="Prominence flex píků", step=1, value=config.get('flex_prom'), w=385, disabled=disabled),
                
                dmc.Space(h=20),

                dmc.SimpleGrid(cols=2,spacing="xs", verticalSpacing="lg", w=600, children=[
                    dmc.Switch(
                        id="butterflex_switch",
                        label="Butterworthův filtr",
                        onLabel="ON",
                        offLabel="OFF",
                        checked=config.get('flexbutter_sw'), disabled=disabled
                    ),
                    dmc.NumberInput(id="arg_butterflex", step=0.1, value=config.get('flexbutter_val'), darkHidden=True, disabled=disabled)
                ]),
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
                    id="chbox_export", label="Exportovat soubory pro EKG ANALYTIK", checked=config.get('exportEKG'), mb=10, disabled=disabled
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
                dmc.NumberInput(id="epoch_delka", label="Délka epochy [s]", step=1, value=config.get('epoch_delka'), w=385, disabled=disabled),

                
                    
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
                dmc.TabsTab("Epoch Analyzer", value="4"),
            ]),
            tab1_content,
            tab2_content,
            tab3_content,
            tab4_content
        ], value="1", color="blue", variant="pills"
    )

    return tabs