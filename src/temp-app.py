#%%
from re import X
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from dash import Dash, dcc, html, Input, Output
from sklearn.model_selection import train_test_split
import pandas as pd
import json
import geopandas as gpd

# =================================================================

# load data 

map_df = gpd.read_file("../data/riyadh.geojson")

with open(r"../data/riyadh_districts.json", 'r', encoding='utf8', errors='ignore') as file:
    neighborhood = json.load(file)


# getting arabic district names from neighborhood file
ar_name = []
en_name = []
for i in range(len(neighborhood)):
    ar_name.append(neighborhood[i]["name_ar"])
    en_name.append(neighborhood[i]["name_en"])

district_df = pd.DataFrame(ar_name, columns=['name_ar'])
district_df["name_en"] = en_name

map_df = map_df.merge(district_df, left_on=["name"], right_on=["name_en"])

apartments = pd.read_csv("../data/apartments_sale_riyadh_cleaned.csv")

# apartments = apartments[['price', 'beds', 'livings', 'wc', 'area', 
#                'street_width', 'age', 'ketchen', 'ac', 
#                'furnished', 'location', 'district', 'width',
#                'length', 'advertiser_type', 'longitude', 'latitude']]
city_side_mapper = {'north': 1, 'south': 2, 'east': 3, 'west':4, 'middle':5}
apartments['city_side'] = apartments['city_side'].apply(lambda side: city_side_mapper[side])

apartments = apartments.groupby(['district'], as_index=False).mean()
# print(apartments.columns)
apartments["district"] = apartments["district"].apply(lambda x: x.strip())



merged_df = map_df.merge(apartments, left_on=["name_ar"], right_on=["district"])

geo_df = merged_df.set_index("district")

# print(geo_df.columns)
# print(geo_df.iloc[2])



#%%
# ==================================================

# helper functions

def make_plot(geo_df, color):
    fig = px.choropleth_mapbox(geo_df,
                            geojson=geo_df.geometry,
                            locations=geo_df.index,
                            color=color,
                            center={"lat": 24.79, "lon":46.70},
                            opacity=0.3, 
                            color_continuous_scale='darkmint',
                            mapbox_style="carto-positron",
                            zoom=8,
                            title="متوسط أسعار الشقق حسب الحي (الرياض)",
                            hover_data={'price':':.0f'})
    return fig

district_features = [{'label': 'price', 'value': 'price'}, 
                     {'label': 'age', 'value': 'age'}, 
                     {'label': 'area', 'value': 'area'}, 
                     {'label': 'street width', 'value': 'street_width'}]

city_sides = [#{'label': 'All', 'value': ['north','south', 'east', 'west']}, 
              {'label': 'North', 'value': 'north'}, 
              {'label': 'South', 'value': 'south'}, 
              {'label': 'East', 'value': 'east'},
              {'label': 'West', 'value': 'west'},
              {'label': 'City center', 'value': 'middle'}]

# ==================================================

# make Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H3('Explore the Sale Appartment Market in Riyadh'),
    dcc.Graph(id="graph", ),
    html.H4("Select a feature to color the plot"),
    # dcc.Dropdown(id="dropdown_color", options=district_features),
    dcc.RadioItems(id="radio_color", options=district_features, value="price"),
    dcc.Checklist(id="checklist_city_side", options=city_sides, value=['north'])
])


@app.callback(Output("graph", "figure"), 
              Input("radio_color", "value"),
              Input("checklist_city_side", "value"))
# @app.callback()

def app_function(color='price', city_sides=['north','south', 'east', 'west']):
    
    # city_side_mapper = {'north': 1, 'south': 2, 'east': 3, 'west':4, 'middle':5}
    city_sides = list(pd.Series(city_sides).apply(lambda side: city_side_mapper[side]))

    df = geo_df.loc[geo_df['city_side'].apply(lambda side: side in city_sides)]
    fig = make_plot(df, color)
    
    return fig
# def app_function():
#     print("the function was run")


app.run(debug=True)