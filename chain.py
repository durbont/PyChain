#David Urbont
#Last Updated: December 16, 2017
#Implementing a blockchain with python

#Based on architecture described at:
#https://www.oreilly.com/ideas/understanding-the-blockchain
### With some light artistic license thrown in ###

##GENERAL OUTLINE##
#    A Market of Individuals connect to the Chain, which acts as a
# hash table of Blocks. When users make an Exchange in the market,
# that Exchange is added to the current Block. When the Block reaches
# capacity, it is added to the Chain. P2P Verification: Two randomly
# selected users have to check their current block, and the current
# block of exchanging users (as well as balances), to verify a transaction. 

#There is no mining involved in this blockchain

import datetime #for hashing
import queue    #for queueing transactions
import hashlib

class Chain:
    #Main class, holds Block objects
    def __init__(self, origin_block):
        self._blocks = {}
        self._size = 1
        self._version = 0
        self._curr_block = origin_block #public hash value
        self.add_block(origin_block)
    
    def add_block(self, block):
        #implement hashing function
        #hash onto new block onto chain
        self._blocks[block.get_public_hash()] = block
        self._size += 1

        
class Block:
    #Block class: an individual in the chain
    def __init__(self):
        self._time = datetime.datetime.today()
        self._exchanges = {} #Map of exchange hashes and objects
        self.hash = self.make_hash() #Public header
        self._next_block_hash = None

    def make_hash(self):
        #simplified block hash. Could be more thorough,
        #Bitcoin uses index, time, exchange data, and the hash
        #of the previous block. I'll just use time and exchanges,
        #since we are restricted to one block at a time.

        h = hashlib.sha256() #make hash object
        
        h.update((str(self._time) +
                 (str(self._exchanges))).encode('utf-8'))
        
        return h.hexdigest() #return hex hash value

    def get_public_hash(self):
        return self.hash

    
class Exchange:
    #Contains information on two users, and price
    def __init__(self, sender, receiver, amount, time):
        self._sender = sender
        self._receiver = receiver
        self._amount = amount
        self._time = time
        self._key = self.make_exchange_key()

    def make_exchange_key(self):
        key = hashlib.sha256((str(self._sender) +
                              str(self._receiver) +
                              str(self._amount) +
                              str(self._time)).encode('utf-8'))
        return key.hexdigest()


class Individual:
    #Contains basic information on user
    def __init__(self, balance, name):
        self._balance = balance
        self._name = name
        self._creation_time = datetime.datetime.today()
        self._public_key = self.make_public_key()

    def make_public_key(self):
        #Every individual has an unique "address"
        key = hashlib.sha256((str(self._creation_time) +
                              str(self._name)).encode('utf-8'))
        return key.hexdigest()
        
    def public_info(self):
        return (self.public_key, balance)

    def verify(self, sender, amount):
        pass

    
class Market:
    #Contains information on all users, allows them to interact
    #with the blockchain and each other.
    def __init__(self, blockchain):
        self._users = {}
        self._blockchain = chain
        
        
    #Each user submits personal transaction history to verifiers
    #Verifiers scan their copy of blockchain to guarentee amount
    #and current block are valid.

def main():

    
    print("Running")

    pending = queue.Queue()

    b = Block()
    c = Chain(b)

    person = Individual(100, "David")    
    
    print("Done")

main()
