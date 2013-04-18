#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import time
import glob
import re
import os

class RotateLogsTailer(object):
    def __init__(self, basename):
        self.basename = basename

    def follow(self):
        following_ts = self.find_latest_ts()
        if not following_ts:
            return
        fd = self.openlog(following_ts, True)
        while True:
            line = fd.readline()
            if not line:
                ts = self.find_latest_ts()
                if ts > following_ts:
                    following_ts = ts
                    fd = self.rotatelog(fd, ts)
                else:
                    time.sleep(1.0)
                continue
            yield line

    def openlog(self, ts, end=False):
        f = open(self.basename + '.' + str(ts))
        if end:
            f.seek(0, 2)
        return f

    def rotatelog(self, file, ts):
        file.close()    # XXX file 이 제대로 닫히는지 확인 필요
        return self.openlog(ts)

    def find_latest_ts(self):
        latest_ts = 0
        for entry in glob.glob(self.basename + '.*'):
            if not os.path.isfile(entry):
                continue
            mat = re.match(r'^\.([0-9]{10})$', entry[-11:])
            if mat:
                ts = int(mat.group(1))
                if ts > latest_ts:
                    latest_ts = ts
        return latest_ts


for line in RotateLogsTailer(sys.argv[1]).follow():
    sys.stdout.write(line)
