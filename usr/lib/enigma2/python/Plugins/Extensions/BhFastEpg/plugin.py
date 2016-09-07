from Components.ActionMap import ActionMap
from Components.Label import Label
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.ChannelSelection import service_types_tv, service_types_radio
from Tools.Directories import fileExists
from Components.Sources.List import List
from Blackhole.BhEpgPanel import DeliteDownEpgNow, DeliteEpgChannels, nab_Get_EpgProvider
from os import system, rename as os_rename, remove as os_remove

from enigma import eServiceReference, eServiceCenter



class Bh_Fastepg_main(Screen):
	skin = """
	<screen position="center,center" size="500,250" title="Fast Epg">
		<widget name="lab1" position="20,40" size="460,30" font="Regular;24" halign="center" valign="center" transparent="1"/>
		<widget source="list" render="Listbox" position="40,90" zPosition="1" size="420,120" scrollbarMode="showOnDemand" transparent="1" >
			<convert type="StringList" />
		</widget>
	</screen>"""


	def __init__(self, session):
		Screen.__init__(self, session)

		self["lab1"] = Label("Available options")
		self["list"] = List(["Download ita OpenEpg", "Update ita epg channel list", "Download uk OpenEpg", "Update uk epg channel list"])
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"back": self.close,
			"ok": self.myDo
		})
		
		self.epgstatus = 1
		if fileExists("/etc/skyitepglock"):
			self.epgstatus = 0
			os_remove("/etc/skyitepglock")
			
		self.onClose.append(self.__onClose)
		
	def myDo(self):
		mchoice = self["list"].getIndex()
		if mchoice == 0:
			provider = "Sky-Ita"
			self.downEpg(provider)
		elif mchoice == 1:
			provider = "Sky-Ita"
			self.updateChans(provider)
		elif mchoice == 2:
			provider = "Sky-Uk"
			self.downEpg(provider)
		elif mchoice == 3:
			provider = "Sky-Uk"
			self.updateChans(provider)
				

	def downEpg(self, provider):
#		ret = self.checkChan(provider)
#		if ret == True:
		self.session.open(DeliteDownEpgNow, provider)
		
	def updateChans(self, provider):
#		ret = self.checkChan(provider)
#		if ret == True:
		self.session.open(DeliteEpgChannels, provider)

	def checkChan(self, provider):
		parts = nab_Get_EpgProvider(provider)
		chanref = parts[3]
		chname = parts[2]
		serviceHandler = eServiceCenter.getInstance()
		services = serviceHandler.list(eServiceReference('%s FROM BOUQUET "bouquets.tv" ORDER BY bouquet'%(service_types_tv)))
		bouquets = services and services.getContent("SN", True)
		for bouquet in bouquets:
			services = serviceHandler.list(eServiceReference(bouquet[0]))
			channels = services and services.getContent("SN", True)
			for channel in channels:
				if channel[0] == chanref:
					return True
		
		services = serviceHandler.list(eServiceReference('%s FROM BOUQUET "bouquets.radio" ORDER BY bouquet'%(service_types_radio)))
		bouquets = services and services.getContent("SN", True)
		for bouquet in bouquets:
			services = serviceHandler.list(eServiceReference(bouquet[0]))
			channels = services and services.getContent("SN", True)
			for channel in channels:
				if channel[0] == chanref:
					return True


		mes = "Sorry %s not found in your channel list" % (chname)
		self.session.open(MessageBox, mes, MessageBox.TYPE_INFO)
		return False

		
	def __onClose(self):
		if self.epgstatus == 0:
			out = open("/etc/skyitepglock", "w")
			out.write("Black Hole")
			out.close()
			

def main(session, **kwargs):
	session.open(Bh_Fastepg_main)
	


def Plugins(**kwargs):
	return PluginDescriptor(name="Fast Opentv Epg", description=_("Fast download of Opentv Epg"), where = PluginDescriptor.WHERE_PLUGINMENU, fnc=main)
