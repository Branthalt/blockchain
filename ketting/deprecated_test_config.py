"""
Created on Sun Jun  10 08:22:10 2018

@author: Rene
"""

import unittest
from config import Config

class TestConfigUnit(unittest.TestCase):

    def setUp(self):
        self.expected_nodeconfig = "/home/baasuser/node-config.json"


    def test_init(self):
        # test subject
        config = Config();
        # tests
        self.assertIsNotNone(config)
        self.assertEqual(config.nodeconfig, self.expected_nodeconfig)
        self.assertEqual(config.ownip, '40.91.211.115')
        # Alternative is self.assertFalse(config.ownip)



if __name__ == '__main__':
    unittest.main()
