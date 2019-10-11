# -*- coding: utf-8 -*-
'''
# @ModuleName : aitrans_shell
# @Function : provide some tc interface to control NIC performance
# @Author : azson
# @Time : 2019/10/10 23:28

# @Environment :
    test on
        OS : Ubuntu 16.04.6 LTS (GNU/Linux 4.4.0-151-generic x86_64)
        python version : Python 3.5.2
        other tools : tc, brctl, tunctl
'''

import os, re
from functools import reduce

class AITrans_tc(object):


    def create_NIC(self, br_name, nic_name, ip):

        print("Func create_NIC")

        orders = [
            "brctl addbr %s" % br_name,
            "ip link set %s up" % br_name,
            "tunctl -t %s" % nic_name,
            "ip link set %s up" % nic_name,
            "brctl addif %s %s" % (br_name, nic_name),
            "ifconfig %s %s up" % (br_name, ip),
            "ifconfig %s promisc" % nic_name,
            "ifconfig %s" % br_name,
            "brctl show"
        ]

        for idx, item in enumerate(orders):

            status = os.system(item)

            if status:
                print("Error!Step %d : %s" % (idx + 1, item))
                break

        return status

    ############################    bridge operation    ############################
    def query_br_list(self):

        out = os.popen("brctl show").read()
        cols = ["bridge name", "bridge id", "STP enabled", "interfaces"]

        ok = reduce(lambda x, y: x in out | y in out, cols)

        if ok:

            out = out[66:].split()
            ans = {
                "cols" : cols,
                "data" : [out[st:st+4] for st in range(0, len(out), 4)]
            }

        else:
            print("Error!Columns not equal standards!Please check \"brctl\" version")
            return None

        return ans


    def query_br_by_col(self, br_name, col="bridge name"):

        br_info = self.query_br_list()
        col_id = br_info['cols'].index(col)
        if col_id != -1:
            for br in br_info['data']:
                if br[col_id] == br_name:
                    return br
        else:
            print("Error!Column \"{0}\" is invalid!".format(col))
            return None

        return None


    def del_br(self, br_name):

        orders = [
            "ifconfig %s down" % br_name,
            "brctl delbr %s" % br_name
        ]

        for idx, item in enumerate(orders):
            status = os.system(item)

            if status:
                print("Error!Step %d : %s" % (idx + 1, item))
                break

        return status


    ############################    nic operation    ############################
    def query_nic(self, nic_name):

        out = os.popen("ifconfig %s" % nic_name).read()

        if "Device not found" in out:
            return None

        return True


    def del_nic(self, nic_name):

        out = os.system("tunctl -d %s" % nic_name)

        return out


    ############################    common operation    ############################
    def hex_to_ip(self, hx_str, jinzhi=16): 
        val = int(hx_str, jinzhi) 
        ans = [] 
        for _ in range(4): 
            ans.append(str(val % 256)) 
            val = val // 256 
        return '.'.join(ans[::-1])


    ############################    tc operation    ############################
    def tc_add_simple_brandwidth(self, nic_name, rate, unit="kbit", qtype="tbf"):

        if (qtype == "tbf"):
            status = os.system("tc qdisc add dev {0} parent 1:1 handle 10: tbf rate {1}{2} buffer 1600 limit 3000". \
                               format(nic_name, rate, unit))

        return status


    def tc_chg_qdisc_delay_loss(self, nic_name, delay_ms, delay_range, loss_pct):

        status = os.system("tc qdisc change dev {0} root handle 1:0 netem delay {1}ms {2}ms {3}%".format  \
                            (nic_name, delay_ms, delay_range, loss_pct))

        return status

    
    def tc_del_qdisc(self, nic_name):

        status = os.system("tc qdisc del dev {0} root".format(nic_name))

        return status


    def tc_add_qdisc_delay_loss(self, nic_name, delay_ms, delay_range, loss_pct):

        status = os.system("tc qdisc add dev {0} root handle 1:0 netem delay {1}ms {2}ms {3}%".format  \
                            (nic_name, delay_ms, delay_range, loss_pct))

        return status


if __name__ == '__main__':

    obj = AITrans_tc()

    nic_name = "test-tap0"
    br_name = "test-br0"
    nic_ip = "169.254.251.7"

    delay_ms = 1000
    delay_range = 10
    loss_pct = 10

    rate = 10
    #ceil_rate = 10
    #dst_ip = "169.254.251.7"

    #print(obj.create_NIC(br_name, nic_name, nic_ip))
    print(obj.tc_add_qdisc_delay_loss(nic_name, delay_ms, delay_range, loss_pct))
    print(obj.tc_add_simple_brandwidth(nic_name, rate))