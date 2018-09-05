import zerorpc
import factom_gateway
import time

chain_seq = "10"
entry_address = "EC2so2gnJztv7KVjCjpTZNMNKVwZw8eztezU3L8rE4kdQrSHJrCm"
b = factom_gateway.BitEmrs(chain_seq, entry_address)


class BitEmrsRPC(object):

    def login(self, ID):
        res = b.login(ID)
        print res
        return res

    def query(self, ID, Hash):
        return b.get_record_from_fct(ID, Hash)

    def append(self, userID, cipher):
        print   "done!  %s " %(time.strftime('%Y-%m-%d %H-%m-%S',time.localtime(time.time())))
        return b.post_record_to_fct(chain_seq, entry_address, userID, cipher)

    def showAddress(self):
        return b.show_address()

    def delete(self, ID, Hash):
        res = b.delete_record(ID, Hash)
        print res
        return res

s = zerorpc.Server(BitEmrsRPC())
s.bind("tcp://0.0.0.0:4242")
s.run()
