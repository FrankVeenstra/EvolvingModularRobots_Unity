from emr import encoding, controller, environment

def get_encoding_controller_and_evaluation_from_config(cfg):
    if (cfg['encoding']['type'] == 'graphgrammar'):
        encoding_reference = encoding.graph_grammar.GraphGrammar
    elif (cfg['encoding']['type'] == 'direct'):
        encoding_reference = encoding.direct_encoding.DirectEncoding
    else:
        encoding_reference = encoding.direct_encoding.DirectEncoding
        print(f"Could not find encoding type (options are 'graphgrammar' and 'direct'). returning direct")

    if (cfg['control']['type'] == 'pco'):
        controller_reference = controller.phase_coupled_oscillator.PhaseCoupledOscillator
    elif (cfg['control']['type'] == 'custom'):
        controller_reference = controller.custom_controller.CustomController
    else:
        print(f"Could not find controller type (options are 'pco' and 'custom'). returning pco")
        controller_reference = controller.phase_coupled_oscillator.PhaseCoupledOscillator
    # specify the evaluation functin to use (reference to function)
    evaluation_function_reference = environment.evaluation.evaluate_individual

    return encoding_reference, controller_reference, evaluation_function_reference
