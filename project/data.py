
import re
import os
import itertools


def read_from(file):
    input_data = open(file)
    read_input_text = input_data.read()  # creates  type(variable) -> <class 'str'>
    return read_input_text


rx_dict = {
    'step_init': re.compile(r'\s*STEP\s*(?P<step_n>\d*)\s*INITIATED:'),
    'load_case': re.compile(r'\s*LOAD INCREMENT:  LOADING\(\s*(?P<load_case>\d*)\) \*   \d*\.\d*E[-|+]\d*'),
    'norm': re.compile(r'\s*STEP\s*\d*\s*:\s*(?P<norm>[A-Z]* NORM)\s*=  \d*\.\d*E[-|+]\d*\s*TOLERANCE =  (?P<norm_tolerance>\d*\.\d*E[-|+]\d*)'),
    'rel_displ_var': re.compile(r'\s*RELATIVE DISPLACEMENT VARIATION =  (?P<rdv>\d*\.\d*E[-|+]\d*)         CHECK = (?P<rdv_check>\w*)'),
    'rel_energy_var': re.compile(r'\s*RELATIVE ENERGY VARIATION       =  (?P<rev>\d*\.\d*E[-|+]\d*)         CHECK = (?P<rev_check>\w*)'),
    'rel_force_var': re.compile(r'\s*RELATIVE OUT OF BALANCE FORCE   =  (?P<rfv>\d*\.\d*E[-|+]\d*)         CHECK = (?P<rfv_check>\w*)'),
    'rel_residu_var': re.compile(r'\s*RELATIVE RESIDU VARIATION       =  (?P<rrv>\d*\.\d*E[-|+]\d*)         CHECK = (?P<rrv_check>\w*)'),
    # 'no_conv': re.compile(r'\s*STEP\s*(?P<step_n>\d*)\s*TERMINATED,\s*NO\s*CONVERGENCE\s*AFTER\s*\d*\s*ITERATION(S)?'),
    'conv': re.compile(r'\s*STEP\s*(?P<step_n>\d*)\s*TERMINATED,\s*CONVERGENCE\s*AFTER\s*(?P<itera>\d*)\s*ITERATION(S)?'),
    'itera': re.compile(r'\s*STEP\s*(?P<step_n>\d*)\s*TERMINATED,\s*(NO\s*)?CONVERGENCE\s*AFTER\s*\d*\s*ITERATION(S)?'),
    'cumulative_react': re.compile(r'     CUMULATIVE REACTION:         FORCE X        FORCE Y          FORCE Z'),
    'cumulative_react_values': re.compile(r'\s*(?P<force_x>(-)?\d*\.\d*D[-|+]\d*)\s*(?P<force_y>(-)?\d*\.\d*D[-|+]\d*)\s*(?P<force_z>(-)?\d*\.\d*D[-|+]\d*)')}


class SingleStepData:

    def __init__(self, step_no):
        self.step_no = int(step_no)
        self.displacement_norm = []
        self.force_norm = []
        self.energy_norm = []
        self.start_step = False
        self.converged = False
        self.load_case = None
        self.zero_itera_step = False
        self.step_iterations = None
        self.total_iterations = None
        self.governing_norm = {}

    def add_result(self, key, match):
        if key == 'rel_displ_var':
            disp_var = match.group('rdv')
            self.displacement_norm.append(float(disp_var))
            if match.group('rdv_check') == 'TRUE':
                self.governing_norm["displacement_norm"] = float(disp_var)

        elif key == 'rel_energy_var':
            energy_var = match.group('rev')
            self.energy_norm.append(float(energy_var))
            if match.group('rev_check') == 'TRUE':
                self.governing_norm["energy_norm"] = float(energy_var)

        elif key == 'rel_force_var':
            force_var = match.group('rfv')
            self.force_norm.append(float(force_var))
            if match.group('rfv_check') == 'TRUE':
                self.governing_norm["force_norm"] = float(force_var)

        elif key == 'rel_residu_var':
            residu_var = match.group('rrv')
            self.residu_norm.append(float(residu_var))

        elif key == 'conv':
            self.is_converged()
            self.step_iterations = match.group('itera')

            if self.step_iterations == '0':
                print('WARNING: ZERO ITERATIONS STEP')
                self.is_zero_itera_step()

        elif key == 'load_case':
            loading_case = match.group('load_case')
            self.load_case = loading_case

    def is_startstep(self):
        self.start_step = True
        self.residu_norm = []

    def is_converged(self):
        self.converged = True

    def is_zero_itera_step(self):
        self.zero_itera_step = True

    # def get_norms(self):
    #     return [i for i in a.__dict__ if isinstance(a.__dict__.get(i), list)]

    def __str__(self):
        s = "STEP NO. {}\nITERATIONS {}\nCONVERGED STEP     {}\nDISPLACEMENT NORM: {}\nFORCE NORM: {}\nENERGY NORM: {}\nLOAD CASE: {}\nGOVERNING NORM: {}".format(
            str(self.step_no), str(self.step_iterations),
            str(self.converged), str(self.displacement_norm),
            str(self.force_norm), str(self.energy_norm),
            self.load_case, self.governing_norm)

        if self.start_step:
            return "START STEP   " + str(self.start_step) + "\n" + s
        return s

    def get_loadcase(self):
        if self.start_step:
            return 'Start step'
        return self.load_case

    def get_step_no(self):
        return self.step_no


def parse_global_data(text):

    def parse_line(line):
        for key, rx in rx_dict.items():
            match = rx.search(line)
            if match:
                return key, match
        return None, None

    step_objects = []
    stripped_text = iter(text[0].split('\n'))

    while True:
        try:
            line = next(stripped_text)
            # print(line)
            key, match = parse_line(line)

            if key == 'step_init':
                step_number = match.group('step_n')
                single_step_obj = SingleStepData(step_number)
                step_objects.append(single_step_obj)

            # if "START STEPS" in line:
            #     single_step_obj.is_startstep()

            if any(key == rx for rx in ['rel_displ_var', 'rel_energy_var', 'rel_force_var', 'rel_residu_var', 'conv', 'load_case']):
                single_step_obj.add_result(key, match)

        except StopIteration:
            break

    return step_objects


class Convergence:
    def __init__(self, step_objects, norm, tolerance):
        self.step_objects = step_objects
        self.norm = norm
        self.tolerance = tolerance

        self.variations()
        self.add_step_last_itera()

    def add_step_last_itera(self):
        self.full_step_itera = []
        self.itera_unconv_pairs = []
        self.itera_conv_pairs = []

        self.converged_norm_other = []
        self.converged_norm_this = []
        self.itera_unconv_pairs = []

        iteration_count = 0
        for step_obj in self.step_objects:
            # print(step_obj)
            if getattr(step_obj, self.norm):
                iteration_count += len(getattr(step_obj, self.norm))
                setattr(step_obj, 'total_iterations', iteration_count)
                last_variation = getattr(step_obj, self.norm)[-1]
                self.full_step_itera.append((iteration_count, last_variation))

                if not step_obj.converged:
                    self.itera_unconv_pairs.append((iteration_count, last_variation))
                else:
                    self.itera_conv_pairs.append((iteration_count, last_variation))

                self.convergence_check(step_obj)

        if not self.full_step_itera:
            print("The are no results for this norm")

    def convergence_check(self, step_obj):
        last_variation = getattr(step_obj, self.norm)[-1]
        if(step_obj.converged):
            try:
                last_variation = step_obj.governing_norm[self.norm]
                self.converged_norm_this.append((step_obj.total_iterations, last_variation))
            except KeyError:
                self.converged_norm_other.append((step_obj.total_iterations, last_variation))
        else:
            self.itera_unconv_pairs.append((step_obj.total_iterations, last_variation))

    def variations(self):
        self.iterations_steps = [getattr(step_obj, self.norm) for step_obj in self.step_objects]
        self.all_iterations = list(itertools.chain(*self.iterations_steps))


# def unpack_values(func):
#     def wrapper(*args, **kwargs):
#         unpacked_values = unpack(func(*args, **kwargs))
#         return unpacked_values
#     return wrapper


def filter_empty_steps(step_objects, norm):
    none_empty = [step_obj for step_obj in step_objects if getattr(step_obj, norm)]
    return none_empty


# def get_data(text_list, norm, tolerance):
#     step_objects = filter_empty_steps(parse_global_data(text_list), norm)
#     convergence = Convergence(step_objects, norm, tolerance)
#     return step_objects, convergence


def get_data(text_list, norm, tolerance):
    
    # step_objects = filter_empty_steps(parse_global_data(text_list), norm)
    step_objects = parse_global_data(text_list)

    for step_object in step_objects:
        max_length = max([len(getattr(step_object,'displacement_norm')),
                        len(getattr(step_object,'energy_norm')),
                        len(getattr(step_object, 'force_norm'))])
    
        for n in ['displacement_norm', 'energy_norm', 'force_norm']:
            variations = getattr(step_object, n)
            if len(variations) == 0:
                setattr(step_object, n, [0.0] * max_length)

    convergence = Convergence(step_objects, norm, tolerance)

    return step_objects, convergence