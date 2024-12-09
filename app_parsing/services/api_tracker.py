#cv parsing 2/app_parsing/services/api_tracker.py

class APIUsageTracker:
    """Tracks OpenAI API usage and costs.

    This class keeps track of API calls, tokens used,
    and associated costs.

    Attributes:
        total_tokens (int): Total number of tokens used
        total_cost (float): Total cost in USD
        total_calls (int): Total number of API calls
    """
    def __init__(self):
        self.total_tokens = 0
        self.total_cost = 0
        self.total_calls = 0

    def update(self, tokens):
        self.total_tokens += tokens
        self.total_cost += (tokens / 1000) * 0.002
        self.total_calls += 1

    def get_stats(self):
        return {
            "total_tokens": self.total_tokens,
            "total_cost_usd": round(self.total_cost, 2),
            "total_api_calls": self.total_calls,
            
        }