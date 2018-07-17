import random,json
from tornado import gen
from simpleweb.finup_handler import REDIS

# 导入pkl模块包



# 处理数据
def get_features(self, req_data):
    usr_unqId = req_data['uuid']

    if 'loan_ids' in req_data and len(req_data['loan_ids']) > 1:
        # 假设用户请求中指定了需要排序的商品（比如用户指定了筛选条件）
        # todo: 起码目前所有lpcode都应该是正整数
        candidate_lpcodes = [int(s) for s in req_data['loan_ids'].split(',')]
    else:
        # 用户没有指定，则当前数据库中所有产品都是候选商品
        candidate_lpcodes = _RedisDB.all_lpcodes

    user_info, items_infos, pairs_infos = yield _RedisDB.query(usr_uniqueId=usr_unqId,
                                                               lpcodes=candidate_lpcodes,
                                                               default_ctr=DEFAULT_CTR)

    # 补充用户信息
    user_info['channelId'] = req_data['channelId']
    user_info['networkType'] = req_data['networkType']
    user_info['pageId'] = req_data['pageId']
    user_info['registered'] = 1 if len(req_data['user_id'].strip()) > 0 else 0
    user_info['authorized'] = 1 if len(req_data['deviceNum'].strip()) > 0 else 0

    # 补充交互信息
    for key, pair_info in pairs_infos.items():
        uniqueId, itemId = key.split("_")
        item_name = _RedisDB.lp_code2name[itemId]

        if 'tags' in req_data and 'applist' in req_data['tags']:
            pair_info['is_installed'] = 1 if (item_name in req_data['tags']['applist']) else 0
        else:
            pair_info['is_installed'] = 0
    #
    raise gen.Return((user_info, items_infos, pairs_infos))


def postproc_new_items(items):
    """ 把新产品随机打乱顺序，放在中间的位置
    """
    old_items = [itemId for itemId in items if itemId not in _RedisDB.new_lpcodes]

    new_items = list(_RedisDB.new_lpcodes)
    random.shuffle(new_items)

    middle_pos = len(old_items) // 2
    return old_items[:middle_pos] + new_items + old_items[middle_pos:]


def postproc_force_top(itemIds, top_lpcode):
    """ 指定产品强制置顶
    """
    if top_lpcode in itemIds:
        itemIds.remove(top_lpcode)
    itemIds.insert(0, top_lpcode)


def _user_type(tags):
    user_type = 1
    if tags and 'getuirisk.white.2018041718.score' in tags and tags['getuirisk.white.2018041718.score'] <= 0.384:
        user_type = 5
    elif tags and 'getui.2018022816.probability(1-0)' in tags and tags['getui.2018022816.probability(1-0)'] >= 0.8328:
        user_type = 1
    elif tags and 'gtlicai.2018050719.label' in tags and tags['gtlicai.2018050719.label'] >= 86:
        user_type = 2
    return user_type
# ------
# ************** query database for features

def predict_proba(req_data):
        req_data = json.loads(req_data)
        req_data['user_type'] =_user_type(req_data['tags'])
        user_info, items_infos, pairs_infos = yield get_features(req_data)

        # ************** run model for ranking
        # return a list of (score,itemId)
        rank_result = _Ranker.rank(user=user_info, items=items_infos, pairs=pairs_infos)
        sorted_items = [itemId for score, itemId in rank_result]

        # ************** apply post rules
        sorted_items = postproc_new_items(sorted_items)
        postproc_force_top(sorted_items,top_lpcode= 1)  # 万卡置顶
        if req_data['user_type'] == 5: # 预授信钱站置顶
            postproc_force_top(sorted_items,top_lpcode=2)

        # ************** return response
        response = req_data  # todo: 包含与request相同的meta信息？？
        response['loan_ids'] = ','.join(str(s) for s in sorted_items)

        return(json.dumps(response))


