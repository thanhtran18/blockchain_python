import time
from hashlib import sha256
import json
from flask import Flask, request
import requests


class Block:
    def __init__(self, index, transactions, timestamp, prev_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.prev_hash = prev_hash
        self.nonce = nonce

    # create the hash of the block
    def calculate_hash(block):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class Blockchain:
    difficulty = 2

    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.create_genesis()

    def create_genesis(self):
        genesis = Block(0, [], time.time(), "0")
        genesis.hash = genesis.calculate_hash()
        self.chain.append(genesis)

    @property
    def get_last_block(self):
        return self.chain[-1]

    # brute force to figure out the nonce
    def create_proof_of_work(self, block):
        block.nonce = 0
        calculated_hash = block.calculate_hash()
        while not calculated_hash.startswith("0" * Blockchain.difficulty):
            block.nonce = block.nonce + 1
            calculated_hash = block.calculate_hash()

        return calculated_hash

    def add_block(self, new_block, proof_of_work):
        curr_prev_hash = self.get_last_block.hash
        if curr_prev_hash != new_block.prev_hash or not self.is_valid_proof_work(new_block, proof_of_work):
            return False
        else:
            new_block.hash = proof_of_work
            self.chain.append(new_block)
            return True

    # check the validity of the block hash and to see if it satisfies the difficulty
    @classmethod
    def is_valid_proof_work(cls, new_block, new_block_hash):
        return (new_block_hash.startswith('0' * Blockchain.difficulty)
                and new_block_hash == new_block.calculate_hash())

    def add_transaction(self, new_transaction):
        self.unconfirmed_transactions.append(new_transaction)

    # add pending transactions to the block and calculate the proof of work
    def mine(self):
        if self.unconfirmed_transactions:
            last_block = self.get_last_block
            new_block = Block(index=last_block.index+1,
                              transactions=self.unconfirmed_transactions,
                              timestamp=time.time(),
                              prev_hash=last_block.hash)
            proof = self.create_proof_of_work(new_block)
            self.add_block(new_block, proof)
            self.unconfirmed_transactions = []
            # broadcast this to the network
            announce_added_block(new_block)
            return new_block.index
        else:
            return False

    @classmethod
    def is_chain_valid(cls, chain):
        result = True
        prev_hash = '0'

        for block in chain:
            block_hash = block.hash
            # remove and recompute the hash
            delattr(block, "hash")

            if not cls.is_valid_proof_work(block, block.hash) or prev_hash != block.prev_hash:
                result = False
                break

            block.hash, prev_hash = block_hash, block_hash
        return result


app = Flask(__name__)

blockchain = Blockchain()

# receive new transaction to the blockchain
@app.route('/new_transaction', methods=['POST'])
def receive_new_transaction():
    new_transaction = request.get_json()
    required_fields = ['author', 'content']

    for field in required_fields:
        if not new_transaction.get(field):
            return 'Invalid transaction data', 404

    new_transaction["timestamp"] = time.time()
    blockchain.add_transaction(new_transaction)
    return 'Success', 201

# return the node's copy of the chain by querying all of the posts
@app.route('/chain', methods=['GET'])
def get_chain():
    chain = []
    for block in blockchain.chain:
        chain.append(block.__dict__)
    return json.dumps({'length': len(chain), 'chain': chain})

# receive request to mine unconfirmed transactions
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if result:
        return 'Block #{} is mined.'.format(result)
    return 'No transactions to mine'

# query unconfirmed transactions
@app.route('/pending_transaction')
def get_pending_transaction():
    return json.dumps(blockchain.unconfirmed_transactions)


# create an address so other can join the network
peers = set()

# receive request to join the network
@app.route('/add_nodes', methods=['POST'])
def register_new_peers():
    nodes = request.get_json()
    if nodes:
        for node in nodes:
            peers.add(node)
        return 'Success', 201
    else:
        return 'Invalid Data', 400


def consensus():
    global blockchain
    longest_chain = None
    curr_length = len(blockchain)

    for peer in peers:
        response = requests.get('http://{}/chain'.format(peer))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > curr_length and blockchain.is_chain_valid(chain):
            curr_length = length
            longest_chain = chain

    # if a longer valid chain is found, it becomes the new global blockchain
    if longest_chain:
        blockchain = longest_chain
        return True
    return False

# add a new block to the node's chain
@app.route('/add_block', methods=['POST'])
def validate_and_add_block():
    new_block_data = request.get_json()
    new_block = Block(new_block_data['index'], new_block_data['transactions'],
                      new_block_data['timestamp'], new_block_data['pre_hash'])
    proof = new_block_data['hash']
    added = blockchain.add_block(new_block, proof)
    if added:
        return 'A new block was added to the blockchain', 201
    return 'Failed to add the new block to the blockchain', 400


def announce_added_block(new_block):
    for peer in peers:
        url = 'http://{}/add_block'.format(peer)
        requests.post(url, data=json.dumps(new_block.__dict__, sort_keys=True))


app.run(debug=True, port=8000)
