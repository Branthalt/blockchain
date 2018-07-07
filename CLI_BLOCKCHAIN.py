import requests
import json
URL = 'http://localhost:5000{}'
MENU = """
Make your choice:
0 Initialize
1 Make New Transaction
2 Push Cached Transactions to a New Block
3 Show Current Chain
4 Show ALIAS-IBAN pairs.
5 Get IBAN by ALIAS
6 Get All Network Nodes
7 Put a New Network Node
99 Exit
Your Choice: 
"""
def chain2dict(chain):
    "Convert a block chain into dict. K-v pairs are alias-iban pairs"
    result = {}
    for block in chain:
        for trnx in block['transactions']:
            result[trnx['alias']] = trnx['newiban']
    return result
print("ALIAS Client V0.1\n=====================================")
while True:
    choice = input(MENU)
    if choice == '0': print(requests.get(URL.format('/mine')))
    elif choice == '1':
        input_keys = ['oldbank', 'oldiban', 'newbank', 'newiban', 'alias']
        user_inputs = []
        for hint in input_keys:
            user_inputs.append(input("{}: ".format(hint)))
        data = json.dumps(dict(zip(input_keys, user_inputs)))
        headers = {'Content-Type':'application/json'}
        print(requests.post(URL.format('/transactions/new'), headers = headers, data = data, auth=('Alice', 'secret')))
    elif choice == '2': print(requests.get(URL.format('/mine')))
    elif choice == '3': print(requests.get(URL.format('/chain')).json())
    elif choice == '4':
        chain = requests.get(URL.format('/chain')).json()['chain'] # it is a list of blocks.
        print(chain2dict(chain))
    elif choice == '5': print(requests.get(URL.format('/alias/{}'.format(input('ALIAS: ')))).json()['content'])
    elif choice == '6': print(requests.get(URL.format('/network')).json()['nodes'])
    elif choice == '7':  # Put a New Network Node
        headers = {'Content-Type':'application/json'}
        data = json.dumps({'node': input('Node URL: ')})
        r = requests.put(URL.format('/network'), headers = headers, data = data) #auth=('Alice', 'secret'))
        print(r.json()['nodes'])
    elif choice == '99': break
    else: pass  # invalid choice, start again.