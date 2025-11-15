"""
Situation grouping logic for the corrected model architecture.

Separates game situations from play types to avoid conflating
play-calling decisions with game outcomes.
"""
from enum import Enum
from typing import Dict, Any, Union


class SituationGroup(Enum):
    """Broad situation categories for grouping plays."""

    # Early downs with manageable distance
    EARLY_DOWN_SHORT = "early_down_short"      # 1st/2nd down, 1-3 yards
    EARLY_DOWN_MEDIUM = "early_down_medium"    # 1st/2nd down, 4-7 yards
    EARLY_DOWN_LONG = "early_down_long"        # 1st/2nd down, 8+ yards

    # Third down situations
    THIRD_SHORT = "third_short"                # 3rd down, 1-3 yards
    THIRD_MEDIUM = "third_medium"              # 3rd down, 4-7 yards
    THIRD_LONG = "third_long"                  # 3rd down, 8+ yards

    # Fourth down
    FOURTH_DOWN = "fourth_down"                # Any 4th down situation

    # Field position modifiers (combined with above)
    RED_ZONE = "red_zone"                      # Inside opponent 20
    GOAL_LINE = "goal_line"                    # Inside opponent 5

    # Special
    OTHER = "other"


def get_score_context(score_differential: float) -> str:
    """
    Classify score context into categories.

    Args:
        score_differential: Points ahead (positive) or behind (negative)

    Returns:
        String: 'trailing', 'tied', or 'leading'
    """
    if score_differential <= -7:
        return "trailing"
    elif score_differential >= 7:
        return "leading"
    else:
        return "tied"


def get_situation_group(down: int, ydstogo: int, yardline_100: int) -> SituationGroup:
    """
    Classify a game situation into a broad group.

    Args:
        down: Down number (1-4)
        ydstogo: Yards to go for first down
        yardline_100: Yards from opponent's goal line (0-100)

    Returns:
        SituationGroup enum value
    """
    # Goal line situations (inside 5 yards)
    if yardline_100 <= 5:
        return SituationGroup.GOAL_LINE

    # Red zone (inside 20 yards)
    if yardline_100 <= 20:
        return SituationGroup.RED_ZONE

    # Fourth down (relatively rare, keep together)
    if down == 4:
        return SituationGroup.FOURTH_DOWN

    # Third down (most predictable, split by distance)
    if down == 3:
        if ydstogo <= 3:
            return SituationGroup.THIRD_SHORT
        elif ydstogo <= 7:
            return SituationGroup.THIRD_MEDIUM
        else:
            return SituationGroup.THIRD_LONG

    # Early downs (1st and 2nd)
    if down in [1, 2]:
        if ydstogo <= 3:
            return SituationGroup.EARLY_DOWN_SHORT
        elif ydstogo <= 7:
            return SituationGroup.EARLY_DOWN_MEDIUM
        else:
            return SituationGroup.EARLY_DOWN_LONG

    return SituationGroup.OTHER


def get_score_aware_situation(
    down: int,
    ydstogo: int,
    yardline_100: int,
    score_differential: float
) -> str:
    """
    Get situation group that includes score context.

    Args:
        down: Down number (1-4)
        ydstogo: Yards to go for first down
        yardline_100: Yards from opponent's goal line (0-100)
        score_differential: Points ahead (positive) or behind (negative)

    Returns:
        String combining base situation and score context
        Example: "third_short_trailing"
    """
    base_situation = get_situation_group(down, ydstogo, yardline_100)
    score_context = get_score_context(score_differential)

    return f"{base_situation.value}_{score_context}"


def get_team_identity_context(pass_rate: float) -> str:
    """
    Classify team offensive identity based on pass rate.

    Args:
        pass_rate: Team's pass rate (0.0 to 1.0)

    Returns:
        String: 'pass_heavy', 'balanced', or 'run_heavy'
    """
    if pass_rate >= 0.60:
        return "pass_heavy"
    elif pass_rate <= 0.45:
        return "run_heavy"
    else:
        return "balanced"


def get_team_identity_situation(
    down: int,
    ydstogo: int,
    yardline_100: int,
    team_pass_rate: float
) -> str:
    """
    Get situation group that includes team offensive identity.

    Args:
        down: Down number (1-4)
        ydstogo: Yards to go for first down
        yardline_100: Yards from opponent's goal line (0-100)
        team_pass_rate: Team's pass rate (0.0-1.0)

    Returns:
        String combining base situation and team identity
        Example: "third_short_pass_heavy"
    """
    base_situation = get_situation_group(down, ydstogo, yardline_100)
    identity_context = get_team_identity_context(team_pass_rate)

    return f"{base_situation.value}_{identity_context}"


def get_combined_situation(
    down: int,
    ydstogo: int,
    yardline_100: int,
    score_differential: float,
    team_pass_rate: float
) -> str:
    """
    Get situation group with both score and team identity.

    Creates most granular situation groups by combining:
    - Base situation (9 types)
    - Score context (3 types: trailing/tied/leading)
    - Team identity (3 types: pass_heavy/balanced/run_heavy)
    = 81 total situation groups

    Args:
        down: Down number (1-4)
        ydstogo: Yards to go for first down
        yardline_100: Yards from opponent's goal line (0-100)
        score_differential: Points ahead (positive) or behind (negative)
        team_pass_rate: Team's pass rate (0.0-1.0)

    Returns:
        String combining all three dimensions
        Example: "third_short_trailing_pass_heavy"
    """
    base_situation = get_situation_group(down, ydstogo, yardline_100)
    score_context = get_score_context(score_differential)
    identity_context = get_team_identity_context(team_pass_rate)

    return f"{base_situation.value}_{score_context}_{identity_context}"


def get_time_context(game_seconds_remaining: float) -> str:
    """
    Classify time remaining context.

    Args:
        game_seconds_remaining: Seconds remaining in the game

    Returns:
        String: 'two_minute' or 'normal'
    """
    if game_seconds_remaining <= 120:  # 2 minutes or less
        return "two_minute"
    else:
        return "normal"


def get_home_away_context(posteam_type: str) -> str:
    """
    Get home/away context.

    Args:
        posteam_type: 'home' or 'away'

    Returns:
        String: 'home' or 'away'
    """
    # Normalize to lowercase
    return posteam_type.lower()


def get_phase1_situation(
    down: int,
    ydstogo: int,
    yardline_100: int,
    game_seconds_remaining: float,
    posteam_type: str
) -> str:
    """
    Get situation group with time remaining and home/away context.

    Creates situation groups by combining:
    - Base situation (9 types)
    - Time context (2 types: normal/two_minute)
    - Home/Away (2 types: home/away)
    = 36 total situation groups

    Args:
        down: Down number (1-4)
        ydstogo: Yards to go for first down
        yardline_100: Yards from opponent's goal line (0-100)
        game_seconds_remaining: Seconds remaining in game
        posteam_type: 'home' or 'away'

    Returns:
        String combining all three dimensions
        Example: "third_short_two_minute_away"
    """
    base_situation = get_situation_group(down, ydstogo, yardline_100)
    time_context = get_time_context(game_seconds_remaining)
    home_away = get_home_away_context(posteam_type)

    return f"{base_situation.value}_{time_context}_{home_away}"


def get_situation_description(group: Union[SituationGroup, str]) -> str:
    """
    Get human-readable description of a situation group.

    Args:
        group: SituationGroup enum or string (for score-aware/team-aware groups)

    Returns:
        Human-readable description
    """
    # Handle combined situation strings (score + team identity)
    if isinstance(group, str):
        # Try to parse team identity suffix
        for team_context in ['_pass_heavy', '_balanced', '_run_heavy']:
            if group.endswith(team_context):
                base_with_score = group[:-len(team_context)]
                team_desc = team_context[1:].replace('_', ' ').title()

                # Check if it also has score context
                for score_context in ['_trailing', '_tied', '_leading']:
                    if base_with_score.endswith(score_context):
                        base_group_str = base_with_score[:-len(score_context)]
                        score_desc = score_context[1:].capitalize()

                        # Try to find the base group
                        for sg in SituationGroup:
                            if sg.value == base_group_str:
                                base_desc = get_situation_description(sg)
                                return f"{base_desc}, {score_desc}, {team_desc}"

                        # If not found in enum, return cleaned version
                        return f"{base_group_str.replace('_', ' ').title()}, {score_desc}, {team_desc}"

                # No score context, just team identity
                for sg in SituationGroup:
                    if sg.value == base_with_score:
                        base_desc = get_situation_description(sg)
                        return f"{base_desc}, {team_desc}"

                return f"{base_with_score.replace('_', ' ').title()}, {team_desc}"

        # Check if it has only score context (no team identity)
        for score_context in ['_trailing', '_tied', '_leading']:
            if group.endswith(score_context):
                base_group_str = group[:-len(score_context)]
                score_desc = score_context[1:].capitalize()

                # Try to find the base group
                for sg in SituationGroup:
                    if sg.value == base_group_str:
                        base_desc = get_situation_description(sg)
                        return f"{base_desc}, {score_desc}"

                # If not found in enum, just return cleaned up version
                return f"{base_group_str.replace('_', ' ').title()}, {score_desc}"

        # No score or team context, just return cleaned string
        return group.replace('_', ' ').title()

    # Handle enum groups
    descriptions = {
        SituationGroup.EARLY_DOWN_SHORT: "Early down, short yardage (1-3 yards)",
        SituationGroup.EARLY_DOWN_MEDIUM: "Early down, medium yardage (4-7 yards)",
        SituationGroup.EARLY_DOWN_LONG: "Early down, long yardage (8+ yards)",
        SituationGroup.THIRD_SHORT: "3rd down, short yardage (1-3 yards)",
        SituationGroup.THIRD_MEDIUM: "3rd down, medium yardage (4-7 yards)",
        SituationGroup.THIRD_LONG: "3rd down, long yardage (8+ yards)",
        SituationGroup.FOURTH_DOWN: "4th down (any distance)",
        SituationGroup.RED_ZONE: "Red zone (inside opponent 20)",
        SituationGroup.GOAL_LINE: "Goal line (inside opponent 5)",
        SituationGroup.OTHER: "Other situation",
    }
    return descriptions.get(group, "Unknown situation")
