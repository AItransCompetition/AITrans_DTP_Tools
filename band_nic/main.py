
from aitrans_shell import AITrans_tc
import os


def test_bond_nic():
    '''
    说明
    C SOCKET 服务绑定网卡测试示例

    结合common.h来看，
    RATIO：设置为1，保证发端等间隔发包
    发端：SEND_IP 亦INTERFAXENAME网卡IP
    手端：RECV_IP 亦RECV_INTERFAXENAME网卡IP

    整个过程：发端 -> INTERFAXENAME网卡 -> RECV_INTERFAXENAME网卡 -> 收端
    因BUFF_SIZE设置为1200，即约9.375kbit，客户端sleep_unit = 1000000 us，即约为9kbit/s的带宽
    当tc设置INTERFAXENAME网卡带宽低于这个值时，queue_delay参数会放生变化，当带宽低于这个值时，queue_delay不变，因为一次都发送完了

    socket服务中的网卡绑定在注释“//bind nic”下方，可直接CTRL+F
    绑定网卡需要导包 #include <net/if.h>
    '''

    obj = AITrans_tc()

    #TC 设置网卡lo的出带宽
    nic_name = "lo"

    #默认BUFF_SIZE设置为1200，本次限制5kbit/s，可以更改rate测试10kbit/s的情况
    rate = 5

    print(obj.tc_add_simple_brandwidth(nic_name, rate, qlevel=1))

    #socket服务
    os.system("gcc bw_udp_c.c -o udp_c_test")
    os.system("gcc bw_udp_s.c -o udp_s_test")

    os.system("./udp_s_test &")
    os.system("./udp_c_test")