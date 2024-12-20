from dash import html, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from components.tabs_content import show_tabs
from components.vysledky_chart_content import appshell
from components.epochy_content import show_epochy

style = {
    "height": 800,
    "marginTop": 20,
    "marginBottom": 20,
    "zoom": 1.5,
}

def create_card(title,disc, link="#", loading=True, src=None):
    return dmc.Card(
        children=[
            dcc.Link(
                [
                    dmc.Text(title, size="lg"),
                    dmc.Text(disc, size="sm"),
                    
                    dmc.LoadingOverlay(
                        visible=loading,
                        overlayProps={"radius": "sm", "blur": 2},
                        zIndex=10,
                    ),
                    dmc.BackgroundImage(
                        dmc.Box(h=200, w=100),
                        src=src,
                    ),
                    
                ],
                href=link,

                style={"textDecoration": "none", "color": "inherit"}  # Removes blue text underline
            ),
        ],
        withBorder=True,
        shadow="sm",
        radius="md",
    )

class layout_content():
    def before_start():
        return html.Div([
                        dcc.Store(id='stage-store'),
                        html.H1("Holter dekodér", style={"text-align": "center"}),
                        dmc.Container([
                            html.Div([
                                html.H3("Nastavení"),
                                show_tabs(disabled=False),
                                dmc.Button("Potvrdit", id="submit-button", n_clicks=0, color="green"),
                                html.Div(id='output-div'),
                            ])
                        ])
                ], style=style)

    def after_start():
        return html.Div([
                    html.H1("Holter dekodér", style={"text-align": "center"} ,id="title"),
                    dcc.Store(id='stage-store'),
                    dcc.Interval(id="my-interval", interval=1000),
                    
                    dmc.Container([
                        html.Div([
                            dmc.Accordion(
                                children=[
                                    dmc.AccordionItem(
                                        [
                                            dmc.AccordionControl("Nastavení", icon=DashIconify(icon="clarity:settings-solid")),
                                            dmc.AccordionPanel([
                                                show_tabs(disabled=True),
                                            ]),
                                        ],
                                        value="nastaveni",
                                    ),
                                    dmc.AccordionItem(
                                        [
                                            dmc.AccordionControl("Info", icon=DashIconify(icon="clarity:info-solid")),
                                            dmc.AccordionPanel([
                                                dmc.Card([html.Div([], id="fileinfo_div")], shadow="sm",radius="md",withBorder=True)
                                            ]),
                                        ],
                                        value="info",
                                    ),
                                    
                            ], value="info"),
                            
                            dmc.Space(h="30"),

                            dmc.Button("Resetovat vyhodnocení", id="reset-button", n_clicks=0, color="red"),

                            dmc.Space(h="5"),

                            dmc.ProgressRoot(
                                [],
                                id="vyhodnoceni_progress",
                                size=20,
                                
                            ),

                            dmc.Space(h="10"),
                            
                            dmc.Container([
                                dmc.SimpleGrid(cols=2,spacing="lg", verticalSpacing="lg", children=[
                                     
                                    create_card("VÝSLEDKY", "Zobrazit vyhodnocené data v grafu", src="assets/vysledky_img.png"),
                                    create_card("EPOCHY",   "Zobrazit jednotlivé epochy měření", src="assets/epochy_img.png"),
                                ],
                            )
                            ])
                                
                        ]),
                    ])
            ], style=style)
    

    def decoding_done():
        return html.Div([
                    dcc.Location(id='url', refresh=False),  
                    html.H1("Holter dekodér", style={"text-align": "center"} ,id="title"),
                    dcc.Interval(id="my-interval2", interval=1000),
                    dmc.Container([
                        html.Div([
                            dmc.Accordion(
                                children=[
                                    dmc.AccordionItem(
                                        [
                                            dmc.AccordionControl("Nastavení", icon=DashIconify(icon="clarity:settings-solid")),
                                            dmc.AccordionPanel([
                                                show_tabs(disabled=True),
                                            ]),
                                        ],
                                        value="nastaveni",
                                    ),
                                    dmc.AccordionItem(
                                        [
                                            dmc.AccordionControl("Info", icon=DashIconify(icon="clarity:info-solid")),
                                            dmc.AccordionPanel([
                                                dmc.Card([
                                                    html.Div([
                                                        dmc.Group(["Počet souborů: ", dmc.Loader(color="red", size="md", type="dots")]),
                                                        dmc.Group(["Počet naměřených minut: ", dmc.Loader(color="red", size="md", type="dots")]),
                                                        dmc.Group(["Úseky měření: ", dmc.Loader(color="red", size="md", type="dots")]),
                                                ], id="fileinfo_div")
                                                ], shadow="sm",radius="md",withBorder=True),
                                            ]),
                                        ],
                                        value="info",
                                    ),
                            ]),
                            
                            dmc.Space(h="30"),
                            dmc.Button("Nové vyhodnocení", id="reset-button", n_clicks=0, color="blue"),
                            dmc.Space(h="5"),
                            

                            dmc.ProgressRoot(
                                [
                                    dmc.ProgressSection(dmc.ProgressLabel("EKG"), value=40, color="red"),
                                    dmc.ProgressSection(dmc.ProgressLabel("FLEX"), value=15, color="orange"),
                                    dmc.ProgressSection(dmc.ProgressLabel("EPOCHY"), value=15, color="pink"),
                                    dmc.ProgressSection(dmc.ProgressLabel("HR A RESP"), value=15, color="cyan"),
                                    dmc.ProgressSection(dmc.ProgressLabel("DOKONČENO"), value=15, color="green"),
                                ],
                                size=20,
                                
                            ),

                            dmc.Space(h="10"),
                            
                            dmc.Container([
                                dmc.SimpleGrid(cols=2,spacing="lg", verticalSpacing="lg", children=[
                                    create_card("VÝSLEDKY", "Zobrazit vyhodnocené data v grafu", link="/vysledky", loading=False, src="assets/vysledky_img.png"),
                                    create_card("EPOCHY",   "Zobrazit jednotlivé epochy měření", link="/epochy",   loading=False, src="assets/epochy_img.png"),
                                ])
                            ])
                                
                        ]),
                    ])
                ], style=style)
    
    def chart_vysledky():
        return appshell
    
    def epochy():
        return show_epochy()