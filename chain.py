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
import random
import time

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
        self._name = name
        self._creation_time = datetime.datetime.today()
        self._history = {}
        self._public_key = self.make_public_key()
        self._chain = chain

    def make_public_key(self):
        #Every individual has an unique "address"
        key = hashlib.sha256((str(self._creation_time) +
                            str(self._name)).encode('utf-8'))
        return key.hexdigest()
    
    def public_info(self):
        return (self.public_key, balance)

    def get_history(self):
        return self._history

    def verify(self, sender_hist):
        #Check all past exchanges in blockchain

        #loop checks every exchange
        for key, exch in sender_hist.items():
            if exch._amount != self._chain._blocks[exch._block]._exchanges[key]._amount:
                return False #incorrect exchange records will return false
        print("Verified")
        return True
            
    
class Market:
    #Contains information on all users, allows them to interact
    #with the blockchain and each other.
    def __init__(self, blockchain, block):
        self._users = {}
        self._chain = blockchain
        self._current_block = block #Create a new block

    def add_user(self, key, individual):
        self._users[key] = individual

    def add_exchange(self, sender, receiver, amount):
        #Add exchange history to sender and receiver history
        #Add exchange to current block, or push full block to chain
        #  and create a new block

        if (self._current_block._size == 2):
            self._current_block = Block() #Create a new current block
            self._chain.add_block(self._current_block) #Add block to chain
            
            print("Pushing full block to chain. Creating new block.")
            print("Current chain size: " + str(self._chain._size))

        else:
            new_exchange = Exchange(sender, receiver, amount,
                                    self._current_block.hash)
            self._current_block._exchanges[new_exchange._key] = new_exchange
            self._current_block._size += 1

            self._users[sender]._history[new_exchange._key] = new_exchange
            self._users[receiver]._history[new_exchange._key] = new_exchange
        
        
    def transaction(self, sender, receiver, amount):

        print("\nBeginning Transaction\n")

        if (sender == receiver):
            print("Invalid Adresses")
        
        elif (self._users[sender]._balance < amount):
            print("Insufficient Funds")
            
        else:
            verify1 = random.choice(list(self._users.keys()))
            verify2 = random.choice(list(self._users.keys()))
            verify3 = random.choice(list(self._users.keys()))

            #No duplicate verifiers
            while (verify1 == verify2 or verify2 == verify3
                   or verify1 == verify3):
                verify2 = random.choice(list(self._users.keys()))
                verify3 = random.choice(list(self._users.keys()))

            #Check all three verifications
            sender_hist = self._users[sender]._history

            if (self._users[verify1].verify(sender_hist)
                and self._users[verify2].verify(sender_hist)
                and self._users[verify3].verify(sender_hist)):

                self._users[sender]._balance -= amount
                self._users[receiver]._balance += amount

                self.add_exchange(sender, receiver, amount)

                print("Sent " + str(amount) + " pyCoins from\n" + str(sender) +
                      "\nto\n" + str(receiver))

            else:
                print("Transaction Denied")
                return

        print("\n")
        
        
    #Each user submits personal transaction history to verifiers
    #Verifiers scan their copy of blockchain to guarentee amount
    #and current block are valid.

def build_sample_market():
    b = Block() #make initial block
    c = Chain(b) #create chain with block
    m = Market(c,b) #start market with chain

    inds = [Individual(300, "Marcy", c),
            Individual(20, "David", c),
            Individual(400, "Charles", c),
            Individual(7000, "Lauren", c),
            Individual(5000, "Dobby", c),
            Individual(89, "Ellen", c)]

    for i in inds:
        m.add_user(i._public_key, i)


    ind1 = Individual(500, "Todd", c)
    ind2 = Individual(800, "Jamie", c)
    m.add_user(ind1._public_key, ind1)
    m.add_user(ind2._public_key, ind2)
    m.transaction(ind1._public_key, ind2._public_key, 300)
    time.sleep(3)
    m.transaction(ind1._public_key, ind2._public_key, 800)
    time.sleep(3)
    m.transaction(ind2._public_key, ind1._public_key, 50)
    time.sleep(3)
    m.transaction(ind2._public_key, ind1._public_key, 40)


    
    
    x = 50
    for i in range(4):
        m.transaction(inds[i]._public_key, inds[i+1]._public_key, x)
        x *= 2
        time.sleep(2)
    

def main():
    build_sample_market()
main()
