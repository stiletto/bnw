import re

perct = re.compile('%([0-9%])', re.U)


def arg_substitution(s, args):
    numarg = 1
    for m in perct.finditer(s):
        if m.group(1) != '%':
            x = int(m.group(1))
            if x > numarg:
                numarg = x
    args = args.split(' ', numarg - 1)
    print numarg, args

    def substitute(m):
        i = m.group(1)
        if i == '%':
            return '%'
        i = int(i)
        if i < len(args):
            return args[i - 1]
        else:
            return args[-1]

    return perct.sub(substitute, s)
