import hashlib
import json
from time import time
from urllib.parse import urlparse
import os

import requests

class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid

        :param chain: A blockchain
        :return: True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(last_block)
            print(block)
            print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], last_block['previous_hash']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.

        :return: True if our chain was replaced, False if not
        """
        print(self.nodes)
        neighbours = self.nodes
        new_chain = None
        # We're only looking for chains longer than ours
        max_length = len(self.chain)
        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get('{node}/chain'.format(node=node))

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self):
        """
        Create a new Block in the Blockchain
        :return: New Block
        """
        if len(self.chain) == 0:  # First block
            previous_hash = '1'
        else:
            last_block = self.last_block
            previous_hash = self.hash(last_block)

        # Create a block without valid proof
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'previous_hash': previous_hash,
        }

        # Calculate the proof of work
        block['proof'] = self.proof_of_work(block)


        # Reset the current list of transactions
        self.current_transactions = []
        self.chain.append(block)
        self._broadcast_block(block)
        return block

    def _broadcast_block(self, block):
        """
        Broadcase a new block to all neighbours
        """
        # Broadcast new bloclk post /chain
        headers = {'Content-Type':'application/json'}
        data = json.dumps(block)
        for neighbour in self.nodes:
            try:
                r = requests.post("{}/chain".format(neighbour), headers = headers, data = data, auth=self.nodecredentials)
            except:
                pass

    def add_remote_block(self, block):
        """Add a block to the chain that has received from another server.
        Params:
            block: the block to add to the chain.

        Return:
            Boolean: True if the remote block has been added."""

        # Validation of block
        valid = _validate_new_block(block)

        # Only add block if it is valid
        if valid:
            self.chain.append(block)
        # Return validation result so API can handle accordingly
        return valid

    def new_transaction(self, oldbank, oldiban, newbank, newiban, alias):
        """
        Creates a new transaction to go into the next mined Block

        :param sender: Address of the Sender
        :param recipient: Address of the Recipient
        :param amount: Amount
        :return: The index of the Block that will hold this transaction
        """
        self.current_transactions.append({
            'oldbank': oldbank,
            'oldiban': oldiban,
            'newbank': newbank,
            'newiban': newiban,
            'alias': alias
        })

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block

        :param block: Block
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, block):
        """
        Simple Proof of Work Algorithm:

         - Find a number p' such that hash(pp') contains leading 4 zeroes
         - Where p is the previous proof, and p' is the new proof

        :param last_block: <dict> last Block
        :return: <int>
        """

        block['proof'] = 0
        while self.valid_proof(block) is False:
            block['proof'] += 1

        return block['proof']

    def valid_proof(self, block):
        """
        Validates the Proof

        :param block: <dict> Block to verify proof of
        :return: <bool> True if correct, False if not.
        """

        guess_hash = self.hash(block)
        return guess_hash[:4] == "0000"

    def _validate_new_block(self, block):
        """Function to validate a new block to be added to the chain"""

        sample_block = {
                        'index': 1,
                        'timestamp': 1528564780.0628762,
                        'transactions': [{"alias":"1234","newbank":"ING","newiban":"NL45INGB23456543","oldbank":"","oldiban":""}],
                        'proof': proof,
                        'previous_hash': "1998626d3776fde5234d768b1fd7957425a296b3eb9b6025e0a62c343064cafc",
                        }

        try:
            assert type(block) == dict
            assert block.keys() == sample_block.keys()
            assert block['previous_hash'] == self.hash(last_block)
        except:
            # Reach this if checks haven't passed
            return False

        # Only here if all checks passed
        return True
