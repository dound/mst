#!/usr/bin/env python

from data import DataSet, WeightResult
from math import sqrt
from mstutil import get_path_to_project_root
import os, sys

# t-distribution values for 90, 95, and 99% confidence intervals for degrees of freedom up to 100 (inclusive)
MAX_DF = 100
DATA_PATH = get_path_to_project_root() + 'writeup/data/weight/'
T_DISTRIBUTION = {90:[None,None,2.9200,2.3534,2.1318,2.0150,1.9432,1.8946,1.8595,1.8331,1.8125,1.7959,1.7823,1.7709,1.7613,1.7531,1.7459,1.7396,1.7341,1.7291,1.7247,1.7207,1.7171,1.7139,1.7109,1.7081,1.7056,1.7033,1.7011,1.6991,1.6973,1.6955,1.6939,1.6924,1.6909,1.6896,1.6883,1.6871,1.6860,1.6849,1.6839,1.6829,1.6820,1.6811,1.6802,1.6794,1.6787,1.6779,1.6772,1.6766,1.6759,1.6753,1.6747,1.6741,1.6736,1.6730,1.6725,1.6720,1.6716,1.6711,1.6706,1.6702,1.6698,1.6694,1.6690,1.6686,1.6683,1.6679,1.6676,1.6672,1.6669,1.6666,1.6663,1.6660,1.6657,1.6654,1.6652,1.6649,1.6646,1.6644,1.6641,1.6639,1.6636,1.6634,1.6632,1.6630,1.6628,1.6626,1.6624,1.6622,1.6620,1.6618,1.6616,1.6614,1.6612,1.6611,1.6609,1.6607,1.6606,1.6604,1.6602],
                  95:[None,None,4.3027,3.1824,2.7765,2.5706,2.4469,2.3646,2.3060,2.2622,2.2281,2.2010,2.1788,2.1604,2.1448,2.1315,2.1199,2.1098,2.1009,2.0930,2.0860,2.0796,2.0739,2.0687,2.0639,2.0595,2.0555,2.0518,2.0484,2.0452,2.0423,2.0395,2.0369,2.0345,2.0322,2.0301,2.0281,2.0262,2.0244,2.0227,2.0211,2.0195,2.0181,2.0167,2.0154,2.0141,2.0129,2.0117,2.0106,2.0096,2.0086,2.0076,2.0066,2.0057,2.0049,2.0040,2.0032,2.0025,2.0017,2.0010,2.0003,1.9996,1.9990,1.9983,1.9977,1.9971,1.9966,1.9960,1.9955,1.9949,1.9944,1.9939,1.9935,1.9930,1.9925,1.9921,1.9917,1.9913,1.9908,1.9905,1.9901,1.9897,1.9893,1.9890,1.9886,1.9883,1.9879,1.9876,1.9873,1.9870,1.9867,1.9864,1.9861,1.9858,1.9855,1.9852,1.9850,1.9847,1.9845,1.9842,1.9840],
                  99:[None,None,9.9250,5.8408,4.6041,4.0321,3.7074,3.4995,3.3554,3.2498,3.1693,3.1058,3.0545,3.0123,2.9768,2.9467,2.9208,2.8982,2.8784,2.8609,2.8453,2.8314,2.8188,2.8073,2.7970,2.7874,2.7787,2.7707,2.7633,2.7564,2.7500,2.7440,2.7385,2.7333,2.7284,2.7238,2.7195,2.7154,2.7116,2.7079,2.7045,2.7012,2.6981,2.6951,2.6923,2.6896,2.6870,2.6846,2.6822,2.6800,2.6778,2.6757,2.6737,2.6718,2.6700,2.6682,2.6665,2.6649,2.6633,2.6618,2.6603,2.6589,2.6575,2.6561,2.6549,2.6536,2.6524,2.6512,2.6501,2.6490,2.6479,2.6469,2.6458,2.6449,2.6439,2.6430,2.6421,2.6412,2.6403,2.6395,2.6387,2.6379,2.6371,2.6364,2.6356,2.6349,2.6342,2.6335,2.6329,2.6322,2.6316,2.6309,2.6303,2.6297,2.6291,2.6286,2.6280,2.6275,2.6269,2.6264,2.6259]}

class ResultAccumulator:
    def __init__(self, v):
        self.values = [v]
        self.min = None
        self.max = None
        self.tot = None
        self.med = None
        self.mean = None
        self.var = None  # sample variance
        self.sdev = None  # sample standard deviation
        self.sdev_mean = None
        self.df = None
        self.lower99 = self.upper99 = None

    def add_data(self, v):
        self.values.append(v)

    def compute_stats(self):
        n = len(self.values)
        if n == 0:
            return
        self.df = n - 1

        self.values.sort()
        self.min = self.values[0]
        self.max = self.values[0]
        self.tot = 0.0
        for i in range(n):
            v = self.values[i]
            if v < self.min:
                self.min = min
            elif v > self.max:
                self.max = v
            if i == n / 2:
                self.med = v
            self.tot += v

        self.mean = self.tot / n
        dev_sq = [(v - self.mean)*(v - self.mean) for v in self.values]
        self.var = sum(dev_sq) / (n - 1)
        self.sdev = sqrt(self.var)
        self.sdev_mean = self.sdev / sqrt(n)
        (self.lower99, self.upper99) = self.conf(99)

    def conf(self, percent=99):
        n = len(self.values)
        if n > 100:
            print sys.stderr, "warning: limited t-table => overestimating error"
            n = 100
        t = T_DISTRIBUTION[percent][n]
        d = t * self.sdev_mean
        return (self.mean - d, self.mean + d)

    def __str__(self):
        fmt = 'min=%f max=%f tot=%f med=%f mean=%f var=%f sdev=%f sdev_mean=%f df=%u l99=%f u99=%f'
        return fmt % (self.min, self.max, self.tot, self.med, self.mean, self.var, self.sdev,
                      self.sdev_mean, self.df, self.lower99, self.upper99)

def gather_weight_data(wtype):
    # get the results
    results = {} # maps |V| to ResultAccumulator
    ds = DataSet.read_from_file(WeightResult, WeightResult.get_path_to(wtype))
    for data in ds.dataset.values():
        result = results.get(data.input().num_verts)
        if result is None:
            result = ResultAccumulator(data.mst_weight)
            results[data.input().num_verts] = result
        else:
            result.add_data(data.mst_weight)

    try:
        # open a file to output to
        fh = open(DATA_PATH + wtype + '.dat', 'w')

        # compute relevant stats and output them
        print >> fh, '#|V|\tLower\tAverage\tUpper  (Lower/Upper from 99% CI)'
        keys = results.keys()
        keys.sort()
        for num_verts in keys:
            r = results[num_verts]
            r.compute_stats()
            print >> fh, '%u\t%.3f\t%.3f\t%.3f' % (num_verts, r.lower99, r.mean, r.upper99)
        fh.close()
        return 0
    except IOError, e:
        print sys.stderr, "failed to write file: " + str(e)
        return -1

def main():
    try:
        os.makedirs(DATA_PATH)
    except OSError, e:
        pass
    gather_weight_data('edge')
    gather_weight_data('loc2')
    gather_weight_data('loc3')
    gather_weight_data('loc4')

if __name__ == "__main__":
    sys.exit(main())