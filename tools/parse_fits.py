#!/usr/bin/env python

from mstutil import get_path_to_project_root
import os, re, sys

rates = ['const', 'log2', 'linear / log2', 'linear', 'linear * log2', 'exponential']

def make_re(suffix):
    return re.compile('.*' + suffix + r'.*= ([-]?\d+[.]?\d*).*[(](\d+[.]?\d*)')

pat_var = re.compile(r'.*residuals.*: (\d+[.]?\d*).*')
pat_m = make_re('_m')
pat_c = make_re('_c')
pat_b = make_re('_b')
pat_e = make_re('_e')

class FitParam:
    def __init__(self, value, err):
        self.val = float(value)
        self.err = float(err)

    def __str__(self):
        return '%s %s' % (str(self.val), str(self.err))

def sapinn(pat, l, cur):
    z = pat.search(l)
    if z is not None:
        return z.groups()
    else:
        return cur

class FitScore:
    def __init__(self, var, avg, max_val):
        self.var = float(var)
        self.avg = float(avg)
        self.max = float(max_val)

    def get_best(self, other):
        if self.var < other.var and self.avg < other.avg and self.max < other.max:
            return self
        elif self.var > other.var and self.avg > other.avg and self.max > other.max:
            return other
        else:
            return None # neither is better

    def __cmp__(self, other):
        def fpcmp(f1, f2):
            return (-1 if f1 < f2 else (1 if f1 > f2 else 0))
        if fpcmp(self.var, other.var) != 0:
            return fpcmp(self.var, other.var)
        if fpcmp(self.avg, other.avg) != 0:
            return fpcmp(self.avg, other.avg)
        if fpcmp(self.max, other.max) != 0:
            return fpcmp(self.max, other.max)
        return 0

    def __str__(self):
        return '<var=%s, avg=%s, max=%s>' % (str(self.var), str(self.avg), str(self.max))

def fpstr(f, extra=1):
    p = 0
    fmt = '%.' + str(p) + 'f'
    while float(fmt % f) == 0.0 and p < 7:
        p += 1
        fmt = '%.' + str(p) + 'f'
    fmt = '%.' + str(p+extra) + 'f'
    return fmt % f

class Fit:
    def __init__(self, what, var):
        self.what = what
        self.var = float(var)
        self.m = self.c = self.b = self.e = None
        self.score = None

    @staticmethod
    def fpsapinn(pat, line, cur):
        ret = sapinn(pat, line, None)
        if ret is None:
            return cur
        else:
            return FitParam(ret[0], ret[1])

    def parse_line(self, line):
        self.m = Fit.fpsapinn(pat_m, line, self.m)
        self.c = Fit.fpsapinn(pat_c, line, self.c)
        self.b = Fit.fpsapinn(pat_b, line, self.b)
        self.e = Fit.fpsapinn(pat_e, line, self.e)

    def update_score(self):
        values = []
        if self.m is not None:
            values.append(self.m.err)
        if self.b is not None:
            values.append(self.b.err)
        if self.e is not None:
            values.append(self.e.err)
        if self.c is not None and len(values)==0: # ignore consts' error if other terms are present
            values.append(self.c.err)
        if len(values) == 0:
            raise Exception('no parameters are set!')
        self.score = FitScore(self.var, sum(values)/len(values), max(values))

    def __cmp__(self, other):
        return self.score.__cmp__(other.score)

    def __str__(self):
        if self.what == 'const':
            s = '%s' % fpstr(self.c.val)
        elif self.what == 'log2':
            s = '%s * log2(x) + %s' % (fpstr(self.m.val), fpstr(self.c.val))
        elif self.what == 'linear / log2':
            s = '%s * x^%s / log2(x) + %s' % (fpstr(self.m.val), fpstr(self.e.val), fpstr(self.c.val))
        elif self.what == 'linear':
            s = '%s * x^%s + %s' % (fpstr(self.m.val), fpstr(self.e.val), fpstr(self.c.val))
        elif self.what == 'linear * log2':
            s = '%s * x^%s * log2(x) + %s' % (fpstr(self.m.val), fpstr(self.e.val), fpstr(self.c.val))
        elif self.what == 'exponential':
            s = '%s * %s^x + %s' % (fpstr(self.m.val), fpstr(self.b.val), fpstr(self.c.val))

        fmt = '%-17s\t%s\t%s\t%s\t%s'
        return fmt % (self.what, fpstr(self.var), fpstr(self.score.avg), fpstr(self.score.max), s)

    def str_more(self):
        s = str(self) + '\n'
        fmt = '    %s: %s\n'
        s += fmt % ('multiplier ', fpstr(self.m))
        s += fmt % ('addtv const', fpstr(self.c))
        s += fmt % ('expon  base', fpstr(self.b))
        s += fmt % ('expon power', fpstr(self.e))
        return s

def main(argv=sys.argv[1:]):
    gplot = get_path_to_project_root() + 'writeup/figures/part2-fit-%s.gnuplot' % argv[0]
    os.system("gnuplot %s 2>&1 | egrep '%%|reduced' > tmp" % gplot)
    fh = open('tmp', 'r')
    lines = fh.readlines()
    fh.close()
    os.remove('tmp')

    res = []
    ri = 0
    fit = None
    for line in lines:
        var = sapinn(pat_var, line.rstrip(), None)
        if var is not None:
            if fit is not None:
                ri += 1
                res.append(fit)

            fit = Fit(rates[ri], var[0])

        if fit is not None:
            fit.parse_line(line)

    # last one
    res.append(fit)

    # print from best to worst
    for r in res:
        r.update_score()
    print 'best to worst fit for %s:' % gplot
    print '%-17s\tRCS\tAvgErr\tMaxErr\tFit' % 'Fit Type'
    res.sort()
    for r in res:
        print str(r)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        main(['edge'])
        main(['loc2'])
        main(['loc3'])
        main(['loc4'])
        sys.exit(0)
    else:
        sys.exit(main())
