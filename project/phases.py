import re

def text_analaysis(input_text):

    rx_phase = r'(PHASE \d* INITIALIZED.*)'
    analysis_text = re.findall(rx_phase, input_text, re.DOTALL)
    return analysis_text

