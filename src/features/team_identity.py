"""
Team offensive identity calculation.

Calculates rolling team pass rates to classify teams as
pass-heavy, balanced, or run-heavy.
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple


def calculate_team_pass_rate(
    pbp_df: pd.DataFrame,
    window_games: int = 4
) -> pd.DataFrame:
    """
    Calculate rolling pass rate for each team.

    Uses a rolling window of recent games to capture each team's
    offensive identity at the time of each play.

    Args:
        pbp_df: Play-by-play DataFrame with columns:
            - game_id: Unique game identifier
            - posteam: Team with possession
            - play_type: 'pass' or 'run'
            - season: Year
        window_games: Number of recent games to use (default: 4)

    Returns:
        DataFrame with columns:
            - game_id: Game identifier
            - posteam: Team
            - team_pass_rate: Rolling pass rate (0.0 to 1.0)
            - team_identity: Classification ('pass_heavy', 'balanced', 'run_heavy')
    """
    # Filter to only pass and run plays
    plays = pbp_df[pbp_df['play_type'].isin(['pass', 'run'])].copy()

    # Create binary pass indicator
    plays['is_pass'] = (plays['play_type'] == 'pass').astype(int)

    # Calculate pass rate per game per team
    game_stats = plays.groupby(['season', 'game_id', 'posteam']).agg({
        'is_pass': ['sum', 'count']
    }).reset_index()

    game_stats.columns = ['season', 'game_id', 'posteam', 'passes', 'total_plays']
    game_stats['game_pass_rate'] = game_stats['passes'] / game_stats['total_plays']

    # Sort by season and game_id to maintain chronological order
    game_stats = game_stats.sort_values(['season', 'game_id'])

    # Calculate rolling pass rate for each team
    team_pass_rates = []

    for team in game_stats['posteam'].unique():
        team_games = game_stats[game_stats['posteam'] == team].copy()

        # Calculate rolling window
        # For first few games of season, use expanding window
        rolling_passes = team_games['passes'].rolling(
            window=window_games, min_periods=1
        ).sum()
        rolling_total = team_games['total_plays'].rolling(
            window=window_games, min_periods=1
        ).sum()

        team_games['rolling_pass_rate'] = rolling_passes / rolling_total
        team_pass_rates.append(team_games)

    team_pass_rates_df = pd.concat(team_pass_rates, ignore_index=True)

    # Classify team identity based on pass rate
    team_pass_rates_df['team_identity'] = team_pass_rates_df['rolling_pass_rate'].apply(
        get_team_identity_context
    )

    # Create result with only needed columns
    result = team_pass_rates_df[[
        'game_id', 'posteam', 'rolling_pass_rate', 'team_identity'
    ]].rename(columns={'rolling_pass_rate': 'team_pass_rate'})

    return result


def get_team_identity_context(pass_rate: float) -> str:
    """
    Classify team offensive identity based on pass rate.

    Thresholds based on NFL averages (~55% pass league-wide):
    - Pass-heavy: Teams that pass significantly more (Chiefs, Dolphins)
    - Run-heavy: Teams that run significantly more (Ravens, Browns)
    - Balanced: Teams near league average

    Args:
        pass_rate: Team's pass rate (0.0 to 1.0)

    Returns:
        String: 'pass_heavy', 'balanced', or 'run_heavy'
    """
    if pd.isna(pass_rate):
        return "balanced"  # Default for missing data

    if pass_rate >= 0.60:
        return "pass_heavy"
    elif pass_rate <= 0.45:
        return "run_heavy"
    else:
        return "balanced"


def add_team_identity_to_plays(
    pbp_df: pd.DataFrame,
    window_games: int = 4
) -> pd.DataFrame:
    """
    Add team identity columns to play-by-play data.

    Convenience function that calculates team pass rates and merges
    them back to the original play-by-play DataFrame.

    Args:
        pbp_df: Play-by-play DataFrame
        window_games: Number of games for rolling window

    Returns:
        Original DataFrame with added columns:
            - team_pass_rate: Rolling pass rate for posteam
            - team_identity: Classification string
    """
    # Calculate team identities
    team_stats = calculate_team_pass_rate(pbp_df, window_games)

    # Merge back to plays
    result = pbp_df.merge(
        team_stats,
        on=['game_id', 'posteam'],
        how='left'
    )

    # Fill missing values with league average (balanced)
    result = result.copy()
    result['team_pass_rate'] = result['team_pass_rate'].fillna(0.55)
    result['team_identity'] = result['team_identity'].fillna('balanced')

    return result
