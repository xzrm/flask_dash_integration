import pandas as pd
import functools
import os
import re

rx_dict = {
    'conv': re.compile(r'\s*STEP\s*(?P<step_n>\d*)\s*TERMINATED,\s*CONVERGENCE\s*AFTER\s*\d*\s*ITERATION(S)?'),
    'no_conv': re.compile(r'\s*STEP\s*(?P<step_n>\d*)\s*TERMINATED,\s*NO\s*CONVERGENCE\s*AFTER\s*\d*\s*ITERATION(S)?'),
    }


def phases_from_sequence(lst):
    seq = [[lst[0]]]
    for i in range(1, len(lst)):
        if lst[i-1] + 1 == lst[i]:
            seq[-1].append(lst[i])
        else:
            seq.append([lst[i]])
    return seq

def parse_global_data(text):

    def _parse_line(line):
        for key, rx in rx_dict.items():
            match = rx.search(line)
            if match:
                return key, match
        return None, None

    converged_step_numbers = []
    unconverged_step_numbers = []
    step_numbers = []
    step_ix = 1

    stripped_text = iter(text.split('\n'))

    while True:
        try:
            line = next(stripped_text)
            key, match = _parse_line(line)

            if key == 'conv':
                step_number = int(match.group('step_n'))
                # converged_step_numbers.append(step_number)
                converged_step_numbers.append((step_ix, step_number))
                step_ix += 1
                step_numbers.append(step_number)
            if key == 'no_conv':
                step_number = int(match.group('step_n'))
                # unconverged_step_numbers.append(step_number)
                unconverged_step_numbers.append((step_ix, step_number))
                step_ix += 1
                step_numbers.append(step_number)

        except StopIteration:
            break
        
    steps_in_phases = phases_from_sequence(step_numbers)
    phases = len(steps_in_phases)
    
    print(f'converged load steps numbers: {converged_step_numbers}\n')
    print(f'unconverged load steps numbers: {unconverged_step_numbers}\n')
    print(f'total load steps numbers: {step_numbers}\n')
    print(f'Steps in phases: {steps_in_phases}')
    print(f'There are {phases} phases')

    return step_numbers, unconverged_step_numbers, steps_in_phases, phases
