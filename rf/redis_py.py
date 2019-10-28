#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
# @ModuleName : redis_py
# @Function : opering the redis
# @Author : azson
# @Time : 2019/10/24 14:25
'''

import redis


class Redis_py(object):
    '''
    管理指定redis服务的pool，可避免重复建立、释放连接，默认自带一项连接rd
    '''

    def __init__(self, REDIS_HOST="127.0.0.1", REDIS_PORT=6379):

        self.pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT)
        self.rd = redis.Redis(connection_pool=self.pool)


    def get_redis(self):

        return redis.Redis(connection_pool=self.pool)


    def lpush_elem_by_blockId(self, block_id, others=None):
        '''
        equal to lpush in redis
        :param block_id: list name
        :param others: the elements in list
        :return: succuss num
        '''
        if not others:
            others = [-1, -1, -1]

        ret = 0
        for item in others:
            ret += self.rd.lpush(block_id, item)

        return ret


    def lset_elem_by_blockId(self, block_id, index, value):

        return self.rd.lset(block_id, index, value)


    def get_block_by_id(self, block_id, start=0, end=-1):
        '''
        equal lrange in redis
        :param block_id: list name
        :param start: start point in list
        :param end: end point in list
        :return: the elements of list from start to end
        '''
        block = self.rd.lrange(block_id, start, end)
        block = list(map(lambda x: x.decode(), block))

        return block


    def del_block(self, block_id):
        '''
        delete the block list by list name
        :param block_id: list name
        :return: succuss size
        '''
        return self.rd.ltrim(block_id, 1, 0)


    def reset(self):
        '''
        delete all the list with the pattern 'block_[0-9]*'
        :return: succuss size
        '''
        ret = 0
        for item in self.rd.keys(pattern='block_[0-9]*'):
            ret += self.rd.delete(item)

        return ret


    def get_latest_block_info(self, size=1):
        '''
        get the top size latest block id and information with the pattern 'block_[0-9]*'
        :return: block
        '''
        block_id_list = self.rd.keys(pattern='block_[0-9]*')
        block_id_list = sorted(block_id_list)[-size:]

        if not len(block_id_list):
            return None, None

        block_list = [self.get_block_by_id(item) for item in block_id_list]

        return block_id_list, block_list


    def get_set_item(self, name):

        return self.rd.get(name)


    def set_set_val(self, name, value):

        return self.rd.set(name, value)




if __name__ == '__main__':

    obj = Redis_py()

    r = obj.get_redis()

    # 新数据
    # block_id = "block_521321"
    # print(obj.lpush_elem_by_blockId(block_id, [1, 2, 1, 1, 1, 1, 3, 1]))

    # 旧数据
    # block_id = "block_221321"
    # print(obj.lpush_elem_by_blockId(block_id, [1, 2, 3, 0, -1, 1, 2, 2]))

    # block_id = "block_221321"
    # print(obj.lpush_elem_by_blockId(block_id, [1, 2, 2, 1, -1, 2, 2, 1]))

    # print(obj.lpush_elem_by_blockId(block_id, [1,2,3]))
    # print(obj.get_block_by_id(block_id))
    # print(obj.del_block(block_id))

    ls1 = r.keys(pattern='block_[0-9]*')
    print(ls1)
    print(obj.get_latest_block_info())
    #obj.reset()
    # print(r.delete(ls1[-1]))