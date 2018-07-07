import os
import json

# Decide to refactor the blockchain.py to extract this Config
class Config():

    def __init__(self, nodeconfig = "/home/baasuser/node-config.json" ):
        self.nodeconfig = nodeconfig
        self.config = {}
        self.ownip = False
        self._load()

    def _load(self):
        if os.path.isfile(self.nodeconfig):
            with open(self.nodeconfig) as f:
                self.config = json.load(f)
                self.ownip = str(self.config['ip'])
        else:
            print("No config file at {0}".format(self.nodeconfig))

    # register nodes from the config in the blockchain
    def network(self, blockchain):
        if self.config.get("network"):
            for ip in self.config['network']:
                blockchain.register_node('{}:5000'.format(ip))

    # get network node ip list
    def ip(self):
        return self.config['network']

    def isOwnIP(self):
        return self.ownip
