from web3 import Web3
from eth_account import Account
import time
import sys
import os
from data_bridge import data_bridge
from keys_and_addresses import private_keys, my_addresses, labels
from network_config import networks

def center_text(text):
    terminal_width = os.get_terminal_size().columns
    lines = text.splitlines()
    centered_lines = [line.center(terminal_width) for line in lines]
    return "\n".join(centered_lines)

ascii_art = """
 __     ___ _    _ _            _     _ 
 \ \   / (_) | _(_) |_ ___  ___| |__ (_)
  \ \ / /| | |/ / | __/ _ \/ __| '_ \| |
   \ V / | |   <| | || (_) \__ \ | | | |
    \_/  |_|_|\_\_|\__\___/|___/_| |_|_|

"""

# Deskripsi teks
description = """
Bot Auto Bridge  https://bridge.t1rn.io/
"""

print("\033[92m" + center_text(ascii_art) + "\033[0m")
print(center_text(description))
print("\n\n")

# Warna yang sesuai dengan setiap chain
chain_colors = {
    'Arbitrum Sepolia': '\033[91m',  # Merah untuk Arbitrum
    'OP Sepolia': '\033[94m',        # Biru untuk OP
    'Blast Sepolia': '\033[93m',     # Kuning untuk Blast
    'Base Sepolia': '\033[95m'       # Ungu untuk Base
}

# Reset warna
reset_color = '\033[0m'

# Fungsi untuk membuat dan mengirim transaksi
def send_bridge_transaction(web3, account, my_address, data, network_name):
    nonce = web3.eth.get_transaction_count(my_address, 'pending')
    value_in_ether = 0.011
    value_in_wei = web3.to_wei(value_in_ether, 'ether')

    try:
        gas_estimate = web3.eth.estimate_gas({
            'to': networks[network_name]['contract_address'],
            'from': my_address,
            'data': data,
            'value': value_in_wei
        })
        gas_limit = gas_estimate + 10000
    except Exception as e:
        print(f"Error estimating gas: {e}")
        return None

    base_fee = web3.eth.get_block('latest')['baseFeePerGas']
    priority_fee = web3.to_wei(5, 'gwei')
    max_fee = base_fee + priority_fee

    transaction = {
        'nonce': nonce,
        'to': networks[network_name]['contract_address'],
        'value': value_in_wei,
        'gas': gas_limit,
        'maxFeePerGas': max_fee,
        'maxPriorityFeePerGas': priority_fee,
        'chainId': networks[network_name]['chain_id'],
        'data': data
    }

    try:
        signed_txn = web3.eth.account.sign_transaction(transaction, account.key)
    except Exception as e:
        print(f"Error signing transaction: {e}")
        return None

    try:
        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        return web3.to_hex(tx_hash), value_in_ether
    except Exception as e:
        print(f"Error sending transaction: {e}")
        return None, None

successful_txs = 0

try:
    while True:
        # Transaksi dari Arbitrum Sepolia
        network_name = 'Arbitrum Sepolia'
        web3 = Web3(Web3.HTTPProvider(networks[network_name]['rpc_url']))
        if not web3.is_connected():
            raise Exception(f"Tidak dapat terhubung ke jaringan {network_name}")

        bridges = ["ARB - BASE", "ARB - OP SEPOLIA", "ARB - BLAST"]
        for bridge in bridges:
            for i, private_key in enumerate(private_keys):
                account = Account.from_key(private_key)
                data = data_bridge[bridge]
                result = send_bridge_transaction(web3, account, my_addresses[i], data, network_name)
                if result:
                    tx_hash, value_sent = result
                    successful_txs += 1
                    print(f"{chain_colors[network_name]}🚀 Tx Hash: {tx_hash} | Total Tx Sukses: {successful_txs} | {labels[i]} | Bridge: {bridge} | Jumlah: {value_sent:.5f} ETH ✅{reset_color}\n")
                time.sleep(10)

        # Transaksi dari OP Sepolia
        network_name = 'OP Sepolia'
        web3 = Web3(Web3.HTTPProvider(networks[network_name]['rpc_url']))
        if not web3.is_connected():
            raise Exception(f"Tidak dapat terhubung ke jaringan {network_name}")

        bridges = ["OP - BLAST", "OP - ARB", "OP - BASE"]
        for bridge in bridges:
            for i, private_key in enumerate(private_keys):
                account = Account.from_key(private_key)
                data = data_bridge[bridge]
                result = send_bridge_transaction(web3, account, my_addresses[i], data, network_name)
                if result:
                    tx_hash, value_sent = result
                    successful_txs += 1
                    print(f"{chain_colors[network_name]}🚀 Tx Hash: {tx_hash} | Total Tx Sukses: {successful_txs} | {labels[i]} | Bridge: {bridge} | Jumlah: {value_sent:.5f} ETH ✅{reset_color}\n")
                time.sleep(10)

        # Transaksi dari Blast Sepolia
        network_name = 'Blast Sepolia'
        web3 = Web3(Web3.HTTPProvider(networks[network_name]['rpc_url']))
        if not web3.is_connected():
            raise Exception(f"Tidak dapat terhubung ke jaringan {network_name}")

        bridges = ["BLAST - OP", "BLAST - ARB", "BLAST - BASE"]
        for bridge in bridges:
            for i, private_key in enumerate(private_keys):
                account = Account.from_key(private_key)
                data = data_bridge[bridge]
                result = send_bridge_transaction(web3, account, my_addresses[i], data, network_name)
                if result:
                    tx_hash, value_sent = result
                    successful_txs += 1
                    print(f"{chain_colors[network_name]}🚀 Tx Hash: {tx_hash} | Total Tx Sukses: {successful_txs} | {labels[i]} | Bridge: {bridge} | Jumlah: {value_sent:.5f} ETH ✅{reset_color}\n")
                time.sleep(10)

        # Transaksi dari Base Sepolia
        network_name = 'Base Sepolia'
        web3 = Web3(Web3.HTTPProvider(networks[network_name]['rpc_url']))
        if not web3.is_connected():
            raise Exception(f"Tidak dapat terhubung ke jaringan {network_name}")

        bridges = ["BASE - OP", "BASE - ARB", "BASE - BLAST"]
        for bridge in bridges:
            for i, private_key in enumerate(private_keys):
                account = Account.from_key(private_key)
                data = data_bridge[bridge]
                result = send_bridge_transaction(web3, account, my_addresses[i], data, network_name)
                if result:
                    tx_hash, value_sent = result
                    successful_txs += 1
                    print(f"{chain_colors[network_name]}🚀 Tx Hash: {tx_hash} | Total Tx Sukses: {successful_txs} | {labels[i]} | Bridge: {bridge} | Jumlah: {value_sent:.5f} ETH ✅{reset_color}\n")
                time.sleep(10)

except KeyboardInterrupt:
    print("\nScript dihentikan oleh pengguna. ✋")
    print(f"Total transaksi sukses: {successful_txs} 🎉")
    sys.exit(0)
