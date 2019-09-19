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
    def is_valid_proof_work(self, new_block, new_block_hash):
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
            return new_block.index
        else:
            return False


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


app.run(debug=True, port=8000)
