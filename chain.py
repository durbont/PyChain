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
# capacity, a new block is made and is added to the Chain.
# P2P Verification: Two randomly selected users have to check their
# current block, and the current block of exchanging users
# (as well as balances), to verify a transaction. 

#There is no mining involved in this blockchain

import datetime #for hashing
import queue    #for queueing transactions
import hashlib
import random
import time
import copy #So miners have uncorruptible version of blockchain

class Chain:
    #Main class, holds Block objects
    def __init__(self, origin_block):
        self._blocks = {}
        self._size = 0
        self._curr_block = origin_block.hash #public key
        self.add_block(origin_block)
    
    def add_block(self, block):
        #implement hashing function
        #hash onto new block onto chain
        self._blocks[block.get_public_hash()] = block
        self._curr_block = block.hash
        self._size += 1

        
class Block:
    #Block class: an individual in the chain
    def __init__(self):
        self._time = datetime.datetime.today()
        self._size = 0
        self._exchanges = {} #Map of exchange hashes and objects
        self.hash = self.make_hash() #Public header

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
    def __init__(self, sender, receiver, amount, block):
        self._sender = sender     #public key
        self._receiver = receiver #public key
        self._amount = amount
        self._time = datetime.datetime.today()
        self._key = self.make_exchange_key()
        self._block = block        #public hash value

    def make_exchange_key(self):
        key = hashlib.sha256((str(self._sender) +
                              str(self._receiver) +
                              str(self._amount) +
                              str(self._time)).encode('utf-8'))
        return key.hexdigest()
    

class Individual:
    #Contains basic information on user
    def __init__(self, balance, name, chain):
        self._balance = balance
        self.__name = name
        self.__creation_time = datetime.datetime.today()
        self._history = {}
        self._public_key = self.make_public_key()
        self.__chain = chain

    def make_public_key(self):
        #Every individual has an unique "address"
        key = hashlib.sha256((str(self.__creation_time) +
                            str(self.__name)).encode('utf-8'))
        return key.hexdigest()
    
    def public_info(self):
        return (self.public_key, balance)

    def get_history(self):
        return self._history

    def add_block(self, block):
        self.__chain.add_block(block)


            
    
class Market:
    #Contains information on all users, allows them to interact
    #with the blockchain and each other.
    def __init__(self, blockchain, block):
        self.__miners = {}
        self._miner_count = 0
        self.__users = {}
        self._chain = blockchain
        self._current_block = block #Create a new block

    def add_user(self, key, individual):
        self.__users[key] = individual

    def add_miner(self, miner):
        self.__miners[miner._index] = miner
        self._miner_count += 1

    def update_users(self):
        for key, user in self.__users.items():
            user.add_block(copy.deepcopy(self._current_block))

    def update_miner_exchanges(self, exchange):
        for key, m in self.__miners.items():
            m.exchange_update(exchange)

    def update_miner_blocks(self,block):
        for key, m in self.__miners.items():
            m.block_update(block)
    
    def add_exchange(self, sender, receiver, amount):
        #Add exchange history to sender and receiver history
        #Add exchange to current block, or push full block to chain
        #  and create a new block

        if (self._current_block._size == 10):
            self._current_block = Block() #Create a new current block
            self._chain.add_block(self._current_block) #Add block to chain

            self.update_miner_blocks(copy.deepcopy(self._current_block))

            print("Pushing full block to chain. Creating new block.")
            print("Current chain size: " + str(self._chain._size))

        else:
            new_exchange = Exchange(sender, receiver, amount,
                                    self._current_block.hash)
            self._current_block._exchanges[new_exchange._key] = new_exchange
            self._current_block._size += 1

            #send data to miners
            self.update_miner_exchanges(copy.deepcopy(new_exchange))
            
            self.__users[sender]._history[new_exchange._key] = new_exchange
            self.__users[receiver]._history[new_exchange._key] = new_exchange
        
        
    def transaction(self, sender, receiver, amount):

        print("\nBeginning Transaction\n")

        if (sender == receiver):
            print("Invalid Adresses")
            return

        sender_object = self.__users[sender]
        receiver_object = self.__users[receiver]
        
        if (self.__users[sender]._balance < amount or amount < 0):
            print("Insufficient Funds")
            return
            
        else:
            m1, m2, m3 = random.sample(range(1, self._miner_count+1), 3)

            #Check all three verifications
            sender_hist = sender_object._history

            if (self.__miners[m1].verify(sender_hist)
                and self.__miners[m2].verify(sender_hist)
                and self.__miners[m3].verify(sender_hist)):

                sender_object._balance -= amount
                receiver_object._balance += amount

                self.add_exchange(sender, receiver, amount)

                print("Sent " + str(amount) + " pyCoins from\n" + str(sender) +
                      "\nto\n" + str(receiver))

            else:
                print("Transaction Denied")
                return

        print("\n")

class Miner:
    def __init__(self, index, chain):
        self._index = index
        self.__chain = chain
        #self.__current_block = block

    def verify(self, sender_hist):
        #Check all past exchanges in blockchain
        for key, exch in sender_hist.items():
            if exch._amount != \
               self.__chain._blocks[exch._block]._exchanges[key]._amount:
                return False #incorrect exchange records will return false
            
        print("Verified")
        return True

    def block_update(self, block):
        self.__chain.add_block(block)

    def exchange_update(self, exchange):
        key = self.__chain._curr_block
        self.__chain._blocks[key]._exchanges[exchange._key] = exchange
    
        
def build_sample_market():
    b = Block() #make initial block
    c = Chain(b) #create chain with block
    m = Market(c,b) #start market with chain

    miners = [Miner(1, copy.deepcopy(c)),
              Miner(2, copy.deepcopy(c)),
              Miner(3, copy.deepcopy(c)),
              Miner(4, copy.deepcopy(c)),
              Miner(5, copy.deepcopy(c)),
              Miner(6, copy.deepcopy(c)),
              Miner(7, copy.deepcopy(c)),
              Miner(8, copy.deepcopy(c))]
    
    for i in miners:
        m.add_miner(i)
    
    inds = [Individual(300, "Marcy", c),
            Individual(20, "David", c),
            Individual(400, "Charles", c),
            Individual(7000, "Lauren", c),
            Individual(5000, "Dobby", c),
            Individual(89, "Ellen", c)]

    for i in inds:
        m.add_user(i._public_key, i)

    x = 25
    for i in range(4):
        m.transaction(inds[i]._public_key, inds[i+1]._public_key, x)
        x *= 2
        time.sleep(2)

    for i in range(4,1,-1):
        m.transaction(inds[i]._public_key, inds[i-1]._public_key, x)
        x /= 4
        time.sleep(2)

    #should be invalid
    m.transaction(inds[0]._public_key, inds[0]._public_key, 10)

    #try revising someones history
    choice = random.choice(list(inds[0]._history.keys()))
    inds[0]._history[choice]._amount += 500
    inds[0]._balance += 500

    m.transaction(inds[0]._public_key, inds[1]._public_key, 10)

def main():
    build_sample_market()
main()
