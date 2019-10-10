#coding:utf8 

import os, re


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

        status = 0
        for idx, item in enumerate(orders):
            print("Step %d : %s" % (idx+1, item))
            status |= os.system(item) * (1<<idx)

        return status


    def hex_to_ip(self, hx_str, jinzhi=16): 
        val = int(hx_str, jinzhi) 
        ans = [] 
        for _ in range(4): 
            ans.append(str(val % 256)) 
            val = val // 256 
        return '.'.join(ans[::-1])


    def tc_add_simple_brandwidth(self, nic_name, rate, unit="kbit", qtype="tbf"):

        if (qtype == "tbf"):
            status = os.system("tc qdisc add dev {0} parent 1:1 handle 10: tbf rate {1}{2} buffer 1600 limit 3000".format(nic_name, rate, unit)) 
        
        '''
                
        class_id, priority = 11, 1
        flowid = class_id

        status = os.system("tc qdisc add dev %s root handle 1: htb default 11" % (nic_name))
        status += os.system("tc class add dev {0} parent 1: classid 1:{5} {4} rate {1}{3} ceil {2}{3}".format  \
                            (nic_name, rate, ceil_rate, unit, qtype, class_id))
        status += os.system("tc filter add dev  {0} protocol ip parent 1:0 prio {3} u32 match ip dst {1} flowid {2}".format  \
                            (nic_name, dst_ip, flowid, priority))
        '''

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

    '''
    def tc_add_qdisc_delay(self, nic_name, delay_ms="1000"):

        status = os.system("tc qdisc add dev {0} root netem delay {1}ms".format(nic_name, delay_ms))

        return status

    
    def tc_add_qdisc_loss(self, nic_name, loss_pct="0"):

        status = os.system("tc qdisc add dev {0} root netem loss {1}%".format(nic_name, loss_pct))

        return status


    def tc_add_qdisc(self, nic_name, qtype="htb"):

        status = os.system("tc qdisc add dev %s root handle 1: htb default 11") % (nic_name)


        return status


    def tc_get_max_class_id(self, nic_name):

        class_id_list = self.tc_get_class_id_list(nic_name)

        return max(map(lambda x:int(x), class_id_list))


    def tc_get_class_id_list(self, nic_name):

        class_str = self.tc_show_class(nic_name)

        class_id_list = re.findall("[0-9]+:([0-9]+)", class_str)

        return class_id_list


    def tc_show_class(self, nic_name):

        out = os.popen("tc class show dev {0}".format(nic_name))

        return out.read()

    
    def tc_add_class_limit_brand(self, nic_name, rate, ceil_rate, class_id=None, unit="mbit", qtype="htb"):
        
        if not class_id:
            class_id = self.tc_get_max_class_id(nic_name) + 1

        status = os.system("tc class add dev {0} parent 1: classid 1:{5} {4} rate {1}{3} ceil {2}{3}".format  \
                            (nic_name, rate, ceil_rate, unit, qtype, class_id))

        return status


    def tc_show_filter(self, nic_name):

        out = os.popen("tc filter show dev {0}".format(nic_name))

        return out.read()

    
    def tc_add_filter_port(self, nic_name, dport, flowid, priority=1):

        if not str(flowid) in self.tc_get_class_id_list(nic_name):
                print("Error!flowid not find!")
                return -1

        status = os.system("tc filter add dev  {0} protocol ip parent 1:0 prio {4} u32 match ip dport {2} 0xffff flowid {3}".format  \
                            (nic_name, dport, flowid, priority))

        return status
    '''


if __name__ == '__main__':

    #os.system("pwd")

    obj = AITrans_tc()
    #print(obj.tc_get_max_class_id("br-left"))

    nic_name = "test-tap0"
    br_name = "test-br0"
    nic_ip = "169.254.251.7"

    delay_ms = 1000
    delay_range = 10
    loss_pct = 10

    rate = 10
    ceil_rate = 10
    dst_ip = "169.254.251.7"

    #print(obj.create_NIC(br_name, nic_name, nic_ip))
    print(obj.tc_add_qdisc_delay_loss(nic_name, delay_ms, delay_range, loss_pct))
    print(obj.tc_add_simple_brandwidth(nic_name, rate))