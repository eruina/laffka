class Configuration():
    #provide user and password, as well as 12 words mnemonic
    user=''
    password=''
    btc_master_key = ''

    secret_key='supersecretkey' #change those
    salt = 'salt' #address salt in db for order id

    shop_name="Laffkashop" #Shop name
    shop_url="laffka6wwduoexvb.onion" #shop url

    database_url = './db/main'  #database location
    wtf_csrf = True

    #debugging stuff
    btc_net = "Main"  # Test for testnet, otherwise MainNet
    debugging = True
    port=5678 #Port to serve for debugging or no. if not set, 5000 applied
    update_rate_sec = 60  # checking btc rate every ... seconds
    update_tx_sec = 300  # checking TX's every ... seconds.
    check_cutoff=60*60*24*30 #30 days in seconds


    #dont modify below
    import binascii, os, hashlib
    user=hashlib.sha224(user.encode('utf-8')).hexdigest()
    password=hashlib.sha224(password.encode('utf-8')).hexdigest()
    #secret_key = binascii.hexlify(os.urandom(24))
    header=shop_name+" - "+shop_url
    if btc_net=="Test":
        tx_url="https://testnet.blockchain.info/q/addressbalance/" #if Configuration.btc_net Test then testnet, mainnet
    else:
        tx_url="https://blockchain.info/q/addressbalance/" #otherwise
