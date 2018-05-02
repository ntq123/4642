#!/usr/bin/python                                                                            
                                                                                             
from mininet.topo import Topo
class MyTopo(Topo):
	def __init__(self):
		Topo.__init__( self )
		print('ELEC4642,LAB2')
		k=input('please input the parameter k:')
		for a in range(k/2):
			for b in range(k/2):
				self.addSwitch('core_%s_%s'%(a,b),dpid='0000000000%s0%s0%s'%(k,a+1,b+1))
		for i in range(k):
			for j in range(k/2):
				pod01=format(i,'02x')
				switch01=format(j+k/2,'02x')
				switch02=format(j,'02x')
				self.addSwitch('aggr_%s_%s'%(i,j),dpid='0000000000%s%s01'%(pod01,switch01))
				self.addSwitch('edge_%s_%s'%(i,j),dpid='0000000000%s%s01'%(pod01,switch02))
		for i in range(k):
			for j in range(k/2):
				for m in range(k/2):
					self.addHost('host_%s_%s_%s'%(i,j,m),ip='10.%s.%s.%s'%(i,j,m+2))
		for a in range(k/2):
			for b in range(k/2):
				for c in range(k):
					core01='core_%s_%s'%(a,b)
					aggr01='aggr_%s_%s'%(c,a)
					self.addLink(core01,aggr01,port1=c,port2=k/2-b-1)
		for n in range(k):
			for e in range(k/2):
				for f in range(k/2):
					aggr02='aggr_%s_%s'%(n,e)
					edge02='edge_%s_%s'%(n,f)
					self.addLink(aggr02,edge02,port1=k/2+f,port2=e)
		for n in range(k):
			for e in range(k/2):
				for f in range(k/2):
					edge03='edge_%s_%s'%(n,e)
					host03='host_%s_%s_%s'%(n,e,f)
					self.addLink(edge03,host03,port1=k/2+f)
topos = { 'mytopo': ( lambda: MyTopo() ) }
