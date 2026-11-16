import unittest,xml.etree.ElementTree as ET,io,ezdxf
from engine import *
class TestEngine(unittest.TestCase):
 def test_graph(self):
  p=load('plant');self.assertEqual(graph(p).number_of_edges(),len(p['Line list']))
 def test_svg(self):ET.fromstring(render(load('plant')))
 def test_dxf(self):self.assertGreater(len(ezdxf.read(io.StringIO(dxf(load('plant')))).modelspace()),0)
 def test_glossary(self):self.assertEqual(len(load('glossary')['Equipment symbols']),29)
if __name__=='__main__':unittest.main()
