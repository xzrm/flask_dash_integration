import re

def text_analaysis(input_text):

    rx_phase = r'(PHASE \d* INITIALIZED.*)'
    analysis_text = re.findall(rx_phase, input_text, re.DOTALL)
    return analysis_text

def read_from(file):
    input_data = open(file)
    read_input_text = input_data.read()# creates  type(variable) -> <class 'str'>
    return read_input_text

