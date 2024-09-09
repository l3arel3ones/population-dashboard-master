# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

#######################
# Page configuration
st.set_page_config(
    page_title="US Population Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)

#######################
# Load data
df_reshaped = pd.read_csv('data/us-population-2010-2019-reshaped.csv')

#######################
# Sidebar
with st.sidebar:
    st.title('🏂 US Population Dashboard')

    year_list = list(df_reshaped.year.unique())[::-1]

    selected_year = st.selectbox('Select a year', year_list)
    df_selected_year = df_reshaped[df_reshaped.year == selected_year]
    df_selected_year_sorted = df_selected_year.sort_values(by="population", ascending=False)

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo',
                        'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)


#######################
# Functions for the Plots

# Heatmap function
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
        y=alt.Y(f'{input_y}:O',
                axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
        x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
        color=alt.Color(f'max({input_color}):Q',
                        legend=None,
                        scale=alt.Scale(scheme=input_color_theme)),
        stroke=alt.value('black'),
        strokeWidth=alt.value(0.25)
    ).properties(width=900
                 ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
    )
    return heatmap


# Choropleth map function
def make_choropleth(input_df, input_id, input_column, input_color_theme):
    choropleth = px.choropleth(input_df, locations=input_id, color=input_column, locationmode="USA-states",
                               color_continuous_scale=input_color_theme,
                               range_color=(0, max(df_selected_year.population)),
                               scope="usa",
                               labels={'population': 'Population'}
                               )
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth


# Donut chart function
def make_donut(input_response, input_text, input_color):
    chart_color = {'blue': ['#29b5e8', '#155F7A'],
                   'green': ['#27AE60', '#12783D'],
                   'orange': ['#F39C12', '#875A12'],
                   'red': ['#E74C3C', '#781F16']}[input_color]

    source = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100 - input_response, input_response]
    })

    plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta="% value",
        color=alt.Color("Topic:N", scale=alt.Scale(domain=[input_text, ''], range=chart_color), legend=None),
    ).properties(width=130, height=130)

    text = plot.mark_text(align='center', color=chart_color[0], font="Lato", fontSize=32, fontWeight=700,
                          fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
    return plot + text


# Format number for display
def format_number(num):
    if num > 1000000:
        return f'{round(num / 1000000, 1)} M'
    return f'{num // 1000} K'


# Population change calculation
def calculate_population_difference(input_df, input_year):
    selected_year_data = input_df[input_df['year'] == input_year].reset_index()
    previous_year_data = input_df[input_df['year'] == input_year - 1].reset_index()
    selected_year_data['population_difference'] = selected_year_data.population.sub(previous_year_data.population,
                                                                                    fill_value=0)
    return selected_year_data.sort_values(by="population_difference", ascending=False)


#######################
# Main Dashboard
col = st.columns((1.5, 4.5, 2), gap='medium')

with col[0]:
    st.markdown('#### Gains/Losses')

    df_population_difference_sorted = calculate_population_difference(df_reshaped, selected_year)

    if selected_year > 2010:
        first_state_name = df_population_difference_sorted.states.iloc[0]
        first_state_population = format_number(df_population_difference_sorted.population.iloc[0])
        first_state_delta = format_number(df_population_difference_sorted.population_difference.iloc[0])
    else:
        first_state_name, first_state_population, first_state_delta = '-', '-', ''
    st.metric(label=first_state_name, value=first_state_population, delta=first_state_delta)

    if selected_year > 2010:
        last_state_name = df_population_difference_sorted.states.iloc[-1]
        last_state_population = format_number(df_population_difference_sorted.population.iloc[-1])
        last_state_delta = format_number(df_population_difference_sorted.population_difference.iloc[-1])
    else:
        last_state_name, last_state_population, last_state_delta = '-', '-', ''
    st.metric(label=last_state_name, value=last_state_population, delta=last_state_delta)

    st.markdown('#### States Migration')

    if selected_year > 2010:
        df_greater_50000 = df_population_difference_sorted[
            df_population_difference_sorted.population_difference > 50000]
        df_less_50000 = df_population_difference_sorted[df_population_difference_sorted.population_difference < -50000]

        states_migration_greater = round(
            (len(df_greater_50000) / df_population_difference_sorted.states.nunique()) * 100)
        states_migration_less = round((len(df_less_50000) / df_population_difference_sorted.states.nunique()) * 100)
        donut_chart_greater = make_donut(states_migration_greater, 'Inbound Migration', 'green')
        donut_chart_less = make_donut(states_migration_less, 'Outbound Migration', 'red')
    else:
        donut_chart_greater = make_donut(0, 'Inbound Migration', 'green')
        donut_chart_less = make_donut(0, 'Outbound Migration', 'red')

    migrations_col = st.columns((0.2, 1, 0.2))
    with migrations_col[1]:
        st.write('Inbound')
        st.altair_chart(donut_chart_greater)
        st.write('Outbound')
        st.altair_chart(donut_chart_less)

with col[1]:
    st.markdown('#### Total Population')

    choropleth = make_choropleth(df_selected_year, 'states_code', 'population', selected_color_theme)
    st.plotly_chart(choropleth, use_container_width=True)

    heatmap = make_heatmap(df_reshaped, 'year', 'states', 'population', selected_color_theme)
    st.altair_chart(heatmap, use_container_width=True)

with col[2]:
    st.markdown('#### Top States')

    st.dataframe(df_selected_year_sorted[["states", "population"]],
                 hide_index=True)

    with st.expander('About', expanded=True):
        st.write('''
            - Data: [U.S. Census Bureau](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-state-total.html).
            - :orange[**Gains/Losses**]: States with high inbound/outbound migration for selected year.
            - :orange[**States Migration**]: Percentage of states with annual inbound/outbound migration > 50,000.
        ''')
