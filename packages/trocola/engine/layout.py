#
# This file is part of TROCOLA.
#
# TROCOLA is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TROCOLA is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TROCOLA.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Module for layout definition.
"""

from trocola.engine import image

# from trocola.module import resolver
# from trocola.module import util

class Layout:

	"""
	Layout.
	"""
	
	def __init__(self):
	
		self.__executions = []
		
	@property
	def executions(self):
	
		"""
		List of :class:`ContainerExecution` values.
		"""
		
		return self.__executions
		
class Container:

	"""
	Container.
	
	:param trocola.engine.image.ImageRef image_ref:
	   Container image reference.
	"""
	
	def __init__(self, image_ref):
	
		self.__image_ref = image_ref
		self.__ports = []
		
	@property
	def image_ref(self):
	
		"""
		Image reference.
		"""
		
		return self.__image_ref
		
	@property
	def ports(self):
	
		"""
		List of :class:`ContainerPort` values.
		"""
		
		return self.__ports
		
class ContainerPort:

	"""
	Port of container service.
	
	:param string value:
	   Port name.
	:param string service_name:
	   Service name.
	"""
	
	def __init__(self, name, service_name):
	
		self.__name = name
		self.__service_name = service_name
		
	@property
	def name(self):
	
		"""
		Port name.
		"""
		
		return self.__name
		
	@property
	def service_name():
	
		"""
		Service name.
		"""
		
		return self.__service_name
		
class ContainerExecution:
	
	"""
	Container execution for a platform.
	
	:param Container cont:
	   Container involved in this setup process.
	:param string plat_name:
	   Name of the target platform.
	:param ContainerExecutionConfig config:
	   Setup configuration.
	"""
	
	def __init__(self, cont, plat_name, config=None):
	
		self.__container = cont
		self.__platform_name = plat_name
		self.__configuration = config
		
	@property
	def container(self):
	
		"""
		Involved container.
		"""
		
		return self.__container
		
	@property
	def platform_name(self):
	
		"""
		Target platform name.
		"""
		
		return self.__platform_name
		
	@property
	def configuration(self):
	
		"""
		Setup configuration.
		"""
		
		return self.__configuration
		
class ContainerExecutionConfig:

	"""
	Container execution configuration.
	"""
	
	def __init__(self):
	
		self.__volumes = []
		
	@property
	def volumes(self):
	
		"""
		List of :class:`VolumeMount` values.
		"""
		
		return self.__volumes
		
class Volume:

	"""
	Volume.
	
	:param string stor_type:
	   Storage type.
	:param int size:
	   Available size.
	"""
	
	def __init__(self, stor_type, size):
	
		self.__storage_type = stor_type
		self.__size = size
		
	@property
	def storage_type(self):
	
		"""
		Storage type.
		"""
		
		return self.__storage_type
		
	@property
	def size(self):
	
		"""
		Available size.
		"""
		
		return self.__size
		
class VolumeMount:

	"""
	Volume mount inside a container.
	
	:param Volume volume:
	   Volume to mount.
	:param string path:
	   Mount path inside container.
	"""
	
	def __init__(self, volume, path):
	
		self.__volume = volume
		self.__path = path
		
	@property
	def volume(self):
	
		"""
		Volume to mount.
		"""
		
		return self.__volume
		
	@property
	def path(self):
	
		"""
		Mount path.
		"""
		
		return self.__path
		
def __load_size(data):

	unit = data[-1]
	if unit.isdigit():
		fact = 0
		index = 1
	elif unit == "B":
		fact = 0
		index = 2
	elif c == "K":
		fact = 1
		index = 2
	elif c == "M":
		fact = 2
		index = 2
	elif c == "G":
		fact = 3
		index = 2
	elif c == "T":
		fact = 4
		index = 2
	else:
		raise Exception("Invalid size unit '{}'".format(data))
	
	num_str = data[0:-index]
	num = eval(num_str)
	if type(num) != int:
		raise Exception("Invalid size integer '{}'".format(num_str))
	for i in range(fact):
		num = num * 1024
	return num
	
def __load_execution(data, containers, volumes):

	cont = containers[data["container"]]
	plat_name = data["platform"]
	if "configuration" in exec_data:
		config = ContainerExecutionConfig()
		config_data = exec_data["configuration"]
		if "volumes" in config_data:
			for vol_data in config_data["volumes"]:
				vol = volumes[vol_data["volume"]]
				path = vol_data["path"]
				config.volumes.append(VolumeMount(vol, path))
	else:
		config = None
	return ContainerExecution(cont, plat_name, config)
	
def load(layout_data, props=None):

	"""
	Load a layout from the given data dictionary.
	
	:param dict layout_data:
	   Dictionary with layout data.
	:param props:
	   Optional properties.
	:rtype:
	   Layout
	:return:
	   The loaded layout.
	   
	An example:
	
	.. code-block:: json
	
	   {
	       "properties": {
	           "main_platform": {
	               "name": "local",
	               "enabled": "true"
	           }
	       },
	       "layout": {
	           "containers": {
	               "members-service-01": {
	                   "image": {
	                       "name": "members-service",
	                       "version": "2.3"
	                   },
	                   "ports": [
	                       {
	                           "name": "http",
	                           "service": "members"
	                       }
	                   ]
	               }
	           },
	           "volumes": {
	               "members-volume-01": {
	                   "storage": "local",
	                   "size": "8Gb"
	               }
	           },
	           "executions": [
	               {
	                   "container": "members-service-01",
	                   "platform": "#{main_platform['name']}",
	                   "configuration": {
	                       "volumes": [
	                           {
	                               "volume": "members-volume-01",
	                               "path": "/var/database"
	                           }
	                       ]
	                   },
	                   "enabled": "#{main_platform['enabled']}"
	               }
	           ]
	       }
	   }
	   
	Data dictionary will be treated as a resolvable one.
	"""
	
	layout_props = {}
	if "properties" in layout_data:
		util.merge_dict(layout_props, layout_data["properties"])
	if props is not None:
		util.merge_dict(layout_props, props)
	layout_def = resolver.resolvable(layout_data["layout"], layout_props)
	
	containers = {}
	if "containers" in layout_def:
		for cont_key, cont_data in layout_def["containers"].items():
			image_data = cont_data["image"]
			if "version" in image_data:
				image_version = image_data["version"]
			else:
				image_version = None
			image_ref = image.ImageRef(image_data["name"], image_version)
			cont = Container(image_ref)
			if "ports" in cont_data:
				for port_data in cont_data["ports"]:
					name = port_data["name"]
					serv_name = port_data["service"]
					cont.ports.append(ContainerPort(name, serv_name))
			containers[cont_key] = cont
			
	volumes = {}
	if "volumes" in layout_def:
		for vol_key, vol_data in layout_def["volumes"].items():
			stor_type = vol_data["storage"]
			size = __load_size(vol_data["size"])
			volumes[vol_key] = Volume(stor_type, size)
			
	layout = Layout()
	if "executions" in layout_def:
		for exec_data in layout_def["executions"]:
			if "enabled" not in exec_data or eval(exec_data["enabled"]):
				execut = __load_execution(exec_data, containers, volumes)
				layout.executions.append(execut)
	return layout

