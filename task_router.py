# task_router.py

def get_market_volatility():
    # Placeholder function; later integrate with an actual market data API
    return 25  # dummy value

def get_threshold():
    volatility = get_market_volatility()
    if volatility > 30:
        return 0.85
    else:
        return 0.82

def route_task(task):
    threshold = get_threshold()
    # For now, simulate similarity calculation with a dummy score
    dummy_similarity_score = 0.83
    if dummy_similarity_score >= threshold:
        return "Agent_A"
    else:
        return "Agent_B"

if __name__ == "__main__":
    sample_task = "Explain SPX volatility smile dynamics"
    assigned_agent = route_task(sample_task)
    print(f"Task: {sample_task} routed to {assigned_agent}")
