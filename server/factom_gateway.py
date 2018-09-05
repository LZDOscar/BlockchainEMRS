#!/usr/bin/env python
# this is a main communication interface for factom block chain
# HAO CHEN

# --------- imports ---------
import os
import csv
import sys
import json
import requests
import sqlite3
import binascii
import time
# --------- classes ---------


class BitEmrs:

    def __init__(self, chain_seq, entry_address):
        self.url = "http://localhost:8089/v2"
        self.url2 = "http://localhost:8088/v2"
        self.bitemrs_chain_dic = {}
        self.bitemrs_entry_dic = {}
        # init a chain for post and inquiry
        # 10 = local chain id ; jackec = Entry Credit Addresses name
        # you can and more chain with local chain id and ec name
        self.init_chain(chain_seq, entry_address)
        self.db_con = sqlite3.connect('cached.db')

    def request(self, method, values):
        """
        private base api
        this function for posting data from bitemrs svr from factom svr.
        url - factom svr url
        action - factom action, compose-chain-submit etc.
        target - factom element, address, chain (name) etc.
        url + action + target gives the whole URL to aceess fcactom svr
        data - the data need to submit.
        """
        jdata = json.dumps(values)
        if method == "factom_walletd":
            return requests.post(self.url, jdata).json()
        else:
            # response 200
            return requests.post(self.url2, jdata).json()

    '''def fct_inquiry(self, method, action, target):
        """
	private base api
        this function for inquiry data from bitemrs svr from factom svr.
        url - factom svr url
        action - factom action, compose-chain-submit etc.
        target - factom element, address, chain (name) etc.
        url + action + target gives the whole URL to aceess fcactom svr
        """

        if method == "factom_walletd":
            return requests.get(self.url+action+"/"+target).json()
        else:
            return requests.get(self.url2+action+"/"+target)
    '''

    def local_validate(self):
        pass

    def init_chain(self, seq, entry_address):
        """
        generate a new chain with humman-read seq for token chain
        """
        values = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "compose-chain",
            "params": {
                "chain": {
                       "firstentry": {
                           "extids": [
                               ("biremrs_chain").encode('hex'),
                               (seq).encode('hex')
                           ],
                           "content": ("NO." + seq + " chain of bitemrs").encode('hex')
                       }
                },
                "ecpub": entry_address
            }
        }
        s = self.request("factom_walletd", values)
        self.request("factomd",  s[u'result'][u'commit'])
        h = self.request("factomd",  s[u'result'][u'reveal'])
        entryhash = h[u'result'][u'entryhash']
        values = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "entry",
            "params": {
                "hash": entryhash
            }
        }
        s = self.request("factomd", values)
        chainid = s[u'result'][u'chainid']
        self.bitemrs_chain_dic.setdefault(seq, chainid)

    def post_record_to_fct(self, seq, entry_address, user_id, enc_content):
        """
        post record to factom with user_id, enc_content
        """
        values = {
                "jsonrpc": "2.0",
                "id": 0,
                "method": "compose-entry",
                "params": {
                    "entry": {
                          "chainid": self.bitemrs_chain_dic[seq],
                          "extids": [
                              ("biremrs_user").encode('hex'),
                           (user_id).encode('hex')
                          ],
                        "content": (enc_content).encode('hex')
                    },
                    "ecpub": entry_address
                }
            }
        s = self.request("factom_walletd", values)
        entry_hashed = s['result']['commit']['params']['message'][14:78]

        # if user exist in list
        if self.bitemrs_entry_dic.has_key(user_id):
            self.bitemrs_entry_dic[user_id].append(entry_hashed)
        else:
            self.bitemrs_entry_dic.setdefault(user_id, [entry_hashed, ])

        # save user_id, entry_hash here(light database)
        self.db_con.execute(
            "INSERT INTO CACHED VALUES ('" + user_id + "', '" + entry_hashed + "');")
        self.db_con.commit()

        self.request("factomd",   s['result']['commit'])
        self.request("factomd",   s['result']['reveal'])
        print   "this is %s" %(time.strftime('%Y-%m-%d %H-%m-%S',time.localtime(time.time())))
        return entry_hashed

    def get_record_from_fct(self, user_id, entry_hashed):
        """
        get record from factom with entry_hashed
        return content
        """
        values = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "entry",
            "params": {
                "hash": entry_hashed
            }
        }
        s = self.request("factomd", values)
        # print jdata
        # now convert HEX to string to print
        print s['result']['content'].decode('hex')
        return s['result']['content'].decode('hex')

    def login(self, user_id):
        """
        a user login in with his/her/its user_id
        return his/her/its entry_hashed list
        """
        cur = self.db_con.execute(
            "select entryhashed from cached where userid='" + user_id + "';")
        cur_list = []
        for row in cur:
            cur_list.append(row)
        return cur_list

    def delete_record(self, user_id, entry_hashed):
        """
        a user login in with his/her/its user_id
        return his/her/its entry_hashed list
        """
        self.db_con.execute(
        "delete from cached where userid='" + user_id + "' and entryhashed='" + entry_hashed + "';" )
        self.db_con.commit()
            
        return True
        #print "delete from cached where userid='" + user_id + "' and entryhashed='" + entry_hashed + "';" 
       


    def show_balance(self, entry_addr):
        values = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "factoid-balance",
            "params": {
                "address": entry_addr
            }
        }
        return self.request("factomd", values)

    def show_address(self):
        values = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "all-addresses"
        }
        return self.request("factom_walletd", values)


# --------- main ---------
if __name__ == '__main__':
    print "testing begin"

    b = BitEmrs("10","EC2so2gnJztv7KVjCjpTZNMNKVwZw8eztezU3L8rE4kdQrSHJrCm")
    print b.bitemrs_chain_dic
    # chenhao = user id ; code = content for encryption info
    b.post_record_to_fct("10", "EC2so2gnJztv7KVjCjpTZNMNKVwZw8eztezU3L8rE4kdQrSHJrCm", "lzd", "code")
    b.post_record_to_fct("10", "EC2so2gnJztv7KVjCjpTZNMNKVwZw8eztezU3L8rE4kdQrSHJrCm", "lzd", "code2")
    b.post_record_to_fct("10", "EC2so2gnJztv7KVjCjpTZNMNKVwZw8eztezU3L8rE4kdQrSHJrCm", "lzd", "code3")
    user_cur = b.db_con.execute("select userid,entryhashed from cached;")
    user_list = []
    for row in user_cur:
        user_list.append(row)
    print user_list
    print b.login("lzd")

    print b.bitemrs_entry_dic
    print b.get_record_from_fct("lzd", b.bitemrs_entry_dic["lzd"][0])
    print b.get_record_from_fct("lzd", b.bitemrs_entry_dic["lzd"][1])

    print b.show_balance("FA1zT4aFpEvcnPqPCigB3fvGu4Q4mTXY22iiuV69DqE1pNhdF2MC")
    print b.show_address()
