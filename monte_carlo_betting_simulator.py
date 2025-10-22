#!/usr/bin/env python3
"""
Monte Carlo Simulator for Low Hold Betting Strategy

This simulator estimates ROI on converting sportsbook promotional bonuses
through low hold betting strategies.
"""

import random
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple
import argparse


@dataclass
class BettingConfig:
    """Configuration for the betting simulation"""
    deposit: float
    bonus_percentage: float  # e.g., 100 for 100% match
    rollover_multiplier: float  # e.g., 10 for 10x rollover
    min_hold: float  # e.g., 0.0 for 0%
    max_hold: float  # e.g., 0.035 for 3.5%
    min_bet_size: float
    max_bet_size: float
    num_simulations: int
    min_promo_odds: int  # e.g., -200
    max_promo_odds: int  # e.g., 450
    regular_book_balance: float  # Starting balance in regular (hedge) book


@dataclass
class SimulationResult:
    """Results from a single simulation run"""
    net_profit: float
    num_bets: int
    rollover_achieved: float
    promo_book_final: float
    regular_book_final: float
    exit_reason: str  # 'lost_promo' or 'rollover_met'


def american_to_decimal(american_odds: int) -> float:
    """Convert American odds to decimal odds"""
    if american_odds > 0:
        return (american_odds / 100) + 1
    else:
        return (100 / abs(american_odds)) + 1


def decimal_to_american(decimal_odds: float) -> int:
    """Convert decimal odds to American odds"""
    if decimal_odds >= 2.0:
        return int((decimal_odds - 1) * 100)
    else:
        return int(-100 / (decimal_odds - 1))


def calculate_hold(odds1_american: int, odds2_american: int) -> float:
    """
    Calculate the hold percentage for a pair of opposing bets

    Hold = (1/odds1_decimal + 1/odds2_decimal - 1)

    This represents the percentage of total wagered amount that is lost
    regardless of outcome.
    """
    odds1_decimal = american_to_decimal(odds1_american)
    odds2_decimal = american_to_decimal(odds2_american)

    hold = (1 / odds1_decimal + 1 / odds2_decimal - 1)
    return hold


def find_opposing_odds(promo_odds_american: int, target_hold: float) -> int:
    """
    Given promo book odds and target hold, calculate the required opposing odds

    From hold formula: hold = 1/p + 1/o - 1
    Solving for o: o = 1 / (hold + 1 - 1/p)
    """
    promo_decimal = american_to_decimal(promo_odds_american)
    opposing_decimal = 1 / (target_hold + 1 - 1/promo_decimal)

    return decimal_to_american(opposing_decimal)


def calculate_bet_outcome(promo_bet: float, promo_odds: int,
                         regular_bet: float, regular_odds: int,
                         promo_wins: bool) -> Tuple[float, float]:
    """
    Calculate the outcome of a bet pair

    Returns: (promo_book_change, regular_book_change)
    """
    promo_decimal = american_to_decimal(promo_odds)
    regular_decimal = american_to_decimal(regular_odds)

    if promo_wins:
        # Win on promo book, lose on regular book
        promo_change = promo_bet * (promo_decimal - 1)  # Net profit (excluding stake)
        regular_change = -regular_bet
    else:
        # Lose on promo book, win on regular book
        promo_change = -promo_bet
        regular_change = regular_bet * (regular_decimal - 1)  # Net profit (excluding stake)

    return promo_change, regular_change


def generate_bet_scenario(config: BettingConfig, promo_balance: float) -> Tuple[float, int, int, float]:
    """
    Generate a random bet scenario with hold, odds, and bet sizes

    Returns: (bet_size, promo_odds, regular_odds, hold)
    """
    # Generate promo odds (underdog/plus odds preferred)
    # Avoid odds between -100 and +100 (American odds don't include this range)
    promo_odds = random.randint(config.min_promo_odds, config.max_promo_odds)
    # Skip invalid odds near 0
    while -100 <= promo_odds <= 100:
        promo_odds = random.randint(config.min_promo_odds, config.max_promo_odds)

    # Generate target hold
    target_hold = random.uniform(config.min_hold, config.max_hold)

    # Calculate opposing odds to achieve target hold
    regular_odds = find_opposing_odds(promo_odds, target_hold)

    # Actual hold (may differ slightly due to rounding)
    actual_hold = calculate_hold(promo_odds, regular_odds)

    # Determine bet size (larger bets for lower holds)
    # Inverse relationship: lower hold = larger bet
    hold_factor = 1 - (actual_hold / config.max_hold)
    bet_range = config.max_bet_size - config.min_bet_size
    bet_size = config.min_bet_size + (bet_range * hold_factor)

    # Add some randomness
    bet_size *= random.uniform(0.8, 1.2)

    # Cap at promo balance
    bet_size = min(bet_size, promo_balance * 0.95)

    # Ensure minimum bet
    bet_size = max(bet_size, config.min_bet_size)

    return bet_size, promo_odds, regular_odds, actual_hold


def run_single_simulation(config: BettingConfig) -> SimulationResult:
    """Run a single simulation of the betting strategy"""
    # Initial balances
    promo_balance = config.deposit + (config.deposit * config.bonus_percentage / 100)
    regular_balance = config.regular_book_balance

    # Rollover requirement
    rollover_required = (config.deposit + config.deposit * config.bonus_percentage / 100) * config.rollover_multiplier
    rollover_achieved = 0.0

    num_bets = 0
    exit_reason = ""

    # Continue betting until exit condition met
    while True:
        num_bets += 1

        # Generate bet scenario
        promo_bet, promo_odds, regular_odds, hold = generate_bet_scenario(config, promo_balance)

        # Calculate opposing bet size to balance the action
        # We want to minimize variance, so we size the regular bet to create a hedge
        promo_decimal = american_to_decimal(promo_odds)
        regular_decimal = american_to_decimal(regular_odds)

        # Calculate required regular bet for full hedge
        required_regular_bet = (promo_bet * promo_decimal) / regular_decimal

        # If we can't afford the full hedge, reduce promo bet size
        if required_regular_bet > regular_balance:
            # Calculate max promo bet we can afford to hedge
            max_affordable_promo_bet = (regular_balance * regular_decimal) / promo_decimal
            promo_bet = min(promo_bet, max_affordable_promo_bet * 0.95)  # 95% for safety margin

            # Recalculate regular bet with reduced promo bet
            required_regular_bet = (promo_bet * promo_decimal) / regular_decimal

            # Double-check we can still place the bet
            if promo_bet < config.min_bet_size or required_regular_bet > regular_balance:
                # Can't place minimum bet with proper hedge
                exit_reason = "insufficient_capital"
                break

        regular_bet = required_regular_bet

        # Simulate outcome (50/50 chance for each side)
        promo_wins = random.random() < 0.5

        # Calculate outcome
        promo_change, regular_change = calculate_bet_outcome(
            promo_bet, promo_odds, regular_bet, regular_odds, promo_wins
        )

        # Update balances
        promo_balance += promo_change
        regular_balance += regular_change

        # Update rollover
        rollover_achieved += promo_bet

        # Check exit conditions
        if promo_balance < config.min_bet_size:
            # Lost on promo book (bonus depleted)
            exit_reason = "lost_promo"
            break

        if rollover_achieved >= rollover_required:
            # Rollover requirement met
            exit_reason = "rollover_met"
            break

        # Safety check: prevent infinite loops
        if num_bets > 10000:
            exit_reason = "max_bets_exceeded"
            break

    # Calculate net profit (total across both books minus initial capital)
    total_final = promo_balance + regular_balance
    initial_capital = config.deposit + config.regular_book_balance
    net_profit = total_final - initial_capital

    return SimulationResult(
        net_profit=net_profit,
        num_bets=num_bets,
        rollover_achieved=rollover_achieved,
        promo_book_final=promo_balance,
        regular_book_final=regular_balance,
        exit_reason=exit_reason
    )


def run_monte_carlo(config: BettingConfig) -> List[SimulationResult]:
    """Run multiple simulations and return results"""
    results = []

    for i in range(config.num_simulations):
        if (i + 1) % 1000 == 0:
            print(f"Running simulation {i + 1}/{config.num_simulations}...")

        result = run_single_simulation(config)
        results.append(result)

    return results


def analyze_results(results: List[SimulationResult], config: BettingConfig):
    """Analyze and display simulation results"""
    net_profits = [r.net_profit for r in results]
    num_bets = [r.num_bets for r in results]

    # Calculate statistics
    avg_profit = np.mean(net_profits)
    median_profit = np.median(net_profits)
    std_profit = np.std(net_profits)
    min_profit = np.min(net_profits)
    max_profit = np.max(net_profits)

    # ROI calculation
    initial_capital = config.deposit + config.regular_book_balance
    avg_roi = (avg_profit / initial_capital) * 100

    # Exit reasons and profit breakdown
    lost_promo = sum(1 for r in results if r.exit_reason == "lost_promo")
    rollover_met = sum(1 for r in results if r.exit_reason == "rollover_met")
    insufficient_capital = sum(1 for r in results if r.exit_reason == "insufficient_capital")

    # Profit by exit scenario
    lost_promo_profits = [r.net_profit for r in results if r.exit_reason == "lost_promo"]
    rollover_met_profits = [r.net_profit for r in results if r.exit_reason == "rollover_met"]
    insufficient_capital_profits = [r.net_profit for r in results if r.exit_reason == "insufficient_capital"]

    avg_profit_lost_promo = np.mean(lost_promo_profits) if lost_promo_profits else 0
    avg_profit_rollover = np.mean(rollover_met_profits) if rollover_met_profits else 0
    avg_profit_insufficient_capital = np.mean(insufficient_capital_profits) if insufficient_capital_profits else 0

    # Betting statistics
    avg_bets = np.mean(num_bets)
    median_bets = np.median(num_bets)

    # Percentiles
    p5 = np.percentile(net_profits, 5)
    p25 = np.percentile(net_profits, 25)
    p75 = np.percentile(net_profits, 75)
    p95 = np.percentile(net_profits, 95)

    # Print results
    print("\n" + "="*70)
    print("MONTE CARLO SIMULATION RESULTS - LOW HOLD BETTING STRATEGY")
    print("="*70)

    print("\n📊 CONFIGURATION:")
    print(f"  Promo Book Deposit:     ${config.deposit:,.2f}")
    print(f"  Bonus:                  {config.bonus_percentage}% (${config.deposit * config.bonus_percentage / 100:,.2f})")
    print(f"  Regular Book Balance:   ${config.regular_book_balance:,.2f}")
    print(f"  Total Initial Capital:  ${config.deposit + config.regular_book_balance:,.2f}")
    print(f"  Rollover Requirement:   {config.rollover_multiplier}x (${(config.deposit + config.deposit * config.bonus_percentage / 100) * config.rollover_multiplier:,.2f})")
    print(f"  Hold Range:             {config.min_hold*100:.2f}% - {config.max_hold*100:.2f}%")
    print(f"  Bet Size Range:         ${config.min_bet_size:,.2f} - ${config.max_bet_size:,.2f}")
    print(f"  Promo Odds Range:       {config.min_promo_odds:+d} to {config.max_promo_odds:+d}")
    print(f"  Simulations:            {config.num_simulations:,}")

    print("\n💰 PROFIT/LOSS STATISTICS:")
    print(f"  Average Net Profit:     ${avg_profit:,.2f}")
    print(f"  Median Net Profit:      ${median_profit:,.2f}")
    print(f"  Standard Deviation:     ${std_profit:,.2f}")
    print(f"  Minimum Profit:         ${min_profit:,.2f}")
    print(f"  Maximum Profit:         ${max_profit:,.2f}")

    print("\n📈 ROI ANALYSIS:")
    print(f"  Average ROI:            {avg_roi:.2f}%")
    print(f"  Initial Capital:        ${initial_capital:,.2f}")

    print("\n📉 PERCENTILE DISTRIBUTION:")
    print(f"  5th Percentile:         ${p5:,.2f}")
    print(f"  25th Percentile:        ${p25:,.2f}")
    print(f"  50th Percentile:        ${median_profit:,.2f}")
    print(f"  75th Percentile:        ${p75:,.2f}")
    print(f"  95th Percentile:        ${p95:,.2f}")

    print("\n🎲 EXIT SCENARIOS:")
    print(f"  Lost Promo Book:        {lost_promo:,} ({lost_promo/len(results)*100:.1f}%)")
    if lost_promo > 0:
        print(f"    → Avg Profit:         ${avg_profit_lost_promo:,.2f}")
    print(f"  Rollover Met:           {rollover_met:,} ({rollover_met/len(results)*100:.1f}%)")
    if rollover_met > 0:
        print(f"    → Avg Profit:         ${avg_profit_rollover:,.2f}")
    if insufficient_capital > 0:
        print(f"  Insufficient Capital:   {insufficient_capital:,} ({insufficient_capital/len(results)*100:.1f}%)")
        print(f"    → Avg Profit:         ${avg_profit_insufficient_capital:,.2f}")

    print("\n🎯 BETTING STATISTICS:")
    print(f"  Average Bets Needed:    {avg_bets:.1f}")
    print(f"  Median Bets Needed:     {median_bets:.0f}")
    print(f"  Min Bets:               {min(num_bets)}")
    print(f"  Max Bets:               {max(num_bets)}")

    print("\n" + "="*70)


def main():
    """Main entry point for the simulator"""
    parser = argparse.ArgumentParser(
        description="Monte Carlo Simulator for Low Hold Betting Strategy"
    )

    parser.add_argument("--deposit", type=float, default=1000.0,
                       help="Initial deposit amount (default: 1000)")
    parser.add_argument("--bonus-pct", type=float, default=100.0,
                       help="Bonus percentage (default: 100 for 100%% match)")
    parser.add_argument("--rollover", type=float, default=10.0,
                       help="Rollover multiplier (default: 10 for 10x)")
    parser.add_argument("--min-hold", type=float, default=0.0,
                       help="Minimum hold percentage (default: 0.0)")
    parser.add_argument("--max-hold", type=float, default=0.035,
                       help="Maximum hold percentage (default: 0.035 for 3.5%%)")
    parser.add_argument("--min-bet", type=float, default=500.0,
                       help="Minimum bet size (default: 500)")
    parser.add_argument("--max-bet", type=float, default=1500.0,
                       help="Maximum bet size (default: 1500)")
    parser.add_argument("--simulations", type=int, default=10000,
                       help="Number of simulations to run (default: 10000)")
    parser.add_argument("--min-promo-odds", type=int, default=-200,
                       help="Minimum promo book odds in American format (default: -200)")
    parser.add_argument("--max-promo-odds", type=int, default=450,
                       help="Maximum promo book odds in American format (default: 450)")
    parser.add_argument("--regular-book-balance", type=float, default=1000.0,
                       help="Starting balance in regular (hedge) book (default: 1000)")

    args = parser.parse_args()

    # Create configuration
    config = BettingConfig(
        deposit=args.deposit,
        bonus_percentage=args.bonus_pct,
        rollover_multiplier=args.rollover,
        min_hold=args.min_hold,
        max_hold=args.max_hold,
        min_bet_size=args.min_bet,
        max_bet_size=args.max_bet,
        num_simulations=args.simulations,
        min_promo_odds=args.min_promo_odds,
        max_promo_odds=args.max_promo_odds,
        regular_book_balance=args.regular_book_balance
    )

    print("Starting Monte Carlo simulation...")
    print(f"This may take a moment for {config.num_simulations:,} simulations...\n")

    # Run simulations
    results = run_monte_carlo(config)

    # Analyze and display results
    analyze_results(results, config)


if __name__ == "__main__":
    main()
