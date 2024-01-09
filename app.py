from flask import Flask, render_template, request
from web3 import Web3
import time
from collections import deque
import threading

# Creates the Flask app
app = Flask(__name__)

# Connect to an Ethereum node
web3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/bfddb9d1b3864da6be2882e641328696'))

# Replace Ethereum address if required for testing
address_to_query = '0xBE0eB53F46cd790Cd13851d5EFf43D12404d33E8'

# Cache to store hourly balances for 12 hours
balance_history = deque(maxlen=12)

# Test data for checking percentage difference in balance in the last 12 hours
timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
balance_history.append((timestamp, 2000000))

# Gets the balance from 12 hours ago from the cache i.e. the least recent balance in the cache
def get_least_recent_balance():
    if balance_history:
        least_recent_timestamp, least_recent_balance = balance_history[0]
        print(f"Least recent balance at {least_recent_timestamp}: {least_recent_balance} Ether")
        return least_recent_balance
    else:
        print("No balance history available yet.")

# Runs in a separate thread and continuously fetches the account balance every hour while maintaining the cache
# of balances for the last 12 hours
def update_cache_periodically(interval_hours=1):
    while True:
        balance = web3.eth.get_balance(address_to_query)
        balance_in_ether = web3.from_wei(balance, 'ether')
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"{timestamp} - Balance: {balance_in_ether} Ether for address: {address_to_query}")
        balance_history.append((timestamp, balance_in_ether))
        time.sleep(interval_hours * 3600)

# Starts the thread for maintaining the cache
balance_thread = threading.Thread(target=update_cache_periodically)
balance_thread.start()

# Handles the 'Get Balance' button click in the web page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Call get_balance API
        balance = get_balance()
        return render_template('index.html', balance=balance)

    # Display the output
    return render_template('index.html', balance=None)

# Returns the current balance in the address along with the necessary attributes to be displayed in the web page
def get_balance():
    # Get the current balance
    current_balance = web3.eth.get_balance(address_to_query)
    current_balance_in_ether = web3.from_wei(current_balance, 'ether')

    # Get the least recent balance
    least_recent_balance = get_least_recent_balance()

    # Calculate the percentage difference
    percentage_difference = ((current_balance_in_ether - least_recent_balance) / least_recent_balance) * 100

    return {
        'address': address_to_query,
        'current_balance': current_balance_in_ether,
        'least_recent_balance': least_recent_balance,
        'percentage_difference': percentage_difference
    }

if __name__ == '__main__':
    app.run(debug=True)
