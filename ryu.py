# ryu-manager ryu1b.py
# dpctl dump-flows -O OpenFlow13

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.topology import event
import copy
from ryu.topology.api import get_switch, get_link
from ryu.ofproto import ether
import sys

class ryu1b(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(ryu1b, self).__init__(*args, **kwargs)
        self.podMax = 0
        self.checked = []

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        switch_id = datapath.id
        dpid = hex(switch_id)[2:].zfill(16)
        dpid = ':'.join(dpid[i:i+2] for i in range(0, len(dpid), 2))
        pod_no=dpid[16:17]     
        switch_no=dpid[19:20]