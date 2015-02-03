# coding:utf-8
'''
本模块的实现参考airtest:https://github.com/netease/airtest
'''

import re
import subprocess
import StringIO
from functools import partial

class Monitor(object):
    def __init__(self, serialno, pkgname):
        self._sno = serialno 
        self._pkg = pkgname
        self._ncpu = -1
        self._sys_memory = {}
        def _adb(*args):
            return subprocess.check_output(['adb', '-s', self._sno] + list(args))
        self.adb = _adb
        self.adbshell = partial(_adb, 'shell')

    def ncpu(self):
        ''' number of cpu '''
        if self._ncpu == -1:
	        output = self.adbshell('cat', '/proc/cpuinfo')
	        matches = re.compile('processor').findall(output)
        	self._ncpu = len(matches)
        return self._ncpu

    def cpu(self):
        ''' cpu usage, range must be in [0, 100] '''
        for line in StringIO.StringIO(self.adbshell('dumpsys', 'cpuinfo')):
            line = line.strip()
            # 0% 11655/im.yixin: 0% user + 0% kernel / faults: 10 minor
            if '/'+self._pkg+':' in line:
                return float(line.split()[0][:-1])/self.ncpu()
        return None

    def memory(self):
        '''
        @description details view: http://my.oschina.net/goskyblue/blog/296798

        @param package(string): android package name
        @return dict: {'VSS', 'RSS'} (unit KB)
        '''
        ret = {}
        # VSS, RSS
        for line in StringIO.StringIO(self.adbshell('ps')):
            if line and line.split()[-1] == self._pkg:
                # USER PID PPID VSIZE RSS WCHAN PC NAME
                values = line.split()
                if values[3].isdigit() and values[4].isdigit():
                    ret.update(dict(VSS=int(values[3]), RSS=int(values[4])))
                else:
                    ret.update(dict(VSS=-1, RSS=-1))
                break
        else:
            log.error("mem get: adb shell ps error")
            return {}

        # PSS
        # memout = self.adbshell('dumpsys', 'meminfo', self._pkg)
        # pss = 0
        # result = re.search(r'\(Pss\):(\s+\d+)+', memout, re.M)
        # if result:
        #     pss = result.group(1)
        # else:
        #     result = re.search(r'TOTAL\s+(\d+)', memout, re.M)
        #     if result:
        #         pss = result.group(1)
        # ret.update(dict(PSS=int(pss)))
        return ret

    def sys_memory(self):
        '''
        unit KB
        '''
        if not self._sys_memory:
            output = self.adbshell('cat', '/proc/meminfo')
            print output
            match = re.compile('MemTotal:\s*(\d+)\s*kB\s*MemFree:\s*(\d+)', re.IGNORECASE).match(output)
            if match:
                total = int(match.group(1), 10)
                free = int(match.group(2), 10)
            else:
                total, free = 0, 0
                self._sys_memory = dict(TOTAL=total, FREE=free)
            return self._sys_memory
