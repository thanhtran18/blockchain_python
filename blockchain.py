import time
from hashlib import sha256
import json


class Block:
    def __init__(self, index, transactions, timestamp, prev_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.prev_hash = prev_hash

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
    def proof_of_work(self, block):
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
