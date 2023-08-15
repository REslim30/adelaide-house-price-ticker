import plotly.express as px
from domain import QuarterlyMedianHouseSales
import pandas as pd
import json

# Returns file path of chart image
def generate_quarterly_median_house_sales_choropleth(index: QuarterlyMedianHouseSales) -> str:
    df = pd.read_excel(index.excel_data)
    with open('adelaide_suburbs.geojson') as f:
        adelaide_suburbs = json.load(f)
    median_price_field = f'Median {index.quarter}Q {index.year}'
    fig = px.choropleth_mapbox(df, geojson=adelaide_suburbs, locations='Suburb', color=median_price_field,
                            featureidkey="properties.suburb",
                            color_continuous_scale=px.colors.sequential.Reds,
                            range_color=(300_000, 2_750_000),
                            mapbox_style="open-street-map",
                            zoom=12, center = {"lat": -34.921230, "lon": 138.599503},
                            opacity=0.5,
                            labels={median_price_field:'Median House Prices'}
                            )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    file_path = "/tmp/fig1.png"
    fig.write_image(file_path, width=1920, height=1080, scale=2)
    return file_path