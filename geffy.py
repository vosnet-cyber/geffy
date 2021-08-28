#!/usr/bin/env python3 

import binascii
import requests
import json
import argparse
import time
import datetime
from datetime import date
from web3 import Web3
from web3.middleware import geth_poa_middleware

# Collect command line arguments
cmdl_args = argparse.ArgumentParser(
	formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=80, width=130),
	description='A Go-Ethereum blockchain data parser to look for images embedded in the chain',
	epilog='When using IPC local search, ensure your blockchain syncing active using e.g. \'geth --goerli\'')

cmdl_args.add_argument('sd', metavar='Start-Date', help='Format DD/MM/YYYY')
cmdl_args.add_argument('ed', metavar='End-Date', help='Format DD/MM/YYYY')
cmdl_args.add_argument('-c', metavar='{IPC/HTTP}', default='IPC', choices=['IPC', 'HTTP'], help='Connection type: IPC or HTTP (Default = IPC)')
cmdl_args.add_argument('-e', metavar='IPC Path/URL', default='~/.ethereum/goerli/geth.ipc', help='IPC Local Path or HTTP URL Endpoint (Default IPC: ~/.ethereum/goerli/geth.ipc) ')
args = cmdl_args.parse_args()

today = date.today().strftime('%d/%m/%Y')
# Convert user input dates to list of integers
tdList = today.split('/')
sdList = args.sd.split('/')
edList = args.ed.split('/')
tDate = [int(i) for i in tdList]
sDate = [int(i) for i in sdList]
eDate = [int(i) for i in edList]

# Convert dates to epoch values
tEpoch = int(datetime.datetime(tDate[2], tDate[1], tDate[0], 0, 0).timestamp())
sEpoch = int(datetime.datetime(sDate[2], sDate[1], sDate[0], 0, 0).timestamp())
eEpoch = int(datetime.datetime(eDate[2], eDate[1], eDate[0], 0, 0).timestamp())

geth_api = 'https://api-goerli.etherscan.io/api' # Hardcoded api URL used to search for start/end block ID's

# Define script functions
def getBlockId(epoch):
	headers = { 'User-Agent': 'vosNET awesome GETH blockchain scanner' }
	params = { 'module': 'block', 'timestamp': epoch, 'action': 'getblocknobytime', 'closest': 'before' }
	r = requests.get(geth_api, params=params, headers=headers)
	rc = r.status_code

	if rc == 200:
		data = r.text
		json_data = json.loads(data)
		blockID = int(json_data['result'])
		return blockID
	else:
		print(f'\n\033[1;31m[!] Connection Error - Web Response Code = {str(rc)}\033[0;0m')
		print(f'\033[1;31m[!] Check Blockchain API URL {geth_api} is online\033[0;0m')
		exit()

def getBlocks():
	if args.c == 'HTTP' :
		checkStr = args.e[0:4].lower() # amend this with if args.e.startswith(args.c.lower()) maybe?
		if checkStr == 'http' :
			w3 = Web3(Web3.HTTPProvider(args.e))
			w3.middleware_onion.inject(geth_poa_middleware, layer=0)
		else:
			print(f'\n\033[1;31m[!] Connection Type {args.c} selected but {args.c} URL not provided\033[0;0m')
			cmdl_args.print_help()
			exit()
	else:
		w3 = Web3(Web3.IPCProvider(args.e))
		w3.middleware_onion.inject(geth_poa_middleware, layer=0)

	print(f'\n\033[1;32m[*]\033[0;0m Attempting to connect to {args.c} endpoint...')
	if w3.isConnected() == True:
		print('\033[1;32m[*]\033[0;0m Connection Established!\n')
		print('\033[1;32m[*]\033[0;0m Begin Writing RAW Data Output to \'raw_data.txt\'...\n')
		print('\033[1;32m[*]\033[0;0m Searching For Image SOF & EOF Signatures...')
		counter = 0
		with open('raw_data.txt', 'w') as datafile:
			for blockID in range(sBlockID, eBlockID):
				counter += 1
				getBlockData(w3, blockID, datafile)
				print(f'\033[1;32m[*]\033[0;0m Getting Block Data: {counter} / {blockRange}', end='\r')
	else:
		print('\n\033[1;31m[!] Connection Failed, is \"geth.ipc\" file or HTTP endpoint available?')
		exit()

def getBlockData(w3, blockID, datafile):
	blockData = w3.eth.getBlock(blockID, True)
	try:
		tData = blockData['transactions']
		if tData != 0:
			for txns in tData:
				data = txns['input'][3:] # Strips the 0x0 value at begining of string
				senderID = txns['from'][2:] # Strips the 0x vlaue at begining of string
				chkData(data, blockID, tData.index(txns))

				datafile.write('=' * 10 + '| DATA START |' + '=' * 10 + '\n')
				datafile.write('Block ID : ' + str(blockID) + '\n')
				datafile.write('Sender ID : ' + str(senderID) +'\n')
				datafile.write('-' * 40 + '\n')
				datafile.write(data)
				datafile.write('\n')
				datafile.write('=' * 10 + '| DATA END |' + '=' * 10 + '\n\n')
		else:
			pass
	except KeyError:
		pass

def chkData(data, blockID, txns):
	sof = False # Start of file
	eof = False # End of file
	""" 
	Set start of file and end of file values
	The hex values can be found on wikipedia
	Might look to make this an option on the cmd line but hardcoded for now
	Might add support for GIF files too at somepoint if required
	"""
	fileSOF = { 
		'jpg_mb': {'hex':'FFD8FF', 'ext':'jpg'},
		'png_mb': {'hex':'89504E470D0A1A0A', 'ext':'png'}
	}

	fileEOF = {
		'jpg_eoi': {'hex':'FFD9'},
		'png_iend': {'hex':'49454E44AE426082'}
	}

	for mb in fileSOF.items():
		mbHex = mb[1]['hex']
		ext = mb[1]['ext']
		if data.upper().startswith(mbHex):
			print(f'\033[1;36m[+]\033[0;0m {ext.upper()} SOF Signature Found in Block {blockID}, Transaction ID {txns}')
			sof = True
			portion = 'SOF'
		else:
			pass

	for ft in fileEOF.items():
		fHex = ft[1]['hex']
		if data.upper().endswith(fHex):
			print(f'\033[1;36m[+]\033[0;0m {ext.upper()} EOF Signature Found in Block {blockID}, Transaction ID {txns}')
			eof = True
			portion = 'EOF'
		else:
			pass

	if sof == True and eof == False:
		print('\033[1;33m[!]\033[0;0m Only Discovered SOF in this Block...')
		saveHex(portion, data, blockID, ext, txns)
	if sof == False and eof == True:
		print('\033[1;33m[!]\033[0;0m Only Discovered EOF in this Block...')
		saveHex(portion, data, blockID, ext, txns)
	if sof == True and eof == True:
		print(f'\033[1;32m[*]\033[0;0m Complete Image Found in {blockID}!')
		saveImg(data, blockID, ext)

def saveImg(data, blockID, ext):
	imgFile = f'{blockID}.{ext}'
	with open(imgFile, 'wb') as image:
		try:
			image.write(binascii.unhexlify(data))
			print(f'\033[1;32m[*]\033[0;0m Complete Image Saved As : {imgFile}\n')
		except Exception as error:
			print(f'\n\033[1;31m[!] Save Image Failed. Error : {error}\033[0;0m')
			return

def saveHex(portion, data, blockID, ext, txns):
	hexFile = f'{blockID}_TID{txns}_{ext}_{portion}.txt'
	with open(hexFile, 'w') as hexData:
		hexData.write(data)
	print(f'\033[1;33m[!]\033[0;0m Incomplete Image Hex Portion Saved As : {hexFile}\n')

def main():
	global sBlockID, eBlockID, blockRange
	# Date sanity checks
	if sEpoch > tEpoch :
		print('\n\033[1;33mStart-Date cannot be in the future, see help\033[0;0m\n')
		cmdl_args.print_help()
	elif sEpoch > eEpoch :
		print('\n\033[1;33mStart-Date cannot be after End-Date, see help\033[0;0m\n')
		cmdl_args.print_help()
	else:
		# Find start/end block ID's and calculate number of blocks to scan
		print(f'\n\033[1;32m[*]\033[0;0m Finding First Block ID for Start-Date: {args.sd}')
		sBlockID = getBlockId(sEpoch)
		print(f'\033[1;32m[*]\033[0;0m FOUND! Start Block ID = {str(sBlockID)}')
		print(f'\n\033[1;32m[*]\033[0;0m Finding Last Block ID for End-Date: {args.ed}')
		
		time.sleep(5) # Sleep 5 seconds to stay under API max rate limit
		
		eBlockID = getBlockId(eEpoch)
		print(f'\033[1;32m[*]\033[0;0m FOUND! End Block-ID Code = {str(eBlockID)}')

		blockRange = eBlockID - sBlockID
		print(f'\n\033[1;32m[*]\033[0;0m Number of blocks in date range to scan {blockRange}')
		time.sleep(1)
		getBlocks()

		print(
			'''
\n\033[1;36mAll blocks in specified range scanned. Any complete images will be ready for viewing.

Partial HEX files will need to be combined where possible. TIP: Check the \'\033[0;0mraw_data.txt\033[1;36m\' file for matching sender ID\'s of both the SOF and EOF portions.
If the sender ID's match and the block ID's are sequential they probably should be combined and converted back from HEX to an image binary file.
This can be done as follows:
\033[0;0mCommand: cat <SOF HEX File> > img.hex && cat <EOF HEX File> >> img.hex')
Command: xxd -p -r img.hex > img.<img extension>

Thanks for using the script, I hope you found it useful.
Vosman @vosNET-Cyber
		''')

main()