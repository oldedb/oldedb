# Streamlit App - Low Hold Betting Simulator

Interactive web interface for the Monte Carlo Low Hold Betting Simulator.

## Quick Start

### Run Locally

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

### Using the App

1. **Configure Parameters** in the left sidebar:
   - Bonus structure (deposit, match %, rollover)
   - Hold range (min, max, target)
   - Bet sizing (min/max, favorite/underdog limits)
   - Odds range
   - Hedge book balance
   - Number of simulations

2. **Click "Run Simulation"** to start the Monte Carlo analysis

3. **Explore Results** across 4 tabs:
   - **Profit Analysis**: Distribution and statistics
   - **Capital Requirements**: How much hedge book balance you need
   - **Exit Scenarios**: Breakdown of success paths
   - **Distributions**: Detailed charts and correlations

4. **Download Results** as CSV for further analysis

## Features

### Interactive Controls
- Sliders for easy parameter adjustment
- Real-time validation
- Tooltips with helpful explanations

### Visualizations
- Profit distribution histograms
- Capital requirements with percentile markers
- Exit scenario pie charts
- Scatter plots showing bet count vs profit
- Box plots by exit scenario

### Key Metrics
- **Success Rate**: % achieving either goal (Lost Promo OR Rollover Met)
- **Average Profit**: Expected profit for successful conversions
- **Capital Needed**: 95th/99th percentile hedge book requirements
- **Average Bets**: Expected number of betting opportunities needed

### Export
- Download full simulation results as CSV
- Includes all metrics for each simulation run

## Tips for Best Results

1. **Start with defaults** and adjust from there
2. **Use 5,000+ simulations** for stable results (10,000+ recommended)
3. **Set hedge book balance high** ($50k+) to see true capital requirements
4. **Target hold ~1.8%** for optimal risk/reward balance
5. **Compare scenarios** by adjusting one variable at a time

## Requirements

```bash
pip install streamlit plotly numpy pandas
```

## Command-Line Alternative

If you prefer command-line:

```bash
python monte_carlo_betting_simulator.py \
  --deposit 1000 \
  --bonus-pct 100 \
  --rollover 10 \
  --max-hold 0.025 \
  --target-hold 0.018 \
  --simulations 5000
```

## Troubleshooting

### Port Already in Use
```bash
streamlit run app.py --server.port 8502
```

### Browser Doesn't Open
Navigate manually to: `http://localhost:8501`

### Slow Performance
- Reduce number of simulations
- Close other browser tabs
- Use command-line version for very large simulations (50k+)

## Architecture

```
app.py                              # Streamlit web interface
monte_carlo_betting_simulator.py   # Core simulation engine
```

The app imports the simulation functions directly, ensuring consistency between web and CLI interfaces.
