from emr.utility import tests
from emr.config import config_handler
if __name__=="__main__":

    from emr.utility import tests
    from emr.config import config_handler
    cfg = config_handler.make_config()
    cfg['experiment']['executable_path'] = "./EMR_Executable/EvolvingModularRobots"
    tests.run_all_tests(cfg, headless = False)
    