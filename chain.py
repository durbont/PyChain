#David Urbont
#Last Updated: December 17, 2017
#Implementing a blockchain with python

### * Designed with some artistic license * ###

##GENERAL OUTLINE##
#    A Market of Individuals connects to the Chain, which acts as a
# hash table of Blocks. When users make an Exchange in the market,
# that Exchange is added to the current Block. When the Block reaches
# capacity, a new block is made and is added to the Chain.
# P2P Verification: 3 randomly selected miners verify the sender
# before a transaction can be completed.
#
#
#  ##############  Market access ############
#    BlockChain  <--------------    Market
#  ##############                ############
#        ||                       ||      ||
#        ||                       ||      ||
#        \/                       \/      \/ 
#     #####   #####        Individuals    Miners
# ..+ Block + Block+..          |           | 
#     #####   #####             |    Verify |
#               ||              |<----------+
#               \/              |
#           #Exchanges#<--------+
#


import datetime #for hashing
import hashlib
import random
import time #For displaying output sequentially
import copy #So miners have uncorruptible version of blockchain


class Chain:
    #Main class, holds Block objects
    def __init__(self, origin_block):
        self._blocks = {}
        self._size = 0
        self._curr_block = origin_block.hash #public key
        self.add_block(origin_block)
    
    def add_block(self, block):
        #Takes a new block as input, adds it to _blocks hash map.
        #Change current block and size of blockchain
        self._blocks[block.hash] = block
        self._curr_block = block.hash
        self._size += 1

        
class Block:
    #Block class: an individual in the chain
    def __init__(self):
        self._time = datetime.datetime.today()
        self._size = 0
        self._exchanges = {} #Map of exchange hashes(keys) and objects
        self.hash = self.make_hash() #Public header

    def make_hash(self):
        #simplified block hash. Could be more thorough,
        #Bitcoin uses index, time, exchange data, and the hash
        #of the previous block. I'll just use time and exchanges.

        h = hashlib.sha256() #make hash object
        
        h.update((str(self._time) +
                 (str(self._exchanges))).encode('utf-8'))
        
        return h.hexdigest() #return hex hash value

    
class Exchange:
    #Contains information on two users, and price
    def __init__(self, sender, receiver, amount, block):
        self._sender = sender     #public key
        self._receiver = receiver #public key
        self._amount = amount
        self._time = datetime.datetime.today()
        self._key = self.make_exchange_key()
        self._block = block       #public hash value

    def make_exchange_key(self):
        #Every exchange has a distinct key for tracking
        key = hashlib.sha256((str(self._sender) +
                              str(self._receiver) +
                              str(self._amount) +
                              str(self._time)).encode('utf-8'))
        return key.hexdigest()
    

class Individual:
    #Contains basic information on user
    def __init__(self, balance, name):
        self._balance = balance
        self.__name = name
        self.__creation_time = datetime.datetime.today()
        self._history = {}
        self._public_key = self.make_public_key()

    def make_public_key(self):
        #Every individual has an unique "address"
        key = hashlib.sha256((str(self.__creation_time) +
                            str(self.__name)).encode('utf-8'))
        return key.hexdigest()
    
    def public_info(self):
        return (self._public_key, self._balance)

    def get_history(self):
        return self._history
      
    
class Market:
    #Contains information on all users, allows them to interact
    #with the blockchain and each other.
    def __init__(self, blockchain, block):
        self.__miners = {}
        self._miner_count = 0
        self.__users = {}
        self.__chain = blockchain
        self.__current_block = block #Create a new block

    def add_user(self, key, individual):
        self.__users[key] = individual

    def add_miner(self, miner):
        self.__miners[miner._index] = miner
        self._miner_count += 1
    
    def add_exchange(self, sender, receiver, amount):
        #Add exchange history to sender and receiver history
        #Add exchange to current block, or push full block to chain
        #  and create a new block
        if (self.__current_block._size == 4):
            self.__current_block = Block() #Create a new current block
            self.__chain.add_block(self.__current_block) #Add block to chain

            print("Pushing full block to chain. Creating new block.")
            print("Current chain size: " + str(self.__chain._size))

        else:
            new_exchange = Exchange(sender, receiver, amount,
                                    self.__current_block.hash)

            #Add exchange object to shared block
            self.__current_block._exchanges[new_exchange._key] = new_exchange
            self.__current_block._size += 1

            #Add copy of exchange object to each user
            self.__users[sender]._history\
                [new_exchange._key] = copy.deepcopy(new_exchange)
            self.__users[receiver]._history\
                [new_exchange._key] = copy.deepcopy(new_exchange)
        
    def transaction(self, sender, receiver, amount):
        #Check sender history before modifying balances and changing
        #the blockchain. Takes public addresses of users as input.
        print("\nBeginning Transaction\n")

        if (sender == receiver):
            print("Invalid Adresses")
            return

        #Get Individual objects from public addresses
        sender_object = self.__users[sender]
        receiver_object = self.__users[receiver]

        #Edge cases
        if (self.__users[sender]._balance < amount or amount < 0):
            print("Insufficient Funds")
            return

        else:
            #Three miners needed to verify sender
            m1, m2, m3 = random.sample(range(1, self._miner_count+1), 3)

            #Check all three verifications
            sender_hist = sender_object._history
            if (self.__miners[m1].verify(sender_hist)
                and self.__miners[m2].verify(sender_hist)
                and self.__miners[m3].verify(sender_hist)):

                sender_object._balance -= amount
                receiver_object._balance += amount

                #Take care of full blocks, and transfer balances
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
        self.__chain = chain #public blockchain

    def verify(self, sender_hist):
        #Does the sender history match the transactions in the
        #blockchain? True if so, otherwise false.
        for key, exch in sender_hist.items():
            if exch._amount != \
               self.__chain._blocks[exch._block]._exchanges[key]._amount:
                return False #incorrect exchange records will return false
            
        print("Verified") #Three of these printed indicate success
        return True

    
def build_sample_market():
    #Tests
    b = Block() #make initial block
    c = Chain(b) #create chain with block
    m = Market(c,b) #start market with chain

    miners = [Miner(1, c),
              Miner(2, c),
              Miner(3, c),
              Miner(4, c),
              Miner(5, c),
              Miner(6, c),
              Miner(7, c),
              Miner(8, c)]
    
    for i in miners:
        m.add_miner(i)
    
    inds = [Individual(300, "Marcy"),
            Individual(20, "David"),
            Individual(400, "Charles"),
            Individual(7000, "Lauren"),
            Individual(5000, "Dobby"),
            Individual(89, "Ellen")]

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

    m.transaction(inds[0]._public_key, inds[1]._public_key, 5)

    for i in inds:
        print(i.public_info())

def main():
    build_sample_market()
main()
