# -*- coding: utf-8 -*-
"""
Created on Sun Mar 11 17:38:12 2018

@author: Ruud


Use this to go through the blockchain and convert a UBN to IBAN
"""

import requests
import argparse

ip = "192.168.178.31"
port = 5000

class ChainSearcher:
    
    def __init__(self):
        self.findtype = None
        self.find = None
    
    def get_chain(self):
        """Get the full blockchain from a predefined party in the network"""
        # Get the full blockchain
        r = requests.get("http://{0}:{1}/chain".format(ip, port))
        self.chain = r.json()['chain']
    
    def _loopbackwards(self):
        """Find the most recent transfer for either a bankaccount or UBN in the
        blockchain"""
        
        # Loop through the blockchain backwards to find the most recent
        # reference to the UBN
        i = len(self.chain) - 1
        while i >= 0:
            block = self.chain[i]
            transaction = self._inspect_block(block)
            if transaction is not None:
                break
            i -= 1
            
        return transaction
            
    def _inspect_block(self, block):
        """Looks in the block for the thing to find"""
        
        # Make sure the thing to find is one of the fields in a transaction
        assert self.findtype in ['ubn', 'newiban', 'oldiban']
        
        # Loop through the transactions in the block and search
        for transaction in block['transactions']:
            if transaction[self.findtype] == self.find:
                return transaction
            
    def ubn_to_iban(self, ubn):
        self.findtype = 'ubn'
        self.find = ubn
        
        transaction = self._loopbackwards()
        if transaction is not None:
            return transaction['newiban']

if __name__ == '__main__':
    # Parse the provided arguments
    parser = argparse.ArgumentParser(
        description='Provide the account you want to convert and the kind of conversion')
    parser.add_argument('account', type=str,
                        help='the account you want to convert')
    parser.add_argument('--conversion', type=str,
                        choices=['ubn-newiban', 'newiban-ubn'],
                        help='the kind of conversion you want to do',
                        default='ubn-newiban')
    args = parser.parse_args()
    
    searcher = ChainSearcher()
    searcher.get_chain()
    
    if args.conversion == 'ubn-newiban':
        result = searcher.ubn_to_iban(args.account)
        if result == 'NA':
            print("UBN {0} is no longer in use."
                  .format(args.account, result))
        elif result is not None:
            print(result)
        else:
            print("UBN {0} not found".format(args.account))