#!/usr/bin/env python3
"""
Streamlit App for Monte Carlo Low Hold Betting Simulator

Interactive web interface for simulating low hold betting strategies
and analyzing ROI on sportsbook bonus conversions.
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from monte_carlo_betting_simulator import BettingConfig, run_monte_carlo

# Page configuration
st.set_page_config(
    page_title="Low Hold Betting Simulator",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .success-metric {
        color: #28a745;
        font-weight: bold;
    }
    .warning-metric {
        color: #ffc107;
        font-weight: bold;
    }
    .info-box {
        background-color: #e7f3ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #0066cc;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🎲 Low Hold Betting Simulator</div>', unsafe_allow_html=True)
st.markdown("**Monte Carlo simulation for sportsbook bonus conversion strategies**")
st.markdown("---")

# Sidebar - Input Parameters
st.sidebar.header("⚙️ Configuration")

# Bonus Parameters
st.sidebar.subheader("💰 Bonus Structure")
deposit = st.sidebar.number_input(
    "Promo Book Deposit ($)",
    min_value=100.0,
    max_value=10000.0,
    value=1000.0,
    step=100.0,
    help="Initial deposit into the promo sportsbook"
)

bonus_pct = st.sidebar.slider(
    "Bonus Match %",
    min_value=0,
    max_value=200,
    value=100,
    step=10,
    help="Percentage bonus match (e.g., 100 = 100% match)"
)

rollover = st.sidebar.slider(
    "Rollover Multiplier",
    min_value=1.0,
    max_value=25.0,
    value=10.0,
    step=0.5,
    help="How many times you must wager (deposit + bonus)"
)

rollover_lesser_of_bet_win = st.sidebar.checkbox(
    "Rollover = Lesser of Bet/Win",
    value=False,
    help="Some sportsbooks only credit the lesser of bet amount or win amount toward rollover when winning"
)

# Hold Parameters
st.sidebar.subheader("📊 Hold Range")
min_hold = st.sidebar.slider(
    "Minimum Hold %",
    min_value=0.0,
    max_value=3.0,
    value=0.0,
    step=0.1,
    help="Minimum hold percentage to accept"
) / 100

max_hold = st.sidebar.slider(
    "Maximum Hold %",
    min_value=0.1,
    max_value=5.0,
    value=2.5,
    step=0.1,
    help="Maximum hold percentage to accept"
) / 100

target_hold = st.sidebar.slider(
    "Target Hold % (Peak)",
    min_value=min_hold * 100,
    max_value=max_hold * 100,
    value=1.8,
    step=0.1,
    help="Most common hold percentage (peak of distribution)"
) / 100

# Bet Sizing
st.sidebar.subheader("💵 Bet Sizing")
min_bet = st.sidebar.number_input(
    "Minimum Bet ($)",
    min_value=50.0,
    max_value=1000.0,
    value=500.0,
    step=50.0
)

max_bet = st.sidebar.number_input(
    "Maximum Bet ($)",
    min_value=min_bet,
    max_value=5000.0,
    value=1500.0,
    step=100.0
)

max_favorite_bet = st.sidebar.number_input(
    "Max Favorite Bet ($)",
    min_value=min_bet,
    max_value=5000.0,
    value=1500.0,
    step=100.0,
    help="Maximum bet on favorite side (negative odds)"
)

min_underdog_bet = st.sidebar.number_input(
    "Min Underdog Bet ($)",
    min_value=50.0,
    max_value=max_bet,
    value=300.0,
    step=50.0,
    help="Minimum bet on underdog side (positive odds)"
)

# Odds Range
st.sidebar.subheader("🎯 Odds Range")
col1, col2 = st.sidebar.columns(2)
with col1:
    min_promo_odds = st.number_input(
        "Min Odds",
        min_value=-500,
        max_value=100,
        value=-200,
        step=50,
        help="Minimum promo book odds"
    )
with col2:
    max_promo_odds = st.number_input(
        "Max Odds",
        min_value=100,
        max_value=1000,
        value=450,
        step=50,
        help="Maximum promo book odds"
    )

# Capital
st.sidebar.subheader("💼 Capital")
regular_book_balance = st.sidebar.number_input(
    "Hedge Book Balance ($)",
    min_value=1000.0,
    max_value=100000.0,
    value=50000.0,
    step=1000.0,
    help="Starting balance in hedge book (set high for 'unlimited')"
)

# Simulation
st.sidebar.subheader("🔬 Simulation")
num_simulations = st.sidebar.select_slider(
    "Number of Simulations",
    options=[1000, 2500, 5000, 10000, 25000, 50000],
    value=5000,
    help="More simulations = more accurate but slower"
)

# Run button
st.sidebar.markdown("---")
run_button = st.sidebar.button("🚀 Run Simulation", type="primary", use_container_width=True)

# Main content area
if run_button:
    # Create configuration
    config = BettingConfig(
        deposit=deposit,
        bonus_percentage=bonus_pct,
        rollover_multiplier=rollover,
        rollover_lesser_of_bet_win=rollover_lesser_of_bet_win,
        min_hold=min_hold,
        max_hold=max_hold,
        target_hold=target_hold,
        min_bet_size=min_bet,
        max_bet_size=max_bet,
        max_favorite_bet=max_favorite_bet,
        min_underdog_bet=min_underdog_bet,
        num_simulations=num_simulations,
        min_promo_odds=min_promo_odds,
        max_promo_odds=max_promo_odds,
        regular_book_balance=regular_book_balance
    )

    # Run simulation with progress bar
    with st.spinner(f'Running {num_simulations:,} simulations...'):
        results = run_monte_carlo(config)

    # Calculate statistics
    net_profits = [r.net_profit for r in results]
    capital_required = [r.max_regular_balance_used for r in results]
    num_bets = [r.num_bets for r in results]

    # Exit reasons
    lost_promo = sum(1 for r in results if r.exit_reason == "lost_promo")
    rollover_met = sum(1 for r in results if r.exit_reason == "rollover_met")
    insufficient_capital = sum(1 for r in results if r.exit_reason == "insufficient_capital")

    successful_conversions = lost_promo + rollover_met
    success_rate = (successful_conversions / len(results)) * 100

    # Successful profits
    successful_profits = [r.net_profit for r in results if r.exit_reason in ["lost_promo", "rollover_met"]]
    avg_successful_profit = np.mean(successful_profits) if successful_profits else 0

    # Summary metrics
    st.header("📊 Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Success Rate",
            f"{success_rate:.1f}%",
            delta="Bonus Converted" if success_rate > 90 else None
        )

    with col2:
        st.metric(
            "Avg Profit (Success)",
            f"${avg_successful_profit:,.2f}",
            delta=f"{(avg_successful_profit/deposit)*100:.1f}% of deposit"
        )

    with col3:
        st.metric(
            "Avg Bets Needed",
            f"{np.mean(num_bets):.1f}",
            delta=f"Median: {np.median(num_bets):.0f}"
        )

    with col4:
        st.metric(
            "Capital Needed (95%)",
            f"${np.percentile(capital_required, 95):,.0f}",
            delta="Hedge Book"
        )

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["💰 Profit Analysis", "📈 Capital Requirements", "🎲 Exit Scenarios", "📊 Distributions"])

    with tab1:
        st.subheader("Profit Distribution")

        col1, col2 = st.columns([2, 1])

        with col1:
            # Profit histogram
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=net_profits,
                nbinsx=50,
                name="All Simulations",
                marker_color='lightblue'
            ))

            if successful_profits:
                fig.add_trace(go.Histogram(
                    x=successful_profits,
                    nbinsx=50,
                    name="Successful Only",
                    marker_color='green',
                    opacity=0.7
                ))

            fig.update_layout(
                title="Profit Distribution",
                xaxis_title="Net Profit ($)",
                yaxis_title="Frequency",
                barmode='overlay',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Key Statistics")
            st.metric("Average Profit", f"${np.mean(net_profits):,.2f}")
            st.metric("Median Profit", f"${np.median(net_profits):,.2f}")
            st.metric("Std Deviation", f"${np.std(net_profits):,.2f}")
            st.metric("Min Profit", f"${np.min(net_profits):,.2f}")
            st.metric("Max Profit", f"${np.max(net_profits):,.2f}")

            st.markdown("### Percentiles")
            st.write(f"5th: ${np.percentile(net_profits, 5):,.2f}")
            st.write(f"25th: ${np.percentile(net_profits, 25):,.2f}")
            st.write(f"50th: ${np.percentile(net_profits, 50):,.2f}")
            st.write(f"75th: ${np.percentile(net_profits, 75):,.2f}")
            st.write(f"95th: ${np.percentile(net_profits, 95):,.2f}")

    with tab2:
        st.subheader("Hedge Book Capital Requirements")

        col1, col2 = st.columns([2, 1])

        with col1:
            # Capital requirements histogram
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=capital_required,
                nbinsx=50,
                marker_color='purple'
            ))

            # Add percentile lines
            p95 = np.percentile(capital_required, 95)
            p99 = np.percentile(capital_required, 99)

            fig.add_vline(x=p95, line_dash="dash", line_color="red",
                         annotation_text=f"95th: ${p95:,.0f}", annotation_position="top")
            fig.add_vline(x=p99, line_dash="dash", line_color="darkred",
                         annotation_text=f"99th: ${p99:,.0f}", annotation_position="top")

            fig.update_layout(
                title="Capital Requirements Distribution",
                xaxis_title="Capital Deployed ($)",
                yaxis_title="Frequency",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Capital Needed")
            st.metric("Average", f"${np.mean(capital_required):,.2f}")
            st.metric("Median", f"${np.median(capital_required):,.2f}")

            st.markdown("### Percentiles")
            st.write(f"**75th:** ${np.percentile(capital_required, 75):,.2f}")
            st.write(f"**90th:** ${np.percentile(capital_required, 90):,.2f}")
            st.write(f"**95th:** ${np.percentile(capital_required, 95):,.2f}")
            st.write(f"**99th:** ${np.percentile(capital_required, 99):,.2f}")

            st.markdown("---")
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown(f"**💡 Recommendation**")
            st.markdown(f"Maintain **${np.percentile(capital_required, 95):,.0f}** in your hedge book for **95% success rate**")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.subheader("Exit Scenarios")

        col1, col2 = st.columns([1, 2])

        with col1:
            # Pie chart
            labels = []
            values = []
            colors = []

            if lost_promo > 0:
                labels.append(f'Lost Promo Book\n({lost_promo/len(results)*100:.1f}%)')
                values.append(lost_promo)
                colors.append('#28a745')

            if rollover_met > 0:
                labels.append(f'Rollover Met\n({rollover_met/len(results)*100:.1f}%)')
                values.append(rollover_met)
                colors.append('#007bff')

            if insufficient_capital > 0:
                labels.append(f'Insufficient Capital\n({insufficient_capital/len(results)*100:.1f}%)')
                values.append(insufficient_capital)
                colors.append('#ffc107')

            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                marker_colors=colors,
                hole=0.3
            )])

            fig.update_layout(
                title="Exit Scenario Breakdown",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Detailed Breakdown")

            # Lost Promo Book
            if lost_promo > 0:
                lost_promo_profits = [r.net_profit for r in results if r.exit_reason == "lost_promo"]
                st.markdown("#### ✅ Lost Promo Book (Success)")
                st.write(f"**Count:** {lost_promo:,} ({lost_promo/len(results)*100:.1f}%)")
                st.write(f"**Avg Profit:** ${np.mean(lost_promo_profits):,.2f}")
                st.write(f"**Outcome:** All promo funds lost in betting, won on hedge side")
                st.markdown("---")

            # Rollover Met
            if rollover_met > 0:
                rollover_met_profits = [r.net_profit for r in results if r.exit_reason == "rollover_met"]
                st.markdown("#### ✅ Rollover Met (Success)")
                st.write(f"**Count:** {rollover_met:,} ({rollover_met/len(results)*100:.1f}%)")
                st.write(f"**Avg Profit:** ${np.mean(rollover_met_profits):,.2f}")
                st.write(f"**Outcome:** Promo funds unlocked, can withdraw")
                st.markdown("---")

            # Insufficient Capital
            if insufficient_capital > 0:
                insufficient_profits = [r.net_profit for r in results if r.exit_reason == "insufficient_capital"]
                st.markdown("#### ❌ Insufficient Capital (Failed)")
                st.write(f"**Count:** {insufficient_capital:,} ({insufficient_capital/len(results)*100:.1f}%)")
                st.write(f"**Avg Profit:** ${np.mean(insufficient_profits):,.2f}")
                st.write(f"**Outcome:** Promo funds LOCKED - could not complete conversion")

    with tab4:
        st.subheader("Distribution Analysis")

        # Create DataFrame
        df = pd.DataFrame({
            'Net Profit': net_profits,
            'Capital Required': capital_required,
            'Number of Bets': num_bets,
            'Exit Reason': [r.exit_reason for r in results]
        })

        # Scatter plot: Profit vs Bets
        fig = px.scatter(
            df,
            x='Number of Bets',
            y='Net Profit',
            color='Exit Reason',
            color_discrete_map={
                'lost_promo': '#28a745',
                'rollover_met': '#007bff',
                'insufficient_capital': '#ffc107'
            },
            title='Profit vs Number of Bets',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        # Box plots
        col1, col2 = st.columns(2)

        with col1:
            fig = go.Figure()
            for reason in df['Exit Reason'].unique():
                subset = df[df['Exit Reason'] == reason]
                fig.add_trace(go.Box(
                    y=subset['Net Profit'],
                    name=reason.replace('_', ' ').title()
                ))
            fig.update_layout(title="Profit by Exit Scenario", yaxis_title="Net Profit ($)", height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = go.Figure()
            for reason in df['Exit Reason'].unique():
                subset = df[df['Exit Reason'] == reason]
                fig.add_trace(go.Box(
                    y=subset['Number of Bets'],
                    name=reason.replace('_', ' ').title()
                ))
            fig.update_layout(title="Bets Needed by Exit Scenario", yaxis_title="Number of Bets", height=400)
            st.plotly_chart(fig, use_container_width=True)

    # Download results
    st.markdown("---")
    st.subheader("📥 Export Results")

    # Create detailed results DataFrame
    export_df = pd.DataFrame({
        'Simulation': range(1, len(results) + 1),
        'Net Profit': [r.net_profit for r in results],
        'Num Bets': [r.num_bets for r in results],
        'Rollover Achieved': [r.rollover_achieved for r in results],
        'Promo Book Final': [r.promo_book_final for r in results],
        'Regular Book Final': [r.regular_book_final for r in results],
        'Exit Reason': [r.exit_reason for r in results],
        'Capital Used': [r.max_regular_balance_used for r in results],
        'Min Regular Balance': [r.min_regular_balance for r in results]
    })

    csv = export_df.to_csv(index=False)
    st.download_button(
        label="Download Results as CSV",
        data=csv,
        file_name="low_hold_betting_results.csv",
        mime="text/csv"
    )

else:
    # Welcome screen
    st.info("👈 Configure your parameters in the sidebar and click **Run Simulation** to start!")

    st.markdown("""
    ## About This Simulator

    This Monte Carlo simulator helps you analyze the **expected ROI and capital requirements**
    for converting sportsbook promotional bonuses using low hold betting strategies.

    ### How It Works

    1. **Low Hold Betting**: Place opposing bets on the same game across different sportsbooks
    2. **Two Success Paths**:
       - **Lose Promo Book**: Bonus depleted → Full conversion to cash
       - **Hit Rollover**: Wager requirement met → Unlock promo funds
    3. **Capital Requirements**: See exactly how much hedge book balance you need

    ### Key Features

    - 🎯 **Triangular hold distribution** - More realistic line shopping simulation
    - 💰 **Balanced bet sizing** - Respects favorite/underdog constraints
    - 📊 **Capital tracking** - Know your hedge book requirements
    - ✅ **True success rate** - Only counts completed conversions
    - 📈 **Interactive visualizations** - Understand your risk/reward profile

    ### Getting Started

    1. Set your **bonus structure** (deposit, match %, rollover)
    2. Configure **hold range** (0-2.5% recommended, target ~1.8%)
    3. Set **bet sizing** limits (favorite max, underdog min)
    4. Choose **number of simulations** (more = more accurate)
    5. Click **Run Simulation**!

    ---

    *Built with Claude Code*
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    Monte Carlo Low Hold Betting Simulator | Built with Streamlit
</div>
""", unsafe_allow_html=True)
