#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from select import poll, POLLIN
from mininet.node import Node
from time import time, sleep
from threading import Thread
import os
import random
from multiprocessing import Process

def createNetworkTopology():

    #Create a network and add nodes to it

    net = Mininet(controller=RemoteController)

    info( '*** Adding controller\n' )
    cA = net.addController('cA', controller=RemoteController, ip="127.0.0.1", port=6633)

    info( '*** Adding hosts\n' )
    h1 = net.addHost('h1', ip='10.1.1.1', mac='0A:01:00:00:00:01')
    h2 = net.addHost('h2', ip='10.1.1.2', mac='0A:02:00:00:00:02')
    h3 = net.addHost('h3', ip='10.1.2.1', mac='0B:01:00:00:00:01')
    h4= net.addHost('h4', ip='10.1.2.2', mac='0B:02:00:00:00:02')

    info( 'Adding switches\n' )
    s10 = net.addSwitch( 'sA', dpid='0000000000000010' ) 
    s11 = net.addSwitch( 's1', dpid='0000000000000001' )
    s12 = net.addSwitch( 's2', dpid='0000000000000002' )

    info( '*** Adding links\n' )
    net.addLink(h1,s11)
    net.addLink(h2,s11)
    
    net.addLink(h3,s12)
    net.addLink(h4,s12)
    
    net.addLink(s11,s10)
    net.addLink(s12,s10)
    


    info('*** Starting network\n')
    net.build()
    s10.start([cA])
    s11.start([cA])
    s12.start([cA])
    
    h1.cmd("python -m http.server 80 &")
    return net

def monitor(net):
  
  fds = [ host.stdout.fileno() for host in net.hosts ]
  poller = poll()
  
  for fd in fds:
    poller.register( fd, POLLIN )
    
  readable = poller.poll(1000)
  for fd, _mask in readable:
    node = Node.outToNode[ fd ]
    if node.name in ["h1", "h2"]:
      msg = node.monitor().strip()
      if "icmp" in msg:
        print ('%s:' % node.name, msg)
        print("***")
    elif  node.name in ["h1"]:
      print ('%s:' % node.name, node.monitor().strip())
      print("***")
  
    
def generateTraffic(net):
  
  hosts = net.hosts
  
  option = random.randint(0, 100)
  if option < 20:
    info("************\n")
    info("h2 starting ping to h1\n")
    info("************\n")
    hosts[1].cmd('ping -c 5', hosts[0].IP(), '&')
    
  elif option < 40:
    info("************\n")
    info("h3 starting ping to h1\n")
    info("************\n")
    hosts[2].cmd('ping -c 5', hosts[0].IP(), '&')
    
  elif option < 60:
    info("************\n")
    info("h2 starting wget to h1\n")
    info("************\n")
    hosts[1].cmd('wget ', hosts[0].IP(), '&')
    
  elif option < 80:
    info("************\n")
    info("h3 starting wget to h1\n")
    info("************\n")
    hosts[2].cmd('wget ', hosts[0].IP(), '&')
    
  elif option < 85:
    info("************************************\n")
    info("************************************\n")
    info("h4 starting attack to h1\n")
    info("************************************\n")
    info("************************************\n")
    hosts[3].cmd('hping3 --flood --udp', hosts[0].IP() , '&')
    sleep(5)
    
  elif option < 90:
    info("************************************\n")
    info("************************************\n")
    info("h3 starting attack to h2\n")
    info("************************************\n")
    info("************************************\n")
    hosts[2].cmd('hping3 --flood --udp', hosts[1].IP(), '&')  
    sleep(5)
    
  elif option < 95:
    info("************************************\n")
    info("************************************\n")
    info("h4 starting attack to h2\n")
    info("************************************\n")
    info("************************************\n")
    hosts[3].cmd('hping3 --flood --udp', hosts[1].IP(), '&')
    sleep(5)
    
  else:
    info("************************************\n")
    info("************************************\n")
    info("h3 starting attack to h1\n")
    info("************************************\n")
    info("************************************\n")
    hosts[2].cmd('hping3 --flood --udp', hosts[0].IP(), '&')
    sleep(5) 
    
if __name__ == '__main__':
    
    seconds = 60
    setLogLevel( 'info' )
    net = createNetworkTopology()
    sleep(1)
    endTime = time() + seconds
    while time() < endTime:
      sleep(random.uniform(1, 2))
      #monitor(net)
      os.system(' ./flood.sh')
      generateTraffic(net)
      
    
    os.system("rm ./index*")
    net.stop()  
    
    