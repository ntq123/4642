from mininet.net import Mininet
from mininet.topo import Topo
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import RemoteController, OVSSwitch
from functools import partial

k=int(input('Enter value of k '))
protocol = 'OpenFlow13'

#sudo mn -c
#sudo mn --custom Question1b.py --topo mytopo --switch ovsbr,stp=1
#py net.waitConnected()
#sudo mn --arp --custom Question1b.py --topo mytopo --mac --switch ovs --controller remote
#ryu-manager ryu.app.simple_switch_13 ryu.app.ofctl_rest
#ryu-manager ryu.app.simple_switch_stp ryu.app.ofctl_rest
#h0 ping h1 -c 2

class MyTopo(Topo):
    #Init method is a constructor
    def __init__(self, n=4, **opts):
        #Initialise topology and default options
        Topo.__init__(self, **opts)
        self.dpidi=1
        self.dpidj=1
        self.pod=0
        self.switch=0
        self.ID = 2
        #add core switches
        self.CoreSwitch=[]
        self.addCoreSwitches()        
        #add aggregation switches
        self.AggregationSwitch=[]
        self.addAggregationSwitches()
        #add edge switches
        self.EdgeSwitch=[]
        self.addEdgeSwitches()
        #add hosts
        self.Host=[]
        self.addHosts()
        #add links
        self.TotalLink=0
        self.addLinks() 

    #Add core switches
    def addCoreSwitches(self):
        #There are (k/2)^2 k-port core switches
        for x in range(0,(k/2)**2):
            self.CoreSwitch.append(self.addSwitch( 'cs'+str(x),dpid='0000000000' + self.convertk2Hex() + self.converti2Hex() + self.convertj2Hex(), protocols=protocol))
            if(self.dpidj >= k/2):
                self.dpidj = 1 
                if(self.dpidi >= k/2):
                    self.dpidi = 1 
                else:
                   self.dpidi +=1
            else:
                self.dpidj += 1
                               
        self.dpidi = 1
        self.dpidj = 1

    #Add aggregation switches
    def addAggregationSwitches(self):
        self.switch = k/2      
        #There are k pods and each pod has k/2 aggregation switches
        for x in range(0, k*k/2):
            self.AggregationSwitch.append(self.addSwitch( 'as'+str(x),dpid='0000000000' + self.convertPod2Hex() + self.convertSwitch2Hex() + '01', protocols=protocol))
            if(self.switch >= k-1):
                self.switch = k/2 
                self.pod += 1
            else:
                self.switch += 1
        self.switch = 0
        self.pod = 0

    #Add edge switches
    def addEdgeSwitches(self):
        #There are k pods and each pod has k/2 edge switches
        for x in range(0, k*k/2):
            self.EdgeSwitch.append(self.addSwitch( 'es'+str(x),dpid='0000000000' + self.convertPod2Hex() + self.convertSwitch2Hex() + '01', protocols=protocol))
            if(self.switch >= k/2-1):
                self.switch = 0 
                self.pod += 1
            else:
                self.switch += 1
        self.switch = 0
        self.pod = 0

    #Add hosts
    def addHosts(self):
        #There are k pods, which each having k/2 edges, with each having k/2 hosts
        for x in range(0,(k**3)/4):
            ipAd = '10' + '.' + str(self.pod) + '.' + str(self.switch) + '.' + str(self.ID)
            self.Host.append(self.addHost('h'+str(x), ip= ipAd))
            if(self.ID >= k/2+1):
                self.ID = 2 
                if(self.switch >= k/2-1):
                    self.switch = 0
                    self.pod += 1
                else:
                    self.switch +=1
            else:
                self.ID += 1
        self.switch = 0
        self.pod = 0
        self.ID = 2

    #Add links 
    def addLinks(self):
        #connecting edge switches to hosts 
        for x in range(0,k*k/2):
            for y in range(0,k/2):
                #ith host in a subnet should be connected to the ith port of the edge switch
                self.addLink( self.EdgeSwitch[x], self.Host[y+(k/2)*x], y+1, 1)
#                print("Port number information")
#                print(self.port(self.EdgeSwitch[x], self.Host[y+(k/2)*x]))                
                self.TotalLink+=1

        #connecting aggregation switches to edge switches 
        for x in range(0,k):
            for y in range(0,k/2):
                for z in range(0,k/2):                    
                    #k/2+i th port of edge siwtch is connected to k/2+i th aggregation switch jth port
                    self.addLink( self.AggregationSwitch[y+(k/2)*x], self.EdgeSwitch[z+(k/2)*x], z+1, (k/2)+y+1 )
#                    print("Port number information")
#                    print(self.port(self.AggregationSwitch[y+(k/2)*x], self.EdgeSwitch[z+(k/2)*x]))      
                    self.TotalLink+=1

#         #connecting core switches to aggregation switches
        for x in range(0,k):
            for y in range(0,k/2):
                for z in range(0,k/2): 
                    #ith port of the core switch is connected to the ith pod to switches on k/2 strides
                    self.addLink( self.CoreSwitch[z+(y*k/2)], self.AggregationSwitch[x*(k/2)+y], x+1, (k/2)+z+1 )
#                    print("Port number information")
#                    print(self.port(self.CoreSwitch[z+(y*k/2)], self.AggregationSwitch[x*(k/2)+y]))

                    self.TotalLink+=1

    #Convert k to 2 digit hex
    def convertk2Hex(self):
        paddTo2=''    
        temp=2-len(hex(k)[2:])
        for i in range(0,temp):
            paddTo2+= '0'
        return paddTo2+hex(k)[2:]

    #Convert i to 2 digit hex
    def converti2Hex(self):
        paddTo2=''    
        temp=2-len(hex(self.dpidi)[2:])
        for i in range(0,temp):
            paddTo2+= '0'
        return paddTo2+hex(self.dpidi)[2:]

    #Convert j to 2 digit hex
    def convertj2Hex(self):
        paddTo2=''    
        temp=2-len(hex(self.dpidj)[2:])
        for i in range(0,temp):
            paddTo2+= '0'
        return paddTo2+hex(self.dpidj)[2:]

    #Convert pod to 2 digit hex
    def convertPod2Hex(self):
        paddTo2=''    
        temp=2-len(hex(self.pod)[2:])
        for i in range(0,temp):
            paddTo2+= '0'
        return paddTo2+hex(self.pod)[2:]

    #Convert switch to 2 digit hex
    def convertSwitch2Hex(self):
        paddTo2=''    
        temp=2-len(hex(self.switch)[2:])
        for i in range(0,temp):
            paddTo2+= '0'
        return paddTo2+hex(self.switch)[2:]

    #Convert ID to 2 digit hex
    def convertID2Hex(self):
        paddTo2=''    
        temp=2-len(hex(self.ID)[2:])
        for i in range(0,temp):
            paddTo2+= '0'
        return paddTo2+hex(self.ID)[2:]

def runTopo():

    #Create an instance of our topology
    topo = MyTopo()

    #Create a netowrk based on the topology using OVS and controlled by a remote controller
    net = Mininet(
        topo=topo,
        controller=lambda name: RemoteController( 'c0', ip='127.0.0.1'),
        autoSetMacs=True )

    net.start()
    CLI(net)
    net.stop()

if __name__ == '_main_':
    setLogLevel('info')
    runTopo()


topos = { 'mytopo': ( lambda: MyTopo() ) }
