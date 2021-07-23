from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
import ryu.ofproto.ofproto_v1_3_parser as parser
import ryu.ofproto.ofproto_v1_3 as ofproto
from ryu.lib.packet import packet
from ryu.lib.packet import ether_types
from ryu.lib.packet import ethernet, arp, ipv4, ipv6, tcp

from cockpit import CockpitApp
from netaddr import IPAddress, IPNetwork

#tm task=security1

ETHERTYPES = {2048: "IPv4", 2054: "ARP", 34525: "IPv6"}
L4PROTO = {1: "ICMP", 4: "IP-in-IP", 6: "TCP", 17: "UDP"}

class SecureGateway(CockpitApp):
    ## Initialize SDN-App
    def __init__(self, *args, **kwargs):
        super(SecureGateway, self).__init__(*args, **kwargs)
        self.pkt_count = {}

    ## You already know this function from the lab
    def debug_output(self, dp, pkt, in_port):
        eth = pkt.get_protocol(ethernet.ethernet)

        self.pkt_count[dp.id] += 1

        print("/// [Switch {}]: PACKET-IN (#{}) on port: {}".format(dp.id, self.pkt_count[dp.id], in_port))
#        print("      SRC: {}, DST: {} --> {}".format(eth.src, eth.dst, ETHERTYPES[eth.ethertype]))

#        ## Info: IP Packet
#        if eth.ethertype == ether_types.ETH_TYPE_IP:
#            ip_pkt = pkt.get_protocol(ipv4.ipv4)
#            print("           {:17},      {:17} --> {}".format(ip_pkt.src, ip_pkt.dst, L4PROTO[ip_pkt.proto]))
#
#            ## Info: TCP Packet
##            if ip_pkt.proto == 6:
##                tcp_pkt = pkt.get_protocol(tcp.tcp)
##                print("      SRC-PORT: {}, DST-PORT: {}, SEQ: {}, ACK: {}".format(tcp_pkt.src_port, tcp_pkt.dst_port, tcp_pkt.seq, tcp_pkt.ack))

#        if eth.ethertype == ether_types.ETH_TYPE_ARP:
#            arp_pkt = pkt.get_protocol(arp.arp)
#            print("  [ARP] SRC-MAC: {}, SRC-IP: {}; DST-MAC: {} DST-IP: {}".format(arp_pkt.src_mac, arp_pkt.src_ip, arp_pkt.dst_mac, arp_pkt.dst_ip))



    ## When a new switch connects to the controller
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        dp = ev.msg.datapath

        self.pkt_count[dp.id] = 0

        ## some debug output
        print("")
        print("")
        print("/// Switch connected. ID: {}".format(dp.id))

        ## default "all to controller" flow
        match = parser.OFPMatch()
        action = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]
        self.program_flow(dp, match, action, priority=0, idle_timeout=0, hard_timeout=0)

        # flood ARP (this is just to get ping to work)
        match = parser.OFPMatch(
            eth_type = ether_types.ETH_TYPE_ARP
        )
        action = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        self.program_flow(dp, match, action, priority=1, idle_timeout=0, hard_timeout=0)

        # set up some proactive flows
        self.flow_project(dp)
        #self.flow_example_groups(dp)

    ## When a new packet comes in at the controller -- "PACKET-IN"
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        # all info is stored in the ev object, extract some relevant fields
        msg = ev.msg
        dp = msg.datapath
        in_port = msg.match["in_port"]
        data = msg.data
        pkt = packet.Packet(data)
        eth = pkt.get_protocol(ethernet.ethernet)
        ip = pkt.get_protocol(ipv4.ipv4)

        # ignore LLDP Packets
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        self.debug_output(dp, pkt, in_port)

    def flow_project(self, dp):
        # two flows allowing d1 <--> p1 traffic
        # allowing d1 --> p1
        match = parser.OFPMatch(
            eth_type = ether_types.ETH_TYPE_IP,
            ipv4_src = '21.21.0.0/8',
            ipv4_dst = '21.11.0.0/8'
        )
        action = [parser.OFPActionOutput(4)]
        self.program_flow(dp, match, action, priority=1, idle_timeout=0, hard_timeout=0)
   
        # allowing d1 <-- p1
        match = parser.OFPMatch(
            eth_type = ether_types.ETH_TYPE_IP,
            ipv4_src = '21.11.0.0/8',
            ipv4_dst = '21.21.0.0/8'
        )
        action = [parser.OFPActionOutput(1)]
        self.program_flow(dp, match, action, priority=1, idle_timeout=0, hard_timeout=0)
        
        # two flows allowing d2 <--> p1 traffic
        # allowing d2 --> p1
        match = parser.OFPMatch(
            eth_type = ether_types.ETH_TYPE_IP,
            ipv4_src = '21.22.0.0/8',
            ipv4_dst = '21.11.0.0/8'
        )
        action = [parser.OFPActionOutput(4)]
        self.program_flow(dp, match, action, priority=1, idle_timeout=0, hard_timeout=0)
        
        # allowing d2 <-- p1
        match = parser.OFPMatch(
            eth_type = ether_types.ETH_TYPE_IP,
            ipv4_src = '21.11.0.0/8',
            ipv4_dst = '21.22.0.0/8'
        )
        action = [parser.OFPActionOutput(2)]
        self.program_flow(dp, match, action, priority=1, idle_timeout=0, hard_timeout=0)

        # two flows allowing d1 <--> p2 traffic
        # allowing d1 --> p2
        match = parser.OFPMatch(
            eth_type = ether_types.ETH_TYPE_IP,
            ipv4_src = '21.21.0.0/8',
            ipv4_dst = '21.12.0.0/8'
        )
        action = [parser.OFPActionOutput(5)]
        self.program_flow(dp, match, action, priority=1, idle_timeout=0, hard_timeout=0)
        
        # allowing d1 <-- p2
        match = parser.OFPMatch(
            eth_type = ether_types.ETH_TYPE_IP,
            ipv4_src = '21.12.0.0/8',
            ipv4_dst = '21.21.0.0/8'
        )
        action = [parser.OFPActionOutput(1)]
        self.program_flow(dp, match, action, priority=1, idle_timeout=0, hard_timeout=0)
        
        # two flows allowing d2 <--> p2 traffic
        # allowing d2 --> p2
        match = parser.OFPMatch(
            eth_type = ether_types.ETH_TYPE_IP,
            ipv4_src = '21.22.0.0/8',
            ipv4_dst = '21.12.0.0/8'
        )
        action = [parser.OFPActionOutput(5)]
        self.program_flow(dp, match, action, priority=1, idle_timeout=0, hard_timeout=0)
        
        # allowing d2 <-- p2
        match = parser.OFPMatch(
            eth_type = ether_types.ETH_TYPE_IP,
            ipv4_src = '21.12.0.0/8',
            ipv4_dst = '21.22.0.0/8'
        )
        action = [parser.OFPActionOutput(2)]
        self.program_flow(dp, match, action, priority=1, idle_timeout=0, hard_timeout=0)
        
        # two flows allowing d1 <--> p3 traffic
        # allowing d1 --> p3
        match = parser.OFPMatch(
            eth_type = ether_types.ETH_TYPE_IP,
            ipv4_src = '21.21.0.0/8',
            ipv4_dst = '21.13.0.0/8'
        )
        action = [parser.OFPActionOutput(6)]
        self.program_flow(dp, match, action, priority=1, idle_timeout=0, hard_timeout=0)
        
        # allowing d1 <-- p3
        match = parser.OFPMatch(
            eth_type = ether_types.ETH_TYPE_IP,
            ipv4_src = '21.13.0.0/8',
            ipv4_dst = '21.21.0.0/8'
        )
        action = [parser.OFPActionOutput(1)]
        self.program_flow(dp, match, action, priority=1, idle_timeout=0, hard_timeout=0)
        
        # two flows allowing d2 <--> p3 traffic 
        # allowing d2 --> p3
        match = parser.OFPMatch(
            eth_type = ether_types.ETH_TYPE_IP,
            ipv4_src = '21.22.0.0/8',
            ipv4_dst = '21.13.0.0/8'
        )
        action = [parser.OFPActionOutput(6)]
        self.program_flow(dp, match, action, priority=1, idle_timeout=0, hard_timeout=0)
        
        # allowing d2 <-- p3
        match = parser.OFPMatch(
            eth_type = ether_types.ETH_TYPE_IP,
            ipv4_src = '21.13.0.0/8',
            ipv4_dst = '21.22.0.0/8'
        )
        action = [parser.OFPActionOutput(2)]
        self.program_flow(dp, match, action, priority=1, idle_timeout=0, hard_timeout=0)

        # two flows allowing d1 <--> p4 traffic
        # allowing d1 --> p4
        match = parser.OFPMatch(
            eth_type = ether_types.ETH_TYPE_IP,
            ipv4_src = '21.21.0.0/8',
            ipv4_dst = '21.14.0.0/8'
        )
        action = [parser.OFPActionOutput(7)]
        self.program_flow(dp, match, action, priority=1, idle_timeout=0, hard_timeout=0)
        
        # allowing d1 <-- p4
        match = parser.OFPMatch(
            eth_type = ether_types.ETH_TYPE_IP,
            ipv4_src = '21.14.0.0/8',
            ipv4_dst = '21.21.0.0/8'
        )
        action = [parser.OFPActionOutput(1)]
        self.program_flow(dp, match, action, priority=1, idle_timeout=0, hard_timeout=0)
        
        # two flows allowing d2 <--> p4 traffic
        # allowing d2 --> p4
        match = parser.OFPMatch(
            eth_type = ether_types.ETH_TYPE_IP,
            ipv4_src = '21.22.0.0/8',
            ipv4_dst = '21.14.0.0/8'
        )
        action = [parser.OFPActionOutput(7)]
        self.program_flow(dp, match, action, priority=1, idle_timeout=0, hard_timeout=0)
        
        # allowing d2 <-- p4
        match = parser.OFPMatch(
            eth_type = ether_types.ETH_TYPE_IP,
            ipv4_src = '21.14.0.0/8',
            ipv4_dst = '21.22.0.0/8'
        )
        action = [parser.OFPActionOutput(2)]
        self.program_flow(dp, match, action, priority=1, idle_timeout=0, hard_timeout=0)