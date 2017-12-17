# PyChain

PyChain uses 5 Classes:

Chain: contains Block objects in a hash map

Block: contains Exchange objects in a hash map

Exchange: contains information on the two users, and other exchange details

Individual: contains user account information

Miner: used to verify transactions, keep separate, more secure copies of the blockchain

Market: contains users, some blockchain information -> facilitates transactions

#How to Use

In build_sample_market, create an origin block, an initial chain that takes the origin block, and a market, which takes both. 
Create individuals, at least three miners, and use the market transaction function to facilitate trades between individuals.
