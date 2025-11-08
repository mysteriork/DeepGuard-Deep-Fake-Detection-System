import numpy as np

class TemporalConsistencyModel:
    """
    Simple temporal smoothing model to capture flicker and irregular changes.
    Works as a moving average + penalty for inconsistent transitions.
    """
    def __init__(self, window=5, alpha=0.7):
        self.window = window
        self.alpha = alpha
        self.history = []

    def update(self, score):
        self.history.append(score)
        if len(self.history) > self.window:
            self.history.pop(0)
        smoothed = np.mean(self.history)
        # penalize high oscillations
        flicker_penalty = np.std(self.history)
        final = (self.alpha * smoothed) - (0.5 * flicker_penalty)
        return np.clip(final, 0, 1)


####################################################################################################################################################3

