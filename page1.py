import streamlit as st
import pandas as pd
import numpy as np

st.title("RDW Car Data Analysis")

tab1, tab2, tab3 = st.tabs(["Barplot", "Lineplot", "Data"])

with tab1:
    @st.fragment
    def barplotter():
        st.header("Bar plot of car fuel types per make")
        df = st.session_state.data_merged.copy()
        
        selected_brands = st.multiselect('Select car brand', sorted(st.session_state.data_merged['merk'].unique().tolist()))
        df = df[df['merk'].isin(selected_brands)]
        st.bar_chart(df.groupby(['brandstof_omschrijving','merk'])['handelsbenaming'].nunique().unstack(fill_value=0))
    
    barplotter()

with tab2:
    st.header("Line plot of car registrations over time")
    
    # @st.fragment
    # def lineplotter():
    #     df = st.session_state.data_merged.copy()
    #     df['datum_tenaamstelling'] = pd.to_datetime(df['datum_tenaamstelling'])

    #     # Daily counts per (fuel, date). Use .nunique('Ticker') if you want unique models instead.
    #     daily = (
    #         df.groupby(['brandstof_omschrijving', 'datum_tenaamstelling'])
    #         .size()
    #         .reset_index(name='Daily')
    #     )

    #     # UI
    #     fuels_all = sorted(daily['brandstof_omschrijving'].unique().tolist())
    #     reg = st.radio("Select daily or cumulative registrations", ('Daily', 'Cumulative'),
    #                 index=0, key='reg_type')
    #     selected_fuels = st.multiselect('Select fuel type', fuels_all)
    #     if not selected_fuels:
    #         selected_fuels = fuels_all  # default to all

    #     # Build a full date range and fill missing days with 0
    #     date_idx = pd.date_range(daily['datum_tenaamstelling'].min(),
    #                             daily['datum_tenaamstelling'].max(), freq='D')

    #     grid = (
    #         pd.MultiIndex.from_product([selected_fuels, date_idx],
    #                                 names=['brandstof_omschrijving', 'datum_tenaamstelling'])
    #         .to_frame(index=False)
    #     )

    #     daily_sel = (grid
    #                 .merge(daily, how='left')
    #                 .fillna({'Daily': 0})
    #                 .sort_values(['brandstof_omschrijving', 'datum_tenaamstelling']))

    #     # Cumulative per fuel
    #     daily_sel['Cumulative'] = (
    #         daily_sel.groupby('brandstof_omschrijving')['Daily'].cumsum()
    #     )

    #     # Plot
    #     if reg == 'Daily':
    #         st.line_chart(daily_sel, x='datum_tenaamstelling', y='Daily', color='brandstof_omschrijving')
    #     else:
    #         st.line_chart(daily_sel, x='datum_tenaamstelling', y='Cumulative', color='brandstof_omschrijving')

    # lineplotter()


    @st.fragment
    def lineplotter_monthly():
        df = st.session_state.data_merged.copy()
        df['datum_tenaamstelling'] = pd.to_datetime(df['datum_tenaamstelling'])

        monthly = (
            df.groupby(['brandstof_omschrijving', df['datum_tenaamstelling'].dt.to_period('M')])
            .size()
            .reset_index(name='Monthly')
            .rename(columns={'datum_tenaamstelling': 'month'})
        )

        fuels_all = sorted(monthly['brandstof_omschrijving'].unique().tolist())
        metric = st.radio("Metric", ('Monthly', 'Cumulative', 'MoM change', 'MoM %'),
                        index=0, key='metric_monthly')
        selected_fuels = st.multiselect('Select fuel type', fuels_all, key='fuels_monthly')
        if not selected_fuels:
            selected_fuels = fuels_all

        month_range = pd.period_range(monthly['month'].min(), monthly['month'].max(), freq='M')
        grid = (pd.MultiIndex.from_product([selected_fuels, month_range], names=['brandstof_omschrijving', 'month']).to_frame(index=False))

        monthly_sel = (grid.merge(monthly, how='left').fillna({'Monthly': 0}).sort_values(['brandstof_omschrijving', 'month']))

        monthly_sel['date'] = monthly_sel['month'].dt.to_timestamp('M')

        monthly_sel['Cumulative'] = monthly_sel.groupby('brandstof_omschrijving')['Monthly'].cumsum()
        monthly_sel['MoM change'] = monthly_sel.groupby('brandstof_omschrijving')['Monthly'].diff().fillna(0)
        monthly_sel['MoM %'] = (monthly_sel.groupby('brandstof_omschrijving')['Monthly'].pct_change() * 100).replace([np.inf, -np.inf], np.nan).fillna(0)

        y_col = {'Monthly': 'Monthly', 'Cumulative': 'Cumulative',
                'MoM change': 'MoM change', 'MoM %': 'MoM %'}[metric]

        st.line_chart(monthly_sel, x='date', y=y_col, color='brandstof_omschrijving')

    lineplotter_monthly()

    
with tab3:
    st.write(sorted(st.session_state.data_merged.loc[st.session_state.data_merged.merk == 'BMW']['handelsbenaming'].unique().tolist()))
    st.write(st.session_state.data_merged.describe())
    