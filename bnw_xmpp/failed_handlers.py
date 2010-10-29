
from parser_redeye import requireAuthRedeye
from parser_simplified import requireAuthSimplified

class FailedHandler(object):#BaseRedeyed,BaseSimplified):
    errstring = 'Command "%s" is present in config file, but i failed to load it. '+ \
         'This problem is big enough therefore your beloved pythonwhore may be already working on it. '+\
         'If the problem persists feel free to send him some hate beams via jabber.'

    def handleRedeye(self,cmd_name,*args,**kwargs):
        return self.errstring % (cmd_name,)
    handleRedeye.arguments=()

fh=FailedHandler()

handlers={'redeye':fh.handleRedeye,
    'simplified':fh.handleRedeye}
