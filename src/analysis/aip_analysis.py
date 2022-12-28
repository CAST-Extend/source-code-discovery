from analysis.analysis import Analysis
from logger import INFO
from config import Config
from util import run_process

from analysis.trackAnalysis import TrackAnalysis

class AIPAnalysis(Analysis):

    def __init__(cls, log_level:int):
        super().__init__(cls.__class__.__name__,log_level)
        pass
    
    def run(cls, config:Config):
        for appl in config.application:

            #has thi spplication already been run?
            aip_status = config.application[appl]['aip']
            if aip_status == '' or aip_status.startswith('Error'):
                #add a new appication in AIP Console
                cls._log.info(f'Running analysis for {config.project_name}\{appl}')
                
                args = [f'{config.java_home}\\bin\\java.exe',
                        '-jar',config.aip_cli,
                        'add',
                        '-n',f'{appl}',
                        '-f', f'{config.project_name}//{appl}//AIP',
                        '-s',config.console_url,
                        '--apikey',config.console_key,
                        '--verbose' , 'false',
                        '--auto-create','--blueprint'
                        ]

                if len(config.node) > 0:
                    args = args + ['--node-name',config.node_name]

                process = run_process(args,wait=False)
            else:
                cls._log.info(f'{appl} has already been successfully analyized, skipping step')
                process = None

            cls.track_process(process,"AIP",appl)

        #TrackAnalysis(INFO).run(config)
        
        


        