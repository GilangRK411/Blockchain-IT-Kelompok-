import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import requests
from flask import Flask, jsonify, request
import ecdsa
import binascii

class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()

        # Buat Genesis Block
        self.new_block(previous_hash='1', proof=100)

    def register_node(self, address):
        """Menambahkan node baru ke daftar node"""
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('URL node tidak valid')

    def valid_chain(self, chain):
        """Memvalidasi blockchain dari node lain"""
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            # Cek hash
            last_block_hash = self.hash(last_block)
            if block['previous_hash'] != last_block_hash:
                return False
            # Cek Proof of Work
            if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """Algoritma Konsensus: Mengganti rantai kita dengan rantai terpanjang di network"""
        neighbors = self.nodes
        new_chain = None
        max_length = len(self.chain)

        for node in neighbors:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True
        return False

    def new_block(self, proof, previous_hash=None):
        """Membuat Block baru di Blockchain"""
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def verify_signature(self, sender_public_key, recipient, amount, signature):
        """Memvalidasi digital signature menggunakan ECDSA"""
        try:
            # Pengecualian untuk transaksi Mining Reward (sender = "0")
            if sender_public_key == "0":
                return True
                
            public_key_bytes = binascii.unhexlify(sender_public_key)
            vk = ecdsa.VerifyingKey.from_string(public_key_bytes, curve=ecdsa.SECP256k1)
            message = f"{sender_public_key}{recipient}{amount}".encode()
            signature_bytes = binascii.unhexlify(signature)
            return vk.verify(signature_bytes, message)
        except Exception as e:
            return False

    def new_transaction(self, sender, recipient, amount, signature):
        """Menambahkan transaksi baru ke mempool setelah divalidasi"""
        if not self.verify_signature(sender, recipient, amount, signature):
            return False

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'signature': signature
        })
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        last_proof = last_block['proof']
        last_hash = self.hash(last_block)
        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


# Instansiasi Node
app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', '')
blockchain = Blockchain()

# ==========================================
# ENDPOINT BLOCKCHAIN UTAMA
# ==========================================

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    # Miner Reward: Pengirim adalah "0" menandakan koin baru ditambang.
    # Signature kosong karena ini adalah transaksi sistem.
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=10, # Reward untuk miner
        signature=""
    )

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "Block baru berhasil ditambang!",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount', 'signature']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'], values['signature'])
    
    if index:
        response = {'message': f'Transaksi akan ditambahkan ke Block {index}'}
        return jsonify(response), 201
    else:
        response = {'message': 'Digital Signature TIDAK VALID! Transaksi ditolak.'}
        return jsonify(response), 403

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Silakan berikan daftar nodes yang valid", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'Node baru telah ditambahkan',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        response = {
            'message': 'Rantai telah diganti dengan yang terpanjang',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Rantai kita sudah otoritatif (paling mutakhir)',
            'chain': blockchain.chain
        }
    return jsonify(response), 200

# ==========================================
# ENDPOINT HELPER UNTUK PENGUJIAN POSTMAN
# ==========================================

@app.route('/wallet/new', methods=['GET'])
def create_wallet():
    """Membuat Private Key dan Public Key baru untuk pengujian"""
    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    response = {
        'private_key': binascii.hexlify(sk.to_string()).decode(),
        'public_key': binascii.hexlify(vk.to_string()).decode()
    }
    return jsonify(response), 200

@app.route('/wallet/sign', methods=['POST'])
def sign_transaction():
    """Helper untuk membuat digital signature menggunakan private key"""
    values = request.get_json()
    private_key_hex = values.get('private_key')
    recipient = values.get('recipient')
    amount = values.get('amount')

    sk_bytes = binascii.unhexlify(private_key_hex)
    sk = ecdsa.SigningKey.from_string(sk_bytes, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    public_key = binascii.hexlify(vk.to_string()).decode()

    message = f"{public_key}{recipient}{amount}".encode()
    signature = sk.sign(message)
    
    response = {
        'sender_public_key': public_key,
        'recipient': recipient,
        'amount': amount,
        'signature': binascii.hexlify(signature).decode()
    }
    return jsonify(response), 200

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='Port untuk menjalankan Node')
    args = parser.parse_args()
    
    print(f"Node berjalan di alamat: http://127.0.0.1:{args.port}")
    print(f"Node Identifier (Miner ID): {node_identifier}")
    app.run(host='0.0.0.0', port=args.port)