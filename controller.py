from operator import attrgetter
import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
import subprocess

class SimpleMonitor(simple_switch_13.SimpleSwitch13):
    
    POLLING_INTERVAL = 2
    
    ATTACK_THRESHOLD = 10000

    STATS_REPORT = False

    def __init__(self, *args, **kwargs):
        super(SimpleMonitor, self).__init__(*args, **kwargs)
        # Datapath flows known by statistics polling
        self.datapaths = {}
	      # Creates thread for polling flow and port statistics
        self.monitor_thread = hub.spawn(self._monitor)          

        self.flow_rates = {"sA": [{}, {}],
                           "s1": [{}, {}, {}],
                           "s2": [{}, {}, {}]}
        
        self.portMaps = {"sA": ["s1", "s2"],
                         "s1": ["h1", "h2", "sA"],
                         "s2": ["h3", "h4", "sA"]
                         }

        self.dpids = {0x10: "sA",
                      0x1: "s1",
                      0x2: "s2"
                      }
                      
        self.hosts = ["h1", "h2", "h3", "h4"]

        self.flow_byte_counts = {}
        

    # Convert from byte count delta to bitrate
    @staticmethod
    def bitrate(bytes):
        return bytes * 8.0 / (SimpleMonitor.POLLING_INTERVAL * 1000)

    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if not datapath.id in self.datapaths:
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                del self.datapaths[datapath.id]

    def _monitor(self):
        while True:
            self.attacks = {}
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(SimpleMonitor.POLLING_INTERVAL)

    def _request_stats(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):

      body = ev.msg.body
      # Get id of datapath for which statistics are reported as int
      dpid = int(ev.msg.datapath.id)
      switch = self.dpids[dpid]

      if SimpleMonitor.STATS_REPORT:
        print ("-------------- Flow stats for switch ", switch, "-------------------")
        # Iterate through all statistics reported for the flow

      for stat in sorted([flow for flow in body if flow.priority == 1],
                           key=lambda flow: (flow.match['in_port'],
                                             flow.match['eth_dst'])):
          in_port = stat.match['in_port']
          out_port = stat.instructions[0].actions[0].port
          eth_dst = stat.match['eth_dst']
          eth_src = stat.match['eth_src']

          key = (dpid, in_port, eth_dst, out_port)
          rate = 0

          if key in self.flow_byte_counts:
            cnt = self.flow_byte_counts[key]
            rate = self.bitrate(stat.byte_count - cnt)
            
          self.flow_byte_counts[key] = stat.byte_count

          self.flow_rates[switch][in_port - 1][str(eth_dst)] = rate
          
          if SimpleMonitor.STATS_REPORT:
            print ("In Port %8x Eth Src %17s Eth Dst %17s Out Port %8x Bitrate %f" % (in_port, eth_src, eth_dst, out_port, rate))
            
          if SimpleMonitor.STATS_REPORT:
            print ("--------------------------------------------------------------------------------------")

          # If the bandwith for flow is higher than the threshold limit, we mark it as vicitim
          try:
            if rate > SimpleMonitor.ATTACK_THRESHOLD:
              victim = str(eth_dst)
              victimHost, victimSwitch, victimPort = self.getVictim(victim)
              attacker = self.getAttacker(victim)
              if attacker not in self.attacks:
                self.attacks[attacker] = list()
                if victim not in self.attacks[attacker] and attacker:
                  print("*********************************Attack detected*******************************")
                  print("Rate: ",rate)
                  print("Identified victim: MAC %s Host %s Switch %s Port %s" % (victim, victimHost, victimSwitch, victimPort))        
                  print("Attacker: ",attacker)
                  self.attacks[attacker].extend(victim)
          except:
            continue
         

    def getVictim(self, victim):
      victimHost = "h" + victim[16]
      for switch in self.portMaps:
        for port in range(len(self.portMaps[switch])):
          if self.portMaps[switch][port] == victimHost:
            return victimHost, switch, str(port)

    def getAttacker(self, victim):
     for switch in self.flow_rates:
      for port in range(len(self.flow_rates[switch])):
       if victim not in self.flow_rates[switch][port]:
         continue
       if self.flow_rates[switch][port][victim] > SimpleMonitor.ATTACK_THRESHOLD:
         attacker = self.portMaps[switch][port]
         if attacker in self.hosts:
           return attacker
           #print("Attacker: ",attacker)
                