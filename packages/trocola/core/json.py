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

import io

class ReaderException(BaseException):

	"""
	Reader exception.
	
	:param args:
	   Exception arguments.
	"""
	
	def __init__(self, args):
	
		super().__init__(args)
		
class Reader:

	"""
	Abstract reader for JSON source.
	
	It can be iterated in order to fetch its child :class:`Reader` items.
	
	:param src:
	   JSON source.
	"""
	
	def __init__(self, src):
	
		self.__src = src
		
	def __iter__(self):
	
		c = self.read(1)
		while len(c) > 0:
			yield from self.next(c)
			c = self.read(1)
			
	def isnumber(self):
	
		"""
		Determines if it is a number reader.
		
		:rtype:
		   bool
		:return:
		   True if it is a number reader. False otherwise.
		"""
		
		return False
		
	def isstr(self):
	
		"""
		Determines if it is an string reader.
		
		:rtype:
		   bool
		:return:
		   True if it is an string reader. False otherwise.
		"""
		
		return False
		
	def islist(self):
	
		"""
		Determines if it is a list reader.
		
		:rtype:
		   bool
		:return:
		   True if it is a list reader. False otherwise.
		"""
		
		return False
		
	def isdict(self):
	
		"""
		Determines if it is a dictionary reader.
		
		:rtype:
		   bool
		:return:
		   True if it is a dictionary reader. False otherwise.
		"""
		
		return False
		
	def read(self, count):
	
		"""
		Read next *count* characters from source.
		
		:param int count:
		   Number of characters to be read.
		:rtype:
		   string
		:return:
		   String containing read characters.
		"""
		
		return self.__src.read(count)
		
class NumberReader(Reader):

	"""
	Reader for JSON numbers.
	
	:param src:
	   JSON source.
	:param string first_c:
	   First character.
	:param concluded_fn:
	   Function called when number reading has been concluded.
	"""
	
	def __init__(self, src, first_c, concluded_fn=None):
	
		super().__init__(src)
		self.__first_c = first_c
		if concluded_fn is None:
			self.__concluded_fn = self.__concluded_pass
		else:
			self.__concluded_fn = concluded_fn
		self.__read = self.__read_first
		self.__next = self.__next_default
		self.__dot_valid = True
		
	def __concluded_pass(self, c):
	
		pass
		
	def __read_first(self, count):
	
		self.__read = self.__read_default
		result = io.StringIO()
		result.write(self.__first_c)
		if count > 1:
			result.write(super().read(count - 1))
		return result.getvalue()
		
	def __read_default(self, count):
	
		return super().read(count)
		
	def __read_concluded(self, count):
	
		return ""
		
	def __next_default(self, c):
	
		if c.isspace() or c in ( ",", ")", "}" ):
			self.__read = self.__read_concluded
			self.__concluded_fn(c)
			yield from ()
		elif c.isdigit():
			yield c
		elif c == ".":
			if self.__dot_valid:
				self.__dot_valid = False
				self.__value.write(c)
				yield c
			else:
				self.__raise_illegal_char(c)
		else:
			self.__raise_illegal_char(c)
			
	def __raise_illegal_char(self, c):
	
		raise ReaderException("Illegal character '{}'".format(c))
		
	def isnumber(self):
	
		"""
		Determines if it is a number reader.
		
		:rtype:
		   bool
		:return:
		   True because it is a number reader.
		"""
		
		return True
		
	def value(self):
	
		"""
		Number value.
		
		:return:
		   The number value.
		"""
		
		val_io = io.StringIO()
		for c in self:
			val_io.write(c)
		val = val_io.getvalue()
		num = eval(val)
		if type(num) not in ( int, float ):
			raise ReaderException("Not a number: '{}'".format(val))
		return num
		
	def read(self, count):
	
		"""
		Read next *count* characters from source.
		
		:param int count:
		   Number of characters to be read.
		:rtype:
		   string
		:return:
		   String containing read characters.
		"""
		
		return self.__read(count)
		
	def next(self, c):
	
		"""
		Yield next item, if any, after reading the given character.
		
		:param string c:
		   Read character.
		:yield:
		   Next item, if any.
		"""
		
		yield from self.__next(c)
		
class StringReader(Reader):

	"""
	Reader for JSON strings.
	
	:param src:
	   JSON source.
	"""
	
	def __init__(self, src):
	
		super().__init__(src)
		self.__read = self.__read_default
		self.__next = self.__next_default
		
	def __read_default(self, count):
	
		return super().read(count)
		
	def __read_concluded(self, count):
	
		return ""
		
	def __next_default(self, c):
	
		if c == "\\":
			self.__next = self.__next_backslash
			yield from ()
		elif c == "\"":
			self.__read = self.__read_concluded
			yield from ()
		else:
			yield c
			
	def __next_backslash(self, c):
	
		self.__next = self.__next_default
		yield eval("\"\\{}\"".format(c))
		
	def isstr(self):
	
		"""
		Determines if it is an string reader.
		
		:rtype:
		   bool
		:return:
		   True because it is an string reader.
		"""
		
		return True
		
	def value(self):
	
		"""
		String value.
		
		:rtype:
		   string
		:return:
		   The string value.
		"""
		
		val_io = io.StringIO()
		for c in self:
			val_io.write(c)
		return val_io.getvalue()
		
	def read(self, count):
	
		"""
		Read next *count* characters from source.
		
		:param int count:
		   Number of characters to be read.
		:rtype:
		   string
		:return:
		   String containing read characters.
		"""
		
		return self.__read(count)
		
	def next(self, c):
	
		"""
		Yield next item, if any, after reading the given character.
		
		:param string c:
		   Read character.
		:yield:
		   Next item, if any.
		"""
		
		yield from self.__next(c)
		
class ListReader(Reader):

	"""
	Reader for JSON lists.
	
	:param src:
	   JSON source.
	"""
	
	def __init__(self, src):
	
		super().__init__(src)
		self.__read = self.__read_default
		self.__next = self.__next_value
		
	def __read_default(self, count):
	
		return super().read(count)
		
	def __read_concluded(self, count):
	
		return ""
		
	def __value_concluded(self, c):
	
		if not c.isspace():
			if c == ",":
				self.__next = self.__next_value
			elif c == "]":
				self.__read = self.__read_concluded
			else:
				self.__raise_illegal_char(c)
				
	def __next_value(self, c):
	
		if c.isspace():
			yield from ()
		elif c == "]":
			self.__read = self.__read_concluded
			yield from ()
		elif c.isdigit() or c in ( "+", "-", "." ):
			self.__next = self.__next_value_ended
			yield NumberReader(self, c, self.__value_concluded)
		elif c == "\"":
			self.__next = self.__next_value_ended
			yield StringReader(self)
		elif c == "[":
			self.__next = self.__next_value_ended
			yield ListReader(self)
		elif c == "{":
			self.__next = self.__next_value_ended
			yield DictionaryReader(self)
		else:
			self.__raise_illegal_char(c)
			
	def __next_value_ended(self, c):
	
		self.__value_concluded(c)
		yield from ()
		
	def __raise_illegal_char(self, c):
	
		raise ReaderException("Illegal character '{}'".format(c))
		
	def islist(self):
	
		"""
		Determines if it is a list reader.
		
		:rtype:
		   bool
		:return:
		   True because it is a list reader.
		"""
		
		return True
		
	def value(self):
	
		"""
		List value.
		
		:rtype:
		   list
		:return:
		   The list value.
		"""
		
		val = []
		for r in self:
			val.append(r.value())
		return val
		
	def read(self, count):
	
		"""
		Read next *count* characters from source.
		
		:param int count:
		   Number of characters to be read.
		:rtype:
		   string
		:return:
		   String containing read characters.
		"""
		
		return self.__read(count)
		
	def next(self, c):
	
		"""
		Yield next item, if any, after reading the given character.
		
		:param string c:
		   Read character.
		:yield:
		   Next item, if any.
		"""
		
		yield from self.__next(c)
		
class DictionaryReader(Reader):

	"""
	Reader for JSON dictionaries.
	
	:param src:
	   JSON source.
	"""
	
	def __init__(self, src):
	
		super().__init__(src)
		self.__read = self.__read_default
		self.__next = self.__next_key
		self.__key = None
		
	def __read_default(self, count):
	
		return super().read(count)
		
	def __read_concluded(self, count):
	
		return ""
		
	def __value_concluded(self, c):
	
		if not c.isspace():
			if c == ",":
				self.__next = self.__next_key
			elif c == "}":
				self.__read = self.__read_concluded
			else:
				self.__raise_illegal_char(c)
				
	def __next_key(self, c):
	
		if c.isspace():
			yield from ()
		elif c == "\"":
			self.__next = self.__next_key_value
			self.__key = io.StringIO()
			yield from ()
		elif c == "}":
			self.__read = self.__read_concluded
			yield from ()
		else:
			self.__raise_illegal_char(c)
			
	def __next_key_value(self, c):
	
		if c == "\\":
			self.__next = self.__next_key_value_backslash
		elif c == "\"":
			self.__next = self.__next_key_ended
		else:
			self.__key.write(c)
		yield from ()
			
	def __next_key_value_backslash(self, c):
	
		self.__next = self.__next_key_value
		self.__key.write(eval("\"\\{}\"".format(c)))
		yield from ()
		
	def __next_key_ended(self, c):
	
		if c.isspace():
			yield from ()
		elif c == ":":
			self.__next = self.__next_value
			yield from ()
		else:
			self.__raise_illegal_char(c)
			
	def __next_value(self, c):
	
		if c.isspace():
			yield from ()
		elif c.isdigit() or c in ( "+", "-", "." ):
			self.__next = self.__next_value_ended
			key = self.__key.getvalue()
			yield ( key, NumberReader(self, c, self.__value_concluded) )
		elif c == "\"":
			self.__next = self.__next_value_ended
			key = self.__key.getvalue()
			yield ( key, StringReader(self) )
		elif c == "[":
			self.__next = self.__next_value_ended
			key = self.__key.getvalue()
			yield ( key, ListReader(self) )
		elif c == "{":
			self.__next = self.__next_value_ended
			key = self.__key.getvalue()
			yield ( key, DictionaryReader(self) )
		else:
			self.__raise_illegal_char(c)
			
	def __next_value_ended(self, c):
	
		self.__value_concluded(c)
		yield from ()
		
	def __raise_illegal_char(self, c):
	
		raise ReaderException("Illegal character '{}'".format(c))
		
	def isdict(self):
	
		"""
		Determines if it is a dictionary reader.
		
		:rtype:
		   bool
		:return:
		   True because it is a dictionary reader.
		"""
		
		return True
		
	def value(self):
	
		"""
		Dictionary value.
		
		:rtype:
		   dict
		:return:
		   The dictionary value.
		"""
		
		val = {}
		for r_k, r_v in self:
			val[r_k] = r_v.value()
		return val
		
	def read(self, count):
	
		"""
		Read next *count* characters from source.
		
		:param int count:
		   Number of characters to be read.
		:rtype:
		   string
		:return:
		   String containing read characters.
		"""
		
		return self.__read(count)
		
	def next(self, c):
	
		"""
		Yield next item, if any, after reading the given character.
		
		:param string c:
		   Read character.
		:yield:
		   Next item, if any.
		"""
		
		yield from self.__next(c)
		
class WriterException(BaseException):

	"""
	Writer exception.
	
	:param args:
	   Exception arguments.
	"""
	
	def __init__(self, args):
	
		super().__init__(args)
		
class Writer:

	"""
	Abstract writer for JSON target.
	
	:param tgt:
	   JSON target.
	"""
	
	def __init__(self, tgt):
	
		self.__tgt = tgt
		self.__write = self.__write_default
		
	def __write_default(self, text):
	
		return self.__tgt.write(text)
		
	def __write_closed(self, text):
	
		raise WriterException("Writer already closed")
		
	def write(self, text):
	
		"""
		Write text to target.
		
		:param text:
		   Text to be written.
		:rtype:
		   int
		:return:
		   Number of written characters.
		:raise WriterExeption:
		   If writer is already closed.
		"""
		
		return self.__write(text)
		
	def close(self):
	
		"""
		Close this writer.
		
		:raise WriterExeption:
		   If writer is already closed.
		"""
		
		self.__write = self.__write_closed
		
class NumberWriter(Writer):

	"""
	Writer for JSON numbers.
	
	:param tgt:
	   JSON target.
	"""
	
	def __init__(self, tgt):
	
		super().__init__(tgt)
		
	def close(self):
	
		"""
		Close this writer.
		
		:raise WriterExeption:
		   If writer is already closed.
		"""
		
		self.write("")
		super().close()
		
class StringWriter(Writer):

	"""
	Writer for JSON strings.
	
	:param tgt:
	   JSON target.
	"""
	
	def __init__(self, tgt):
	
		super().__init__(tgt)
		
	def close(self):
	
		"""
		Close this writer.
		
		:raise WriterExeption:
		   If writer is already closed.
		"""
		
		self.write("\"")
		super().close()
		
class ListWriter(Writer):

	"""
	Writer for JSON lists.
	
	:param tgt:
	   JSON target.
	:param int depth:
	   Depth for pretty print.
	"""
	
	def __init__(self, tgt, depth=None):
	
		super().__init__(tgt)
		self.__depth = depth
		self.__write_sep = self.__write_sep_first
		
	def __next_depth(self):
	
		return None if self.__depth is None else self.__depth + 1
		
	def __write_next(self, n):
	
		if self.__depth is not None:
			self.write("\n")
			for i in range(self.__depth + n):
				self.write("\t")
				
	def __write_sep_first(self):
	
		self.__write_sep = self.__write_sep_default
		
	def __write_sep_default(self):
	
		self.write(",")
		
	def append(self, value):
	
		"""
		Append a value.
		
		:param value:
		   Value to be appended.
		:raise WriterException:
		   If value type is not supported.
		"""
		
		self.__write_sep()
		self.__write_next(1)
		if type(value) in ( int, float ):
			writer = NumberWriter(self)
			writer.write(str(value))
		elif type(value) == str:
			self.write("\"")
			writer = StringWriter(self)
			writer.write(value)
		elif type(value) == list:
			self.write("[")
			writer = ListWriter(self, self.__next_depth())
			for item in value:
				writer.append(item)
		elif type(value) == dict:
			self.write("{")
			writer = DictionaryWriter(self, self.__next_depth())
			for k, v in value.items():
				writer.put(k, v)
		else:
			msg = "Value type '{}' is not supported"
			raise WriterException(msg.format(type(value)))
		writer.close()
		
	def append_number(self):
	
		"""
		Append a number.
		
		:rtype:
		   NumberWriter
		:return:
		   The appended number writer.
		"""
		
		self.__write_sep()
		self.__write_next(1)
		return NumberWriter(self)
		
	def append_str(self):
	
		"""
		Append an string.
		
		:rtype:
		   StringWriter
		:return:
		   The appended string writer.
		"""
		
		self.__write_sep()
		self.__write_next(1)
		self.write("\"")
		return StringWriter(self)
		
	def append_list(self):
	
		"""
		Append a list.
		
		:rtype:
		   ListWriter
		:return:
		   The appended list writer.
		"""
		
		self.__write_sep()
		self.__write_next(1)
		self.write("[")
		return ListWriter(self, self.__next_depth())
		
	def append_dict(self):
	
		"""
		Append a dictionary.
		
		:rtype:
		   DictionaryWriter
		:return:
		   The appended dictionary writer.
		"""
		
		self.__write_sep()
		self.__write_next(1)
		self.write("{")
		return DictionaryWriter(self, self.__next_depth())
		
	def close(self):
	
		"""
		Close this writer.
		
		:raise WriterExeption:
		   If writer is already closed.
		"""
		
		self.__write_next(0)
		self.write("]")
		super().close()
		
class DictionaryWriter(Writer):

	"""
	Writer for JSON dictionaries.
	
	:param tgt:
	   JSON target.
	:param int depth:
	   Depth for pretty print.
	"""
	
	def __init__(self, tgt, depth=None):
	
		super().__init__(tgt)
		self.__depth = depth
		self.__write_sep = self.__write_sep_first
		
	def __next_depth(self):
	
		return None if self.__depth is None else self.__depth + 1
		
	def __write_next(self, n):
	
		if self.__depth is not None:
			self.write("\n")
			for i in range(self.__depth + n):
				self.write("\t")
				
	def __write_sep_first(self):
	
		self.__write_sep = self.__write_sep_default
		
	def __write_sep_default(self):
	
		self.write(",")
		
	def __write_key(self, key):
	
		self.write("\"")
		self.write(key)
		self.write("\":")
		if self.__depth is not None:
			self.write(" ")
			
	def put(self, key, value):
	
		"""
		Put a value.
		
		:param string key:
		   Key of the value to be put.
		:param value:
		   Value to be put.
		:raise WriterException:
		   If value type is not supported.
		"""
		
		self.__write_sep()
		self.__write_next(1)
		self.__write_key(key)
		if type(value) in ( int, float ):
			writer = NumberWriter(self)
			writer.write(str(value))
		elif type(value) == str:
			self.write("\"")
			writer = StringWriter(self)
			writer.write(value)
		elif type(value) == list:
			self.write("[")
			writer = ListWriter(self, self.__next_depth())
			for item in value:
				writer.append(item)
		elif type(value) == dict:
			self.writer("{")
			writer = DictionaryWriter(self, self.__next_depth())
			for k, v in value.items():
				writer.put(k, v)
		else:
			msg = "Value type '{}' is not supported"
			raise WriterException(msg.format(type(value)))
		writer.close()
		
	def put_number(self, key):
	
		"""
		Put a number.
		
		:param string key:
		   Key of the value to be put.
		:rtype:
		   NumberWriter
		:return:
		   The put number writer.
		"""
		
		self.__write_sep()
		self.__write_next(1)
		self.__write_key(key)
		return NumberWriter(self)
		
	def put_str(self, key):
	
		"""
		Put an string.
		
		:param string key:
		   Key of the value to be put.
		:rtype:
		   StringWriter
		:return:
		   The put string writer.
		"""
		
		self.__write_sep()
		self.__write_next(1)
		self.__write_key(key)
		self.write("\"")
		return StringWriter(self)
		
	def put_list(self, key):
	
		"""
		Put a list.
		
		:param string key:
		   Key of the value to be put.
		:rtype:
		   ListWriter
		:return:
		   The put list writer.
		"""
		
		self.__write_sep()
		self.__write_next(1)
		self.__write_key(key)
		self.write("[")
		return ListWriter(self, self.__next_depth())
		
	def put_dict(self, key):
	
		"""
		Put a dictionary.
		
		:param string key:
		   Key of the value to be put.
		:rtype:
		   DictionaryWriter
		:return:
		   The put dictionary writer.
		"""
		
		self.__write_sep()
		self.__write_next(1)
		self.__write_key(key)
		self.write("{")
		return DictionaryWriter(self, self.__next_depth())
		
	def close(self):
	
		"""
		Close this writer.
		
		:raise WriterExeption:
		   If writer is already closed.
		"""
		
		self.__write_next(0)
		self.write("}")
		super().close()
		
def __write_depth(str_out, depth):

	if depth is None:
		return None
		
	for i in range(depth):
		str_out.write("\t")
	return depth
	
def read(str_in):

	"""
	Read from JSON source.
	
	:param str_in:
	   JSON string input.
	:rtype:
	   Reader
	:return:
	   JSON reader.
	:raise ReaderException:
	   If some error has been ocurred at reading.
	"""
	
	c = str_in.read(1)
	while len(c) > 0:
		if not c.isspace():
			if c.isdigit() or c in ( "+", "-", "." ):
				return NumberReader(str_in, c)
			elif c == "\"":
				return StringReader(str_in)
			elif c == "[":
				return ListReader(str_in)
			elif c == "{":
				return DictionaryReader(str_in)
			else:
				raise ReaderException("Illegal character '{}'".format(c))
		c = str_in.read(1)
	return None
	
def write(str_out, value, depth=None):

	"""
	Write a value.
	
	:param str_out:
	   JSON string output.
	:param value:
	   Value to be written.
	:param int depth:
	   Depth for pretty print.
	:raise WriterException:
	   If value type is not supported.
	"""
	
	next_depth = __write_depth(str_out, depth)
	if type(value) in ( int, float ):
		writer = NumberWriter(str_out)
		writer.write(str(value))
	elif type(value) == str:
		str_out.write("\"")
		writer = StringWriter(str_out)
		writer.write(value)
	elif type(value) == list:
		str_out.write("[")
		writer = ListWriter(str_out, next_depth)
		for item in value:
			writer.append(item)
	elif type(value) == dict:
		str_out.write("{")
		writer = DictionaryWriter(str_out, next_depth)
		for k, v in value.items():
			writer.put(k, v)
	else:
		msg = "Value type '{}' is not supported"
		raise WriterException(msg.format(type(value)))
	writer.close()
	
def write_number(str_out, depth=None):

	"""
	Write a number.
	
	:param str_out:
	   JSON string output.
	:param int depth:
	   Depth for pretty print.
	:rtype:
	   NumberWriter
	:return:
	   The written number writer.
	"""
	
	__write_depth(str_out, depth)
	return NumberWriter(str_out)
	
def write_str(str_out, depth=None):

	"""
	Write an string.
	
	:param str_out:
	   JSON string output.
	:param int depth:
	   Depth for pretty print.
	:rtype:
	   StringWriter
	:return:
	   The written string writer.
	"""
	
	__write_depth(str_out, depth)
	str_out.write("\"")
	return StringWriter(str_out)
	
def write_list(str_out, depth=None):

	"""
	Write a list.
	
	:param str_out:
	   JSON string output.
	:param int depth:
	   Depth for pretty print.
	:rtype:
	   ListWriter
	:return:
	   The written list writer.
	"""
	
	next_depth = __write_depth(str_out, depth)
	str_out.write("[")
	return ListWriter(str_out, next_depth)
	
def write_dict(str_out, depth=None):

	"""
	Write a dictionary.
	
	:param str_out:
	   JSON string output.
	:param int depth:
	   Depth for pretty print.
	:rtype:
	   DictionaryWriter
	:return:
	   The written dictionary writer.
	"""
	
	next_depth = __write_depth(str_out, depth)
	str_out.write("{")
	return DictionaryWriter(str_out, next_depth)

