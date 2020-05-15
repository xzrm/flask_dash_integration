import re
import os
import itertools


def read_from(file):
    input_data = open(file)
    read_input_text = input_data.read()  # creates  type(variable) -> <class 'str'>
    return read_input_text


# rx_pattern = re.compile(r'\*PHASE LABEL=\".*\"(.*?)\*PHASE LABEL=\".*\"', re.DOTALL)

def multiple_replace(dict, text):
    # Create a regular expression  from the dictionary keys
    regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text)


d = {"*": r"\*", '"': r"\""}


def get_dcf_commands(text_file):
    """
    Returns text being all commands
    """

    input_text = read_from(text_file)
    rx_all_commands = re.compile(r'\*INPUT\n(.*?)\*END\n', re.DOTALL)
    mo_all_commands_text = rx_all_commands.search(input_text)  # NOTE: mo stands for matched object
    try:
        all_commands = mo_all_commands_text.group(0)
        return all_commands
    except AttributeError:
        return None


def get_phases_from_commands(input_file):
    """
    Returns phase names (labels) from commands
    """

    all_commands = get_dcf_commands(input_file)
    if all_commands == None:
        return

    rx_phase_names = re.compile(r'\*(?P<phase>PHASE LABEL=\".*\")\n')
    phases_list = rx_phase_names.findall(all_commands)

    return rename_phases(phases_list)


def get_phase_text(input_file):

    phases_list = get_phases_from_commands(input_file)
    text_in_phases = []
    # rx_phase = r'\*PHASE LABEL=\"Phased\"(.*)\*PHASE LABEL=\"Phased 1\"'

    for i in range(len(phases_list)):
        try:
            text_bound_beg = multiple_replace(d, phases_list[i]).strip("\n")
            text_bound_end = multiple_replace(d, phases_list[i + 1]).strip("\n")
            rx_text_phase = (text_bound_beg + "(.*)" + text_bound_end)
        except IndexError:
            rx_text_phase = (text_bound_beg + "(.*)" + r"\*END")

        mo_text_phase = re.search(rx_text_phase, all_commands, re.DOTALL)
        text_in_phases.append(mo_text_phase.group(0))

    return text_in_phases


# def get_labels(input_file):
#     phases = get_phases_from_commands(input_file)
#     labels_rx = re.compile(r'PHASE LABEL=\"(?P<label>.*)\"')
#     labels = [labels_rx.match(i).group('label') for i in phases]

#     return rename_phases(labels)


def text_single_phase(input_file, phase):
    """Function searches for a phase - text between the specified phase and phase + 1
        If the specified phase is the last phase in the .out file,
        the text is read to the end and returned.
        If none of the phases is found None is returned.
    """

    assert isinstance(phase, int), "Specify phase number as an integer"

    read_input_text = read_from(input_file)

    rx_phase = r'(PHASE {0} INITIALIZED.*?) PHASE {1} INITIALIZED'.format(phase, phase + 1)
    phase_text = re.findall(rx_phase, read_input_text, re.DOTALL)

    if not phase_text:
        rx_phase = r'(PHASE {0} INITIALIZED.*)'.format(phase)
        phase_text = re.findall(rx_phase, read_input_text, re.DOTALL)
        if not phase_text:
            print("Phase not in a file")
            return None
        else:
            return phase_text
    else:
        return phase_text


def rename_phases(phases):
    renamed_phases = ['Phase ' + str(i) for i, phase in enumerate(phases, 1)]
    return renamed_phases


def get_phases_from_analysis(input_file):
    read_input_text = read_from(input_file)

    rx_phase = r' PHASE (?P<phase_no>\d*) INITIALIZED'
    phase_list = re.findall(rx_phase, read_input_text, re.DOTALL)
    return rename_phases(phase_list)


# input_file = "aanvaarbescherming_11_LC1_LC_A.out"
# input_file = "Analysis_wCL_full_241-09.out"

# print(get_phases_from_analysis(input_file))
# print(get_phases_from_commands(input_file))


def get_phases(input_file):
    phases = get_phases_from_commands(input_file)
    if phases == None:
        phases = get_phases_from_analysis(input_file)
    return phases


# def text_analaysis_no_phases(input_data):

#     read_input_text = read_from(input_file)
#     rx_phase = r'(STEP      1 INITIATED:.*)'
#     analysis_text = re.findall(rx_phase, read_input_text, re.DOTALL)
#     return analysis_text


def text_analaysis(input_text):

    rx_phase = r'(PHASE \d* INITIALIZED.*)'
    analysis_text = re.findall(rx_phase, input_text, re.DOTALL)
    return analysis_text



# print(get_phases(input_file))
