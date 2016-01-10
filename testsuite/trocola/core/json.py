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

from trocola.core import json

import io
import os.path
import unittest

class TestRead(unittest.TestCase):

	def __concluded_pass(self, c):
	
		pass
		
	def test_value_number(self):
	
		try:
			json_in = resource_open("value-number.json")
			reader = json.read(json_in)
			self.assertTrue(reader.isnumber())
			self.assertEqual(reader.value(), 176)
		finally:
			json_in.close()
		
	def test_value_str(self):
	
		try:
			json_in = resource_open("value-str.json")
			reader = json.read(json_in)
			self.assertTrue(reader.isstr())
			self.assertEqual(reader.value(), "abcD123\"aaa")
		finally:
			json_in.close()
		
	def test_value_list(self):
	
		try:
			json_in = resource_open("value-list.json")
			reader = json.read(json_in)
			self.assertTrue(reader.islist())
			value = reader.value()
			self.assertEqual(value[0], "value1")
			self.assertEqual(value[1], "value2")
			self.assertEqual(value[2], "value3")
		finally:
			json_in.close()
		
	def test_value_dict(self):
	
		try:
			json_in = resource_open("value-dict.json")
			reader = json.read(json_in)
			self.assertTrue(reader.isdict())
			value = reader.value()
			self.assertEqual(value["key1"], "value1")
			self.assertEqual(value["key2"], "value2")
			self.assertEqual(value["key3"], "value3")
		finally:
			json_in.close()
		
	def test_stream_complex(self):
	
		try:
			json_in = resource_open("stream-complex.json")
			reader = json.read(json_in)
			self.assertTrue(reader.isdict())
			for ra_i, (ra_k, ra_v) in enumerate(reader):
				if ra_i == 0:
					self.assertTrue(ra_v.isstr())
					self.assertEqual(ra_k, "name")
					self.assertEqual(ra_v.value(), "complex")
				elif ra_i == 1:
					self.assertTrue(ra_v.isnumber())
					self.assertEqual(ra_k, "complexity")
					self.assertEqual(ra_v.value(), 1)
				elif ra_i == 2:
					self.assertTrue(ra_v.islist())
					self.assertEqual(ra_k, "items")
					for rb_i, rb in enumerate(ra_v):
						self.assertTrue(rb.isstr())
						self.assertEqual(rb.value(), "item{}".format(rb_i + 1))
				elif ra_i == 3:
					self.assertTrue(ra_v.isdict())
					for rb_i, (rb_k, rb_v) in enumerate(ra_v):
						if rb_i == 0:
							self.assertTrue(rb_v.isstr())
							self.assertEqual(rb_k, "type")
							self.assertEqual(rb_v.value(), "stream")
						elif rb_i == 1:
							self.assertTrue(rb_v.isnumber())
							self.assertEqual(rb_k, "depth")
							self.assertEqual(rb_v.value(), 2)
						else:
							self.assertTrue(False)
				else:
					self.assertTrue(False)
		finally:
			json_in.close()
			
class TestWrite(unittest.TestCase):

	def test_value_number(self):
	
		json_out = io.StringIO()
		json.write(json_out, 176)
		self.assertSameContent(json_out, "value-number.json")
		
	def test_value_str(self):
	
		json_out = io.StringIO()
		json.write(json_out, "abcD123\\\"aaa")
		self.assertSameContent(json_out, "value-str.json")
		
	def test_value_list(self):
	
		json_out = io.StringIO()
		json.write(json_out, [
			"value1",
			"value2",
			"value3"
		], 0)
		self.assertSameContent(json_out, "value-list.json")
		
	def test_value_dict(self):
	
		json_out = io.StringIO()
		writer = json.write_dict(json_out, 0)
		writer.put("key1", "value1")
		writer.put("key2", "value2")
		writer.put("key3", "value3")
		writer.close()
		self.assertSameContent(json_out, "value-dict.json")
		
	def test_stream_complex(self):
	
		json_out = io.StringIO()
		writer = json.write_dict(json_out, 0)
		writer.put("name", "complex")
		writer.put("complexity", 1)
		wa = writer.put_list("items")
		wa.append("item1")
		wa.append("item2")
		wa.append("item3")
		wa.close()
		wa = writer.put_dict("properties")
		wa.put("type", "stream")
		wa.put("depth", 2)
		wa.close()
		writer.close()
		self.assertSameContent(json_out, "stream-complex.json")
		
	def assertSameContent(self, str_io, res_path, msg=None):
	
		try:
			str_io.write("\n")
			str_io.seek(0)
			res_in = resource_open(res_path)
			self.assertEqual(str_io.read(), res_in.read())
		finally:
			res_in.close()
			
def resource_open(path):
	
	res_path = os.path.dirname(__file__)
	res_path = os.path.join(res_path, "resources")
	res_path = os.path.join(res_path, path)
	return open(res_path)

