# Monte Carlo Low Hold Betting Simulator

A Monte Carlo simulator for estimating ROI on low hold betting strategies used to convert sportsbook promotional bonuses into actual money.

## Overview

Low hold betting is a strategy to convert sportsbook promotional bonus money into real money by placing opposing bets on the same game across different sportsbooks. This simulator helps you understand the expected outcomes, variance, and optimal strategies.

## How Low Hold Betting Works

1. **Deposit + Bonus**: You deposit money and receive a bonus (e.g., 100% match)
2. **Rollover Requirement**: You must wager a multiple of (deposit + bonus) before withdrawing
3. **Low Hold Bets**: Place opposing bets with minimal hold (0-3.5%) to preserve capital
4. **Exit Scenarios**:
   - Lose on promo book early → bonus converted quickly
   - Hit rollover requirement → unlock full bonus

### Hold Calculation

Hold represents the percentage of total wagered amount that is lost regardless of outcome:

```
Hold = (1/odds1_decimal + 1/odds2_decimal - 1)
```

**Example**: Bet $100 on Team A at -110 and $100 on Team B at -110
- Win either way: ~$90.91
- Total wagered: $200
- Net loss: $9.09
- Hold: 4.5%

**Lower hold = better for conversion** (typical sweet spot: 1.8%)

## Installation

```bash
pip install numpy
```

## Usage

### Basic Usage

```bash
python monte_carlo_betting_simulator.py
```

This runs with default parameters:
- $1,000 deposit
- 100% bonus match
- 10x rollover
- 0-3.5% hold range
- $500-$1,500 bet sizes
- 10,000 simulations

### Custom Parameters

```bash
python monte_carlo_betting_simulator.py \
  --deposit 1000 \
  --bonus-pct 100 \
  --rollover 10 \
  --min-hold 0.0 \
  --max-hold 0.018 \
  --min-bet 500 \
  --max-bet 1500 \
  --simulations 5000
```

### All Available Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--deposit` | Initial deposit amount | 1000 |
| `--bonus-pct` | Bonus percentage (100 = 100% match) | 100 |
| `--rollover` | Rollover multiplier | 10 |
| `--min-hold` | Minimum hold percentage (0.0 = 0%) | 0.0 |
| `--max-hold` | Maximum hold percentage (0.035 = 3.5%) | 0.035 |
| `--min-bet` | Minimum bet size | 500 |
| `--max-bet` | Maximum bet size | 1500 |
| `--simulations` | Number of Monte Carlo simulations | 10000 |
| `--min-promo-odds` | Min promo book odds (American) | -200 |
| `--max-promo-odds` | Max promo book odds (American) | 450 |

## Example Scenarios

### Scenario 1: Conservative Strategy (Higher Hold)

```bash
python monte_carlo_betting_simulator.py \
  --deposit 500 \
  --bonus-pct 100 \
  --rollover 10 \
  --max-hold 0.035 \
  --simulations 5000
```

**Expected Results**:
- Lower ROI (~15-20%)
- Fewer bets needed (1-3 bets avg)
- Higher chance of losing promo book early
- Faster conversion

### Scenario 2: Optimal Strategy (Sweet Spot ~1.8% Hold)

```bash
python monte_carlo_betting_simulator.py \
  --deposit 1000 \
  --bonus-pct 100 \
  --rollover 10 \
  --max-hold 0.018 \
  --simulations 5000
```

**Expected Results**:
- Higher ROI (~30-35%)
- More bets needed (10-20 bets avg)
- Higher chance of hitting rollover
- Best risk/reward balance

### Scenario 3: Aggressive Strategy (Very Low Hold)

```bash
python monte_carlo_betting_simulator.py \
  --deposit 1000 \
  --bonus-pct 100 \
  --rollover 10 \
  --max-hold 0.010 \
  --simulations 5000
```

**Expected Results**:
- Highest ROI (35-40%+)
- Many bets needed (20-30+ bets)
- Very high chance of hitting rollover
- Requires finding many low hold opportunities

## Understanding the Output

### Configuration Section
Shows your input parameters and calculated rollover requirement.

### Profit/Loss Statistics
- **Average Net Profit**: Expected profit across all simulations
- **Median Net Profit**: Middle value (50th percentile)
- **Standard Deviation**: Measure of variance/risk
- **Min/Max Profit**: Range of outcomes

### ROI Analysis
- **Average ROI**: Expected return on initial capital (deposit × 2)
- Shows what percentage return you can expect

### Percentile Distribution
Shows profit at different confidence levels:
- **5th Percentile**: Worst-case scenario (you'll do better 95% of time)
- **25th Percentile**: Below-average outcome
- **50th Percentile**: Median (typical outcome)
- **75th Percentile**: Above-average outcome
- **95th Percentile**: Best-case scenario

### Exit Scenarios
- **Lost Promo Book**: % of simulations where you lost promo funds early
- **Rollover Met**: % of simulations where you hit the rollover requirement

### Betting Statistics
- **Average/Median Bets**: How many bets you'll likely need
- **Min/Max Bets**: Range of bets needed across simulations

## Strategy Tips

1. **Find the Sweet Spot**: Around 1.8% hold offers best ROI while being achievable
2. **Lower Hold = Higher ROI**: But requires more betting opportunities
3. **Variance Matters**: Check standard deviation to understand risk
4. **Promo Book Position**: Ideally place bonus funds on underdog (+odds) side
5. **Bankroll Management**: Keep enough in regular book to hedge all promo bets
6. **Rollover Tracking**: Know your requirement and track progress

## Real-World Application

Use this simulator to:
1. **Evaluate Offers**: Compare different bonus structures
2. **Plan Strategy**: Determine optimal hold range for your situation
3. **Manage Risk**: Understand variance and worst-case scenarios
4. **Set Expectations**: Know how many bets you'll likely need
5. **Bankroll Planning**: Ensure adequate funds in regular book

## Assumptions & Limitations

- Assumes you can consistently find bets at your target hold range
- Assumes 50/50 probability on each bet (fair odds)
- Does not account for:
  - Line movement
  - Bet limits
  - Account restrictions
  - Timing between finding opportunities
  - Actual availability of low hold lines
- Simplified bet sizing model
- Does not model worst-case scenarios like account closure

## Tips for Success

1. **Use Multiple Sportsbooks**: More options = more low hold opportunities
2. **Line Shopping Tools**: Use odds comparison sites to find low holds
3. **Timing**: Be ready to place bets quickly when low holds appear
4. **Bankroll**: Maintain adequate balance in regular book
5. **Track Everything**: Keep detailed records of all bets
6. **Understand Terms**: Read all bonus terms carefully

## Example Output Interpretation

```
Average ROI: 33.56%
Lost Promo Book: 41.8%
Rollover Met: 58.2%
Average Bets Needed: 13.5
```

**Interpretation**:
- Expect ~33% return on capital
- 42% chance of quick conversion (lose promo early)
- 58% chance of hitting rollover
- Need to find ~13-14 good low hold opportunities
- Total capital at risk: deposit × 2
- Expected profit: deposit × 0.67 (67% of deposit as profit)

## Questions?

The simulator is designed to be flexible. Experiment with different parameters to match your specific situation and risk tolerance.
