from web3 import Web3
from eth_account import Account
import time
import sys
import os

# Data jembatan (bridge data)
from data_bridge import data_bridge
from keys_and_addresses import private_keys, my_addresses, labels
from network_config import networks

# Fungsi untuk memusatkan teks
def center_text(text):
    terminal_width = os.get_terminal_size().columns
    lines = text.splitlines()
    centered_lines = [line.center(terminal_width) for line in lines]
    return "\n".join(centered_lines)

# Fungsi untuk membersihkan terminal
def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

ascii_art = """
 __     ___ _    _ _            _     _ 
 \ \   / (_) | _(_) |_ ___  ___| |__ (_)
  \ \ / /| | |/ / | __/ _ \/ __| '_ \| |
   \ V / | |   <| | || (_) \__ \ | | | |
    \_/  |_|_|\_\_|\__\___/|___/_| |_|_|
"""

description = """
Bot Auto Bridge  https://bridge.t1rn.io/
"""

# Warna dan simbol untuk setiap chain
chain_symbols = {
    'Arbitrum Sepolia': '\033[34m',   
    'OP Sepolia': '\033[91m',         
    'Blast Sepolia': '\033[93m',     
    'Base Sepolia': '\033[96m'       
}

# Warna hijau
green_color = '\033[92m'
reset_color = '\033[0m'
menu_color = '\033[95m'  # Warna untuk teks menu

# URLs Explorer untuk setiap jaringan
explorer_urls = {
    'Arbitrum Sepolia': 'https://sepolia.arbiscan.io/tx/',
    'OP Sepolia': 'https://sepolia-optimism.etherscan.io/tx/',
    'Blast Sepolia': 'https://testnet.blastscan.io/tx/',
    'Base Sepolia': 'https://sepolia.basescan.org/tx/',
    'BRN': 'https://brn.explorer.caldera.xyz/tx/'
}

# Fungsi untuk mendapatkan saldo BRN
def get_brn_balance(web3, my_address):
    balance = web3.eth.get_balance(my_address)
    return web3.from_wei(balance, 'ether')

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
        gas_limit = gas_estimate + 50000  # Increase safety margin
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
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        # Mendapatkan saldo terkini
        balance = web3.eth.get_balance(my_address)
        formatted_balance = web3.from_wei(balance, 'ether')

        # Mendapatkan link explorer
        explorer_link = f"{explorer_urls[network_name]}{web3.to_hex(tx_hash)}"

        # Menampilkan informasi transaksi
        print(f"{green_color}📤 Alamat Pengirim: {account.address}")
        print(f"⛽ Gas digunakan: {tx_receipt['gasUsed']}")
        print(f"🗳️  Nomor blok: {tx_receipt['blockNumber']}")
        print(f"💰 Saldo ETH: {formatted_balance} ETH")
        brn_balance = get_brn_balance(Web3(Web3.HTTPProvider('https://brn.rpc.caldera.xyz/http')), my_address)
        print(f"🔵 Saldo BRN: {brn_balance} BRN")
        print(f"🔗 Link Explorer: {explorer_link}\n{reset_color}")

        return web3.to_hex(tx_hash), value_in_ether
    except Exception as e:
        print(f"Error sending transaction: {e}")
        return None, None

# Fungsi untuk memproses transaksi pada jaringan tertentu
def process_network_transactions(network_name, bridges, chain_data, successful_txs):
    web3 = Web3(Web3.HTTPProvider(chain_data['rpc_url']))
    if not web3.is_connected():
        raise Exception(f"Tidak dapat terhubung ke jaringan {network_name}")

    for bridge in bridges:
        for i, private_key in enumerate(private_keys):
            account = Account.from_key(private_key)
            data = data_bridge[bridge]
            result = send_bridge_transaction(web3, account, my_addresses[i], data, network_name)
            if result:
                tx_hash, value_sent = result
                successful_txs += 1

                # Check if value_sent is valid before formatting
                if value_sent is not None:
                    print(f"{chain_symbols[network_name]}🚀 Total Tx Sukses: {successful_txs} | {labels[i]} | Bridge: {bridge} | Jumlah Bridge: {value_sent:.5f} ETH ✅{reset_color}\n")
                else:
                    print(f"{chain_symbols[network_name]}🚀 Total Tx Sukses: {successful_txs} | {labels[i]} | Bridge: {bridge} ✅{reset_color}\n")

                print(f"{'='*150}")
                print("\n")
            time.sleep(7)

    return successful_txs

# Fungsi untuk menampilkan menu pilihan chain
def display_menu():
    print(f"{menu_color}Pilih chain untuk menjalankan transaksi:{reset_color}")
    print("")
    print(f"{chain_symbols['Arbitrum Sepolia']}1. ARB -> OP, BLAST, BASE Sepolia{reset_color}")
    print(f"{chain_symbols['OP Sepolia']}2. OP -> ARB, BLAST, BASE Sepolia{reset_color}")
    print(f"{chain_symbols['Blast Sepolia']}3. BLAST -> ARB, OP, BASE Sepolia{reset_color}")
    print(f"{chain_symbols['Base Sepolia']}4. BASE -> ARB, OP, BLAST Sepolia{reset_color}")
    print(f"{menu_color}5. Jalankan Semua{reset_color}")
    print("")
    choice = input("Masukkan pilihan (1-5): ")
    return choice

def main():
    print("\033[92m" + center_text(ascii_art) + "\033[0m")
    print(center_text(description))
    print("\n\n")

    successful_txs = 0

    while True:
        # Tampilkan menu dan dapatkan pilihan pengguna
        choice = display_menu()
        clear_terminal()  # Membersihkan terminal sebelum menampilkan transaksi baru
        print("\033[92m" + center_text(ascii_art) + "\033[0m")
        print(center_text(description))
        print("\n\n")

        try:
            if choice == '1':
                while True:
                    successful_txs = process_network_transactions('Arbitrum Sepolia', ["ARB - BASE", "ARB - OP SEPOLIA", "ARB - BLAST"], networks['Arbitrum Sepolia'], successful_txs)
            elif choice == '2':
                while True:
                    successful_txs = process_network_transactions('OP Sepolia', ["OP - BLAST", "OP - ARB", "OP - BASE"], networks['OP Sepolia'], successful_txs)
            elif choice == '3':
                while True:
                    successful_txs = process_network_transactions('Blast Sepolia', ["BLAST - OP", "BLAST - ARB", "BLAST - BASE"], networks['Blast Sepolia'], successful_txs)
            elif choice == '4':
                while True:
                    successful_txs = process_network_transactions('Base Sepolia', ["BASE - OP", "BASE - ARB", "BASE - BLAST"], networks['Base Sepolia'], successful_txs)
            elif choice == '5':
                while True:
                    successful_txs = process_network_transactions('Arbitrum Sepolia', ["ARB - BASE", "ARB - OP SEPOLIA", "ARB - BLAST"], networks['Arbitrum Sepolia'], successful_txs)
                    successful_txs = process_network_transactions('OP Sepolia', ["OP - BLAST", "OP - ARB", "OP - BASE"], networks['OP Sepolia'], successful_txs)
                    successful_txs = process_network_transactions('Blast Sepolia', ["BLAST - OP", "BLAST - ARB", "BLAST - BASE"], networks['Blast Sepolia'], successful_txs)
                    successful_txs = process_network_transactions('Base Sepolia', ["BASE - OP", "BASE - ARB", "BASE - BLAST"], networks['Base Sepolia'], successful_txs)
            else:
                print("Pilihan tidak valid. Silakan coba lagi.")

        except KeyboardInterrupt:
            print("\nScript dihentikan oleh pengguna. ✋")
            print(f"Total transaksi sukses: {successful_txs} 🎉")
            sys.exit(0)
        except Exception as e:
            print(f"Error occurred: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
