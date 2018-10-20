"""
Created on Sun Jun  10 00:00:10 2018

@author: Rene
"""

import unittest
from blockchain import Blockchain

class TestBlockchainUnit(unittest.TestCase):

    def setUp(self):
        pass

    def test_init(self):
        # test subject
        blockchain = Blockchain();
        # tests
        self.assertIsNotNone(blockchain)
        self.assertEqual(blockchain.current_transactions, [])

        # chain contains a genisis block
        self.assertEqual(len(blockchain.chain), 1)
        # list of nodes is 1 (count of other nodes)
        self.assertEqual(len(blockchain.nodes), 1)

        # When no config file available False
        # When config file available 40.91.211.115
        self.assertTrue(blockchain.ownip == '40.91.211.115')

    def test_valid_chain(self):
        # test subject
        blockchain = Blockchain();
        valid = blockchain.valid_chain(blockchain.chain)
        # tests
        self.assertTrue( valid )

    def test_hash(self):
        # test subject
        blockchain = Blockchain();
        # does not use a timestamped block, but a known JSON as input
        hash = blockchain.hash({'message': 'test'})
        # tests
        expected = '86914779a1d5bdaf5b828a62d6424dfea3463d453e728251777ab8ec2f6a30fe'
        self.assertEqual(hash, expected)

    def test_mine(self):
        #test subject
        blockchain = Blockchain();
        # extend test with the refactored mine method
        pass



if __name__ == '__main__':
    unittest.main()
