# coding:utf-8
'''
本模块的实现参考airtest:https://github.com/netease/airtest
'''

import subprocess
import paramiko
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('ios_log')
logging.getLogger('paramiko').setLevel(logging.WARNING)

class Monitor(object):
    def __init__(self, ip, appname):
        self._ssh = paramiko.client.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._ssh.connect(ip, username='root', password='mangome')
        self._ip = ip 
        self._name = appname
        self._ncpu = -1
        self._pid = -1
        def _sh(*args):
            cmd = args[0] if len(args) == 1 else subprocess.list2cmdline(args)
            stdin, out, err = self._ssh.exec_command(cmd)
            return out.read()
        self.sh = _sh

    def ncpu(self):
        ''' number of cpu '''
        if self._ncpu == -1:
        	out = self.sh('sysctl', 'hw.ncpu')
        	self._ncpu = int(out.strip().split()[1])
        return self._ncpu

    def pid(self):
    	if self._pid == -1:
	        name = '/['+self._name[0]+']'+self._name[1:]  # change "grep name" -> "grep [n]ame"
	        output = self.sh('ps -eo pid,command | grep '+name)
        	self._pid = int(output.split()[0])
        return self._pid

    def cpu(self):
        ''' cpu usage, range must be in [0, 100] '''
        pid = self.pid()
        output = self.sh('ps -o pcpu -p %d | tail -n+2' % pid)
        cpu = output.strip()
        return float(cpu)/self.ncpu()
        

    def memory(self):
        '''
        @description details view: http://my.oschina.net/goskyblue/blog/296798

        @param package(string): android package name
        @return dict: {'VSS', 'RSS'} (unit KB)
        '''
        output = self.sh('ps -o pmem,rss,vsz -p %d | tail -n+2' % self.pid())
        # pmem 是内存占用率，这个数值先不用
        pmem, rss, vss = output.split()
        return dict(VSS=int(vss), RSS=int(rss))

if __name__ == '__main__':
    monitor = Monitor('192.168.213.164', 'xc_daily') 
    print 'cpu:{cpu}, memory:{memory}'.format(
        cpu=monitor.cpu(), memory=monitor.memory())