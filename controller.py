import env
import argparse
import sys
import dtp_zmq
import threading
from user_func import Policy
from user_func import Train
from user_func import rl_thread



def run_server(ip, port, with_log):
    env_server = env.Env_server(ip, port, with_log)
    env_server.run()


def run_client(ip, port, with_log, config):
    env_client = env.Env_client(ip, port, with_log, config)
    env_client.run()



def main():
    parser = argparse.ArgumentParser(description='DTP arguments')
    
    # parse arguments
    parser.add_argument('server_or_client')
    parser.add_argument('IP')
    parser.add_argument('port')
    parser.add_argument('--config', '-c', help='Path of the config file of client')
    parser.add_argument('--log', '-l', action='store_true', help='Option of print log')

    args = parser.parse_args()
    params = vars(args)

    server_or_client = params['server_or_client']
    ip = params['IP']
    port  = params['port']
    with_log = params['log']
    config = None



    if server_or_client == 'client':

        # start reinforcement learning thread
        policy = Policy()
        train = Train(policy)   
        thread_training = rl_thread(2, 'rl_training', train)
        thread_training.start()

        # start zmq thread
        zmq = dtp_zmq.Zmq_thread(1, 'zmq_thread', policy.all_rl_stats, policy)
        zmq.start()
        

    # start environment

    if server_or_client == 'server':
        run_server(ip, port, with_log)

    elif server_or_client == 'client':

        if params.__contains__('config'):
            config = params['config']
        else:
            print("Error: No config files, client need a config file")
            sys.exit(1)

        run_client(ip, port, with_log, config)


if __name__ == '__main__':
    main()
    

        


        




        
