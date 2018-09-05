import zerorpc
import factom_gateway

chain_seq = "10"
entry_address = "EC2so2gnJztv7KVjCjpTZNMNKVwZw8eztezU3L8rE4kdQrSHJrCm"
b = factom_gateway.BitEmrs(chain_seq, entry_address)


class BitEmrsRPC(object):

    def login(self, userID):
        res = b.login(userID)
        print res
        return res

    def query(self, userID, Hash):
        return b.get_record_from_fct(userID, Hash)

    def append(self, userID, cipher):
        return b.post_record_to_fct(chain_seq, entry_address, userID, cipher)

    def showAddress(self):
        return b.show_address()

s = zerorpc.Server(BitEmrsRPC())
s.bind("tcp://0.0.0.0:4242")
s.run()
