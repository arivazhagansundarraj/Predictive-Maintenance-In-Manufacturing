"""
src/recommendation.py
Maintenance Recommendation Engine.

Maps Machine Health Score [0–100] → one of four action categories.
"""


RECOMMENDATIONS = {
    "Immediate Maintenance": {
        "threshold_max": 40,
        "color": "#FF4B4B",
        "emoji": "🔴",
        "priority": "CRITICAL",
        "description": (
            "Machine is in a critical state. Stop operation immediately "
            "and perform full maintenance inspection. Risk of catastrophic "
            "failure is HIGH."
        ),
        "actions": [
            "Halt machine operation immediately",
            "Notify maintenance team (Priority: URGENT)",
            "Perform full sensor and mechanical inspection",
            "Replace worn tooling components",
            "Log failure event in maintenance system",
        ],
    },
    "Schedule Maintenance": {
        "threshold_min": 40,
        "threshold_max": 60,
        "color": "#FF8C00",
        "emoji": "🟠",
        "priority": "HIGH",
        "description": (
            "Machine shows signs of degradation. Schedule maintenance "
            "within the next 24–48 hours. Continue operation at reduced load."
        ),
        "actions": [
            "Schedule maintenance within 24–48 hours",
            "Reduce machine load by 20–30%",
            "Increase monitoring frequency",
            "Prepare replacement parts",
            "Review last maintenance log",
        ],
    },
    "Monitor Closely": {
        "threshold_min": 60,
        "threshold_max": 80,
        "color": "#FFD700",
        "emoji": "🟡",
        "priority": "MEDIUM",
        "description": (
            "Machine is operating within acceptable bounds but shows "
            "early warning indicators. Increase monitoring frequency."
        ),
        "actions": [
            "Increase sensor check frequency",
            "Review temperature and torque trends",
            "Plan preventive maintenance within 1 week",
            "Check lubrication levels",
            "Document anomaly observations",
        ],
    },
    "Healthy": {
        "threshold_min": 80,
        "color": "#00D4FF",
        "emoji": "🟢",
        "priority": "LOW",
        "description": (
            "Machine is operating normally. No immediate action required. "
            "Continue routine maintenance schedule."
        ),
        "actions": [
            "Continue normal operation",
            "Maintain routine maintenance schedule",
            "Log sensor readings for trend analysis",
            "Confirm next scheduled service date",
        ],
    },
}


def get_recommendation(health_score: float) -> dict:
    """
    Return a recommendation dict based on health score [0–100].

    Parameters
    ----------
    health_score : float

    Returns
    -------
    dict with keys: name, color, emoji, priority, description, actions
    """
    if health_score < 40:
        name = "Immediate Maintenance"
    elif health_score < 60:
        name = "Schedule Maintenance"
    elif health_score < 80:
        name = "Monitor Closely"
    else:
        name = "Healthy"

    rec = RECOMMENDATIONS[name].copy()
    rec["name"] = name
    rec["health_score"] = round(health_score, 2)
    return rec


def get_recommendation_color(health_score: float) -> str:
    return get_recommendation(health_score)["color"]


def get_recommendation_label(health_score: float) -> str:
    rec = get_recommendation(health_score)
    return f"{rec['emoji']} {rec['name']}"
