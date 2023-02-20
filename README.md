# elephant
一个简单的服务器性能指标采集工具，能指定采集某个服务进程级的内存、CPU、IOPS等数据。



### Setup

```
wget https://github.com/ywjt/elephant/releases/download/v0.2.4-beta/elephant_v0.2.4-beta.tar.gz
tar -zxvf elephant_v0.2.4-beta.tar.gz -C /usr/local/
chmod 775 -R /usr/local/elephant
ln -s /usr/local/elephant/bin/elephantd /usr/local/bin/
ln -s /usr/local/elephant/etc /etc/elephant.d
```

```
elephantd help

Usage: elephantd 
                          
 Options:  
        daemon       start service for daemon. 
        start        start service for console. 
        [daemon|start] Args:                  
                --iface=  point to network interface. (default: eth0) 
                --disk=   point to disk partition. (default: vdb)   
                --lport=  point to monitoring ports. (default: 0)  
                or --proc=   point to monitoring process name. (default: )  
                or --lpid=   point to monitoring process id. (default: 0)  
                --istep=  second intervals of data acquisition. (default: 5)
                --delay=  minute intervals of auto close. (default: 10)
                --jid=    job id for record. (default: 0)
          Exps:  
                elephantd daemon --iface=eth0 --disk=vdb --lport="6666,6667" --proc="procA,procB" --istep=5 --delay=10   
        stop         stop daemon service. 
        status       show service run infomation. 
        watch        same as tailf, watching log output. 
        help         show this usage information. 
        version      show version information. 
 
```
