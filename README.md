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
[root@test ~]# elephantd help

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

```
[root@test ~]# elephantd start --iface=eth0 --disk=sda --lport="11443" --istep=3 --delay=10
Args Set: (eth0 sda ['start'] 10021 0 3 10) 
Running: successd
{'p_netpack': [{'18564_docker-proxy': {'recv': 7, 'send': 8}, '18556_docker-proxy': {'recv': 1, 'send': 2}}], 'ioutil': 0.0, 'cpu_idle': 99.3, 'mem_free': 22643351552, 'p_io': [{'18564_docker-proxy': {'read': 0, 'write': 0}, '18556_docker-proxy': {'read': 0, 'write': 0}}], 'jid': 0, 'p_memuse': [{'18564_docker-proxy': 10256384, '18556_docker-proxy': 10223616}], 'uptime': 1676878713, 'p_cpuuse': [{'18564_docker-proxy': 0.0, '18556_docker-proxy': 0.0}], 'p_netflow': [{'18564_docker-proxy': {'recv': 454, 'send': 474}, '18556_docker-proxy': {'recv': 71, 'send': 143}}], 'p_conns': [{'18564_docker-proxy': 0, '18556_docker-proxy': 0}], 'netpack': {'recv': 1, 'send': 3}, 'netflow': {'recv': 71, 'send': 416}, 'loadavg': '0.04'}
{'p_netpack': [{'18564_docker-proxy': {'recv': 0, 'send': 0}, '18556_docker-proxy': {'recv': 0, 'send': 0}}], 'ioutil': 0.0, 'cpu_idle': 99.1, 'mem_free': 22647062528, 'p_io': [{'18564_docker-proxy': {'read': 0, 'write': 0}, '18556_docker-proxy': {'read': 0, 'write': 0}}], 'jid': 0, 'p_memuse': [{'18564_docker-proxy': 10256384, '18556_docker-proxy': 10223616}], 'uptime': 1676878719, 'p_cpuuse': [{'18564_docker-proxy': 0.0, '18556_docker-proxy': 0.0}], 'p_netflow': [{'18564_docker-proxy': {'recv': 0, 'send': 0}, '18556_docker-proxy': {'recv': 0, 'send': 0}}], 'p_conns': [{'18564_docker-proxy': 0, '18556_docker-proxy': 0}], 'netpack': {'recv': 0, 'send': 0}, 'netflow': {'recv': 0, 'send': 0}, 'loadavg': '0.11'}

```
