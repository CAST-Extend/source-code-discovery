"""
    Read and validate configuration file
"""
from cast_common.logger import Logger,DEBUG, INFO, WARN, ERROR
from cast_common.util import create_folder
from json import load
from argparse import ArgumentParser
from json import JSONDecodeError,dump
from os.path import abspath,exists

__author__ = "Nevin Kaplan"
__copyright__ = "Copyright 2022, CAST Software"
__email__ = "n.kaplan@castsoftware.com"

class Config():
    log = None
    log_translate = {} 
    def __init__(self,base_folder:str,project_name,config='config.json',log_level: int=INFO):
        self.log = Logger(self.__class__.__name__,log_level)

        #do all required fields contain data
        try:
            self._config_file = abspath(f'{base_folder}/.oneclick/{project_name}.json')
            if exists(self._config_file):
                with open(abspath(self._config_file), 'rb') as config_file:
                    self._config = load(config_file)
            else:
                self._config={}

            self.setting['base'] = base_folder
            self.project = project_name

            self._save()

        except JSONDecodeError as e:
            msg = str(e)
            self.log.error(f'Configuration file {self._config_file} must be in a JSON format {msg}')
            exit()

        except ValueError as e:
            msg = str(e)
            self.log.error(msg)
            exit()

    def clean_creds(self,value):
        if type(value) is dict:
            for skey, svalue in value.items():  
                if skey=='password' or skey=='user':
                    value[skey]='*******************'
                else:
                    self.clean_creds(svalue)
        return

    def _save(self):
        create_folder(abspath(f'{self.base}/.oneClick'))
        with open(self._config_file, "w") as f:
            dump(self._config, f,indent=4)

    def _set_rest_settings(self,dict):
        for v in ["Active","URL","user","password"]:
            if v not in dict:
                raise ValueError(f"Required field '{v}' is missing from config.json")
    @property
    def rest(self):
        return self._get(self._config,'rest',{})

    def _set_active(self,node,chk_lst):
        chk = True
        for item in chk_lst:
            if item not in node or node[item]=='':
                chk = False
                break
        node['Active']=chk

    def _get(self,base,key,default=''):
        if key not in base:
            base[key] = default  
        return base[key]        

    def _set_value(self,base,key,value,default=''):
        base[key] = self._get(base,key,default)
        if value is not None:
            base[key]=value
            return True
        else:
            return False

    """ **************** Highlight entries ************************ """
    @property
    def highlight(self):
        if 'Highlight' not in self.rest:
            self.rest['Highlight']={}
            self.highlight['Active']=False
        return self.rest['Highlight']
    @property
    def is_hl_active(self):
        return self.highlight['Active']

    def _set_hl_active(self):
        self._set_active(self.highlight,['URL','user','password','instance'])

    @property
    def hl_url(self):
        return self._get(self.highlight,'URL')
    @hl_url.setter
    def hl_url(self,value):
        if self._set_value(self.highlight,'URL',value):
            self._set_hl_active()
            self._save()

    @property
    def hl_user(self):
        return self._get(self.highlight,'user')
    @hl_user.setter
    def hl_user(self,value):
        if self._set_value(self.highlight,'user',value):
            self._set_hl_active()
            self._save()

    @property
    def hl_password(self):
        return self._get(self.highlight,'password')
    @hl_password.setter
    def hl_password(self,value):
        if self._set_value(self.highlight,'password',value):
            self._set_hl_active()
            self._save()

    @property
    def hl_instance(self):
        return self._get(self.highlight,'instance')
    @hl_instance.setter
    def hl_instance(self,value):
        if self._set_value(self.highlight,'instance',value):
            self._set_hl_active()
            self._save()

    @property
    def hl_cli(self):
        return self._get(self.highlight,'cli')
    @hl_cli.setter
    def hl_cli(self,value):
        if self._set_value(self.highlight,'cli',value):
            self._save()

    @property
    def perlInstallDir(self):
        return self._get(self.highlight,'perlInstallDir')
    @perlInstallDir.setter
    def perlInstallDir(self,value):
        if self._set_value(self.highlight,'perlInstallDir',value):
            self._save()

    @property
    def analyzerDir(self):
        return self._get(self.highlight,'analyzerDir')
    @analyzerDir.setter
    def analyzerDir(self,value):
        if self._set_value(self.highlight,'analyzerDir',value):
            self._save()

    @property
    def is_hl_config_valid(self)->bool:
        if not self.is_hl_active:
            self.log.warning('Highlight analysis is inactive')            
            return True

        is_ok=True
        msg=[]
        if len(self.hl_cli) == 0:
            msg.append('hl_cli')
        if len(self.perlInstallDir) == 0:
            msg.append('perlInstallDir')
        if len(self.analyzerDir) == 0:
            msg.append('analyzerDir')
        if len(self.java_home) == 0:
            msg.append('java_home')
        
        if len(msg) > 0:
            fmt_msg=', '.join(msg)
            self.log.error(f'Invalid Highlight configuration, missing {fmt_msg} fields')
            is_ok=False

        return is_ok

    """ **************** AIP REST related entries ************************ """
    def _set_aip_active(self,key,value,default=''):
        if self._set_value(self.aip,key,value,default):
            self._set_active(self.aip,['URL','user','password'])
            self._save()

    @property
    def aip(self):
        return self._get(self.rest,'AIP',{})

    @property
    def is_aip_active(self)->bool:
        return self.aip['Active']

    @property
    def aip_url(self):
        return self.aip['URL']
    @aip_url.setter
    def aip_url(self,value):
        self._set_aip_active('URL',value,'')
            
    @property
    def aip_user(self):
        return self.aip['user']
    @aip_user.setter
    def aip_user(self,value):
        self._set_aip_active('user',value,'')

    @property
    def aip_password(self):
        return self.aip['password']
    @aip_password.setter
    def aip_password(self,value):
        self._set_aip_active('password',value,'')

    """ **************** Console REST related entries ************************ """
    def _set_console_active(self,key,value,default=''):
        if self._set_value(self.console,key,value,default):
            self._set_active(self.console,['URL','API_Key'])
            self._save()

    @property
    def console(self):
        return self._get(self.rest,'AIPConsole',{})

    def cosole_active(self)->bool:
        return self.console['Active']

    @property
    def console_url(self)->str:
        return self.console['URL']
    @console_url.setter
    def console_url(self,value):
        self._set_console_active('URL',value,'')

    @property
    def console_key(self)->str:
        return self.console['API_Key']
    @console_key.setter
    def console_key(self,value):
        self._set_console_active('API_Key',value,'')

    @property
    def console_cli(self):
        return self.console['console-cli']
    @console_cli.setter
    def console_cli(self,value):
        self._set_console_active('console-cli',value,'')

    @property
    def node(self):
        if self.console['node'] is None or len(self.console['node'])==0:
            return 'local'
        return self.console['node']   
    @node.setter
    def node(self,value):
        self._set_console_active('node',value,'')

    """ **************** Action Plan related entries ************************ """
    def _set_database_active(self,key,value,default=''):
        if self._set_value(self.db,key,value,default):
            self._set_active(self.db,['database','user','password','host','port'])
            self._save()

    @property
    def db(self):
        return self._get(self._config,'Database',{})

    @property
    def database(self):
        return self.db['database']
    @database.setter
    def database(self,value):
        self._set_database_active('database',value,'')

    @property
    def user(self):
        return self.db['user']
    @user.setter
    def user(self,value):
        self._set_database_active('user',value,'')

    @property
    def password(self):
        return self.db['password']
    @password.setter
    def password(self,value):
        self._set_database_active('password',value,'')
    
    @property
    def host(self):
        return self.db['host']
    @host.setter
    def host(self,value):
        self._set_database_active('host',value,'')
    
    @property
    def port(self):
        return self.db['port']
    @port.setter
    def port(self,value):
        self._set_database_active('port',value,'')



    """ **************** Project related entries ************************ """
    @property
    def project(self):
        return self._config['project']
    @project.setter
    def project(self,value):
        if type(value) is not str:
            raise ValueError(f'Expecting a the project name, got {type(value)}')

        self.log.info(f'New project: {value}')
        if 'project' not in self._config:
            self._config['project']={}
            self._config['project']['name']=value
            self._config['project']['application']={}

        elif value != self.project_name:
            raise ValueError("Can't rename a project")

    @property
    def project_name(self):
        return self.project['name']

    @property
    def company_name(self):
        return self.project['company_name']
    @company_name.setter
    def company_name(self,value):
        if value is not None:
            self.project['company_name']=value
            self._save()

    """ **************** Application related entries ************************ """
    @property
    def application(self):
        return self.project['application']
    @application.setter
    def application(self,value:list):
        if type(value) is not list:
            raise ValueError(f'Expecting a list of application names, got {type(value)}')

        update = False
        for appl_name in value:
            if appl_name in self.application.keys():
                pass
            else:
                self.project['application'][appl_name]={'aip':'','hl':''}
                update = True


        # self._config['application']=value
        if update:
            self._save()

    @application.deleter
    def application(self):
        self.project['application']={}

    @property
    def deliver(self):
        return f'{self.base}\\deliver\\{self.project_name}'
    @property
    def work(self):
        return f'{self.base}\\STAGED\\{self.project_name}'
    @property
    def report(self):
        return f'{self.base}\\REPORT'
    @property
    def logs(self):
        return f'{self.base}\\LOGS'

    """ **************** Email related entries ************************ """
    @property 
    def email(self):
        return self._config['email']
    @property
    def from_email_addrs(self):
        return self.email['from']

    @property
    def from_email_passwd(self):
        return self.email['password']

    @property
    def to_email_addrs(self):
        return self.email['to']

    @property
    def email_body(self):
        return self.email['body']     

    @property
    def email_subject(self):
        return self.email['subject'] 

    """ **************** Setting related entries ************************ """
    @property 
    def setting(self):
        if 'setting' not in self._config:
            self._config['setting']={}
        return self._config['setting']

    @property
    def arg_template(self):
        return self.setting['arg-template']

    @property
    def base(self):
        return self.setting['base']
    @base.setter
    def base(self,value):
        if value is not None:
            self.setting['base']=value
            self._save()

    # @property
    # def reset(self):
    #     return self.setting['reset']
    # @reset.setter
    # def reset(self,value):
    #     if value is None:
    #         self.setting['reset']=False
    #     else:
    #         self.setting['reset']=value
    #     self._save()

    @property
    def java_home(self):
        return self.setting['java-home']
    @java_home.setter
    def java_home(self,value):
        if self._set_value(self.setting,'java-home',value,''):
            self._save()


#        def _set_value(self,base,key,value,default=''):


    
    # @property
    # def template(self):
    #     return self._config['template']