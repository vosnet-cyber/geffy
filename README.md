# geffy

## Description
This parser was written to speed up the process of searching through the Gorli Ethereum Testnet for embedded PNG or JPG images. You can search through the blockchain [here](https://goerli.etherscan.io). This might work with other blockchains, but it isn't tested for that but feel free to experiment if you want to.


## Usage
This script can utilise either a local copy of the blockchain on your host via the IPC functionality or query a HTTP URL where the blockchain is hosted. The IPC local search is a lot quicker, and I don't know of any public HTTP locations that you can use but the functionality is there if you want to use it.

To utilise the IPC search function (which is the default) you'll need to grab a copy of the Goerli Ethereum Testnet blockchain and have it synchronising. Once this is done you can run "geffy.py".

I'm sure there are few other ways to get setup, but this is how I did it:
1. Ensure you have the requisite software installed:
	1. Ensure the Golang is updated
	2. Get any other software pre-requisites installed
	3. Clone the Go-Ethereum repository (https://github.com/ethereum/go-ethereum)
	4. Make and run the geth binary
	5. Use geffy.py to select date range and let it find images for you

I know this script may not be the most efficient or best coding in the world and I know my instructions are a bit vague. I'm kind of happy about that because if you found this because of a "challenge" you might be doing I don't want it to be so simple as to be an automatic win. I hope this helps you speed up the enumeration that would be long grind if done manually and that you play around with it, amend it, understand the whole challenge, and learn by trial and error trying to get everything setup and working because that's what those challenges are about.

Other resources:
https://geth.ethereum.org/docs/install-and-build/installing-geth
https://golang.org/dl/


## What Happens
When you get this working, the script will calculate the amount of blocks needed to scan in the date range you specify. It will then scan all blocks and output any potential images or parts of images it finds. 


----------------------
Vosman @vosNET-Cyber
