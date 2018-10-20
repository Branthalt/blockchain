# -*- coding: utf-8 -*-
"""
Created on Sat Jun  9 14:14:17 2018

@author: Ruud
"""

import unittest
from unittest import mock
from unittest.mock import patch
from ketting import Blockchain

class TestBlockchain(unittest.TestCase):

    def setUp(self):
        self.sample_block = {
            'index': 1,
            'timestamp': 1528564780.0628762,
            'transactions': [{"alias":"1234","newbank":"ING","newiban":"NL45INGB23456543","oldbank":"","oldiban":""}],
            'proof': "123456789776fde5234d768b1fd7957425a296b3eb9b6025e0a62c3430abcdef",
            'previous_hash': "1998626d3776fde5234d768b1fd7957425a296b3eb9b6025e0a62c343064cafc",
            'message': "some nice string with a message"
            }
        self.blockchain = Blockchain()

    def test_basic_initialisation(self):
       blockchain = Blockchain()
       self.assertEqual(blockchain.chain, [])
       self.assertEqual(blockchain.transactions, [])

    @patch('ketting.blockchain.time', mock.MagicMock(return_value=0))
    def test_create_new_chain(self):
        blockchain = Blockchain()
        message = "hello world"
        block = blockchain.new_block(message)
        self.assertEqual(blockchain.last_block, block)
        self.assertEqual(block.keys(), self.sample_block.keys())
        self.assertEqual(block['message'], message)
        self.assertEqual(block['index'], 0)
        self.assertEqual(block['previous_hash'], "1")
        self.assertEqual(block['timestamp'], 0)
        self.assertEqual(block['proof'], 89608)

    def test_invalid_message(self):
        blockchain = Blockchain()
        with self.assertRaises(AssertionError):
            blockchain.new_block(1)

        with self.assertRaises(AssertionError):
            blockchain.new_block({})

        with self.assertRaises(AssertionError):
            blockchain.new_block([])

        with self.assertRaises(AssertionError):
            blockchain.new_block("hello".encode())

    def test_add_valid_transaction(self):
        transaction = {'foo': 'bar'}
        self.assertTrue(self.blockchain.new_transaction(transaction))
        self.assertTrue(self.blockchain.new_transaction({}))

        self.assertEqual(len(self.blockchain.transactions), 2)
        self.assertEqual(self.blockchain.transactions[0], transaction)
        self.assertEqual(self.blockchain.transactions[1], {})

    def test_add_invalid_transaction(self):
        transaction = ['foo', 'bar']
        self.assertFalse(self.blockchain.new_transaction(transaction))
        self.assertFalse(self.blockchain.new_transaction([]))
        self.assertFalse(self.blockchain.new_transaction("foo"))
        self.assertFalse(self.blockchain.new_transaction(1))
        self.assertFalse(self.blockchain.new_transaction(1.1))

        self.assertEqual(len(self.blockchain.transactions), 0)

if __name__ == "__main__":
    unittest.main()