import logging
from functools import partial
import traceback

#from failed_handlers import handlers as failed_handlers

def recursive_getattr(obj,path):
    split_path=path.split('.')
    while len(split_path)>0:
        obj=getattr(obj,split_path.pop(0))
    return obj

class CommandDefinition(object):
    def __init__(self,command_mod,**parsers):
        self.parsers={}
        try:
            self.module=__import__(command_mod)
            if '.' in command_mod:
                cm=command_mod.split('.')
                cm.pop(0)
                while len(cm)>0:
                    self.module=getattr(self.module,cm.pop(0))
            for parser_name,parser_args in parsers.iteritems():
                vts=parser_args.copy()
                vts.update({'handler':recursive_getattr(self.module,parser_args['handler'])})
                self.parsers[parser_name]=vts
        except:
            logging.error('CommandDefinition: %s failed to load:\n%s' % (command_mod,traceback.format_exc()))
            raise
            if hasattr(self,'module'):
                logging.error('module''s contents: %s',dir(self.module))
            for parser_name,parser_args in parsers.iteritems():
                vts=parser_args.copy()
                vts.update({'handler':partial(failed_handlers[parser_name],parser_args['name'])})
                self.parsers[parser_name]=vts
                
    def failedHandler(self,cmd_name,*args,**kwargs):
        return 'Command %s is present in config file, but I have failed to load it. '+ \
         'This problem is big enough therefore your beloved pythonwhore may be already working on it. '+\
         'If the problem persists feel free to send him some hate beams via jabber.'
    
class CommandRegistry(object):
    
    def __init__(self):
        self.parsers={}
        
    def __getitem__(self,key):
        return self.parsers.__getitem__(key)

    def __contains__(self,key):
        return self.parsers.__contains__(key)
        
    def registerCommand(self,command_mod,**parsers):
        cd=CommandDefinition(command_mod,**parsers)
        self.registerCommandDef(cd)
        
    def registerCommandDef(self,command_definition):
        for parser_name,parser_args in command_definition.parsers.iteritems():
            self.parsers[parser_name,parser_args['name']]=parser_args
            
    def findCommand(self,parser,name):
        return self.parsers[parser,name]

