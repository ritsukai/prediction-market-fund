# EV calculator module for the prediction market fund

def calculate_expected_value(probability, odds):
    """
    Calculates the expected value of a bet.
    """
    return (probability * (odds - 1)) - (1 - probability)
