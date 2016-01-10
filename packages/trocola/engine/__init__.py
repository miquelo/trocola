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
Package with engine classes.

.. class:: EngineTask

   Scheduled task for engine operations.
   
   .. function:: result(timeout)
   
.. class:: EngineEventQueue

   Queue for engine task events.
   
   .. function:: dispatch(task, name, value)
   
      Function used for task event dispatching.
      
      :param EngineTask task:
         Source task.
      :param string name:
         Event type name.
      :param value:
         Event value.
"""

import concurrent.futures

class NoneOutput:

	"""
	Output to *null device*.
	"""
	
	def write(self, text):
	
		"""
		Return length of the given text.
		"""
		
		return len(text)
		
class NoneEngineEventQueue:

	"""
	Ignore event queue for an :class:`Engine`.
	"""
	
	def dispatch(self, task, name, value):
	
		"""
		Does nothing.
		"""
		
		pass
		
class Engine:
		
	"""
	The engine of the management tool.
	
	:param Resource state_res:
	   State resource of the engine.
	:param EngineEventQueue event_queue:
	   Event queue used for dispatching engine task events.
	:param out:
	   Engine main output.
	:param err:
	   Engine error ouput.
	:param int max_workers:
	   Maximum number of workers used by engine executor.
	"""
	
	def __init__(
		self,
		state_res,
		event_queue=NoneEngineEventQueue(),
		out=NoneOutput(),
		err=NoneOutput(),
		max_workers=10
	):
	
		self.__state_res = state_res
		self.__event_queue = event_queue
		self.__out = out
		self.__err = err
		self.__executor = concurrent.futures.ThreadPoolExecutor(max_workers)

