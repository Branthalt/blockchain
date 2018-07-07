from urllib.parse import urlparse
from uuid import uuid4
import json
import requests
from flask import Flask, jsonify, request, Response
from flask_cors import CORS

from blockchain.blockchain import Blockchain


"""
20180302 BvS: Made script compatible with Python3.5 (f function)
"""

# Instantiate the Node
app = Flask(__name__)
CORS(app)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

# response_noauth = Response('Could not verify your access level for that URL.\n'
#                           'You have to login with proper credentials', 401,
#                           {'WWW-Authenticate': 'Basic realm="Login Required"'})

@app.route('/mine', methods=['GET'])
def mine():
    # Create new blocl at local chain
    block = blockchain.new_block()
    # Broadcast new bloclk post /chain
    headers = {'Content-Type':'application/json'}
    data = json.dumps(block)
    for neighbour in blockchain.nodes:
        r = requests.post("{}/chain".format(neighbour), headers = headers, data = data, auth=('Alice', 'secret'))
        print(r)
    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }
    return jsonify(response), 200

@app.route('/alias')
@app.route('/alias/<alias>')
def get_iban(alias = None):
    "Given a alias, return its IBAN"
    alias_ibans = _chain2dict(blockchain.chain, 'newiban')
    alias_banks = _chain2dict(blockchain.chain, 'newbank')
    response = {}
    r = []
    if alias:
        r.append({'alias': alias,'iban': alias_ibans.get(alias), 'bank': alias_banks.get(alias)})
    else:
        for u in alias_ibans.keys():
            r.append({'alias':u, 'iban': alias_ibans.get(u), 'bank': alias_banks.get(u)})
    response['content'] = r
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    """Code for endpoint of creating new transaction to be added to chain"""
    # Check authentication, limiting the parties that can make changes on the
    # chain
    if not _authorisation(request.authorization):
        response = {'message': 'You have to login with proper credentials'}
        #return response_noauth
        return jsonify(response), 401

    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['oldbank', 'oldiban', 'newbank', 'newiban', 'alias']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['oldbank'], values['oldiban'],
                                       values['newbank'], values['newiban'],
                                       str(values['alias']))

    response = {'message': 'Transaction will be added to Block {index}'.format(index=index)}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/chain', methods=['POST'])
def add_block():
    """"This is used by other nodes in the network to notify of new blocks that
    they have mined."""
    # Check authorisation
    if not _authorisation(request.authorization):
        response = {'message':'You have to login with proper credentials'}
        #return response_noauth
        return jsonify(response), 401

    # Get the block from the request
    block = request.get_json()

    # validate and add the new block
    valid = blockchain.add_remote_block(block)

    # Response based on validation
    if valid:
        return jsonify(valid), 202
    else:
        return jsonify(valid), 406

@app.route('/network', methods=['GET'])
def interrogate_nodes():
    "Return list of known banks nodes."
    response = {'nodes': list(blockchain.nodes)}
    return jsonify(response), 200

@app.route('/network', methods=['PUT'])
def insert_node():
    "Put a new node into the blockchain node set"
    url = request.get_json().get('node') # Should be string of nodes info. {'node': 'http://192.168.0.1:5000'}
    try:
        p = urlparse(url)
        if p.netloc:  # url is with http(s) prefix
            new_node = "{}://{}".format(p.scheme, p.netloc)
        elif p.path:
            new_node = "http://{}".format(p.path)
        else:
            raise ValueError('Input URL is malformatted')
        blockchain.nodes.add(new_node)
        response = {
            'message': 'New node has been added',
            'nodes': list(blockchain.nodes)
            }
        return jsonify(response), 201
    except:
        response = {
        'message': 'New Node Structure not correct. {}'.format(url),
        'nodes': list(blockchain.nodes)
        }
        return jsonify(response), 400

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    "Deprecated, use PUT /network"
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


@app.route('/authtest', methods=['GET'])
def auth_test():
    if _authorisation(request.authorization):
        response = {'message':'OK'}
        return jsonify(response), 200
    else:
        #return response_noauth
        response = {'message':'You have to login with proper credentials'}
        return jsonify(response), 401

#####
# support steps
#####


def _authorisation(auth):
    """Check username/password for basic authentication"""
    if not auth:
        return False

    user = auth.username
    password = auth.password

    credentials = {'Alice': 'secret',
                   'Bob': 'supersecret'}

    try:
        truepass = credentials[user]
    except KeyError:
        return False

    if truepass == password:
        return True
    else:
        return False

def _chain2dict(chain, v = 'newiban'):
    """Convert a block chain into dict. K-v pairs are alias-iban pairs
       :param v = newiban or newbank
    """
    result = {}

    for block in chain:
        for trnx in block['transactions']:
            result[trnx['alias']] = trnx[v]
    return result

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
