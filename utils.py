from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import create_session, scoped_session
import settings
import time

#metadata = MetaData()
#database_engine = create_engine(settings.DATABASE_URI, convert_unicode=True)
#session = scoped_session(lambda: create_session(database_engine,
#                         autocommit=True))
#session = create_session(database_engine, autocommit=True)

def log(urgency,format,*args):
    print time.strftime('%c',time.gmtime())+': '+(format % args)


def cmd_registered(func):
    def check_registered(conn,source,user,args):
        if user is None:
            conn.sendMessage(source,'Sorry. This command is for registered users only.')
        else:
            func(conn,source,user,args)
    check_registered.__doc__=func.__doc__
    check_registered.func_dict=func.func_dict
    return check_registered


def cmd_admins(func):
    def check_admin(conn,source,user,args):
        if user is None:
            conn.sendMessage(source,'Sorry. This command is for registered users only.')
            return
        elif user.nid!=settings.ADMIN:
            conn.sendMessage(source,'Hey, you are not an administrator, %s (%s).' % (source,user.nid) )
            return
        else:
            func(conn,source,user,args)
    check_admin.__doc__=func.__doc__
    check_admin.func_dict=func.func_dict
    return check_admin

def gettext(text,lang=None):
    return text
