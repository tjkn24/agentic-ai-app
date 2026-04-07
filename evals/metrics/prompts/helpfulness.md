# Helpfulness metric

Score the agent response on a scale of 1–5:
- 5: Fully answers the question, clear, accurate, no padding
- 3: Partially answers, some irrelevance
- 1: Does not answer, confusing, or harmful

Return only JSON: {"score": <int>, "reason": "<one sentence>"}
