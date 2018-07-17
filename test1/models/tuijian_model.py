# -*-coding:utf-8-*-
import os, sys, six, simplejson as json, csv, hashlib, time, pandas as pd, numpy as np

from sklearn.externals import joblib
# from libs.utils import load_pkl, PANDAS_EXPORT_KWARGS

MODEL_NAME = "tuijian__2018051718"

# if six.PY2 and sys.getdefaultencoding() != 'utf8':
#     reload(sys)
#     sys.setdefaultencoding('utf8')

##############################
NAN = np.NaN
NAN_STR = r'\N'

PANDAS_COL_REQUEST_TIME = u'Time'
PANDAS_COL_DEVICE_ID = u'DeviceID'

PANDAS_DATA_DICT = (
    (PANDAS_COL_REQUEST_TIME, np.object, 1),
    (PANDAS_COL_DEVICE_ID, np.object, 1),
    (u'Model', np.object, 1),
    (u'Version', np.object, 1),
    (u'Score', np.float64, 1),
)

PANDAS_COL_ENABLES = tuple(col_name for col_name, col_type, enable in PANDAS_DATA_DICT if enable)
PANDAS_COL_NAMES = tuple(col_name for col_name, col_type, enable in PANDAS_DATA_DICT)
PANDAS_COL_DTYPES = dict((col_name, col_type) for col_name, col_type, enable in PANDAS_DATA_DICT)
PANDAS_COL_REMOVES = (PANDAS_COL_REQUEST_TIME, PANDAS_COL_DEVICE_ID)

PANDAS_IMPORT_KWARGS = dict(sep='|', na_values=NAN_STR, header=None, engine='c', encoding='utf8',
                            names=PANDAS_COL_NAMES, dtype=PANDAS_COL_DTYPES, usecols=PANDAS_COL_ENABLES,
                            # error_bad_lines=False, warn_bad_lines=True,
                            )


def csv2df(csvfile, **kwargs):
    kws = PANDAS_IMPORT_KWARGS.copy()
    kws.update(kwargs)
    df = pd.read_csv(csvfile, **kws)
    return df


# def df2csv(df, filename, columns=None, gzip=False, **kwargs):
#     kws = PANDAS_EXPORT_KWARGS.copy()
#     kws.update(kwargs)
#     if not gzip:
#         kws.pop('compression', None)
#     df.to_csv(filename, columns=columns, **kws)


def csv_to_dataframe(row_csv):
    df = pd.read_csv(six.StringIO(row_csv), **PANDAS_IMPORT_KWARGS)
    return df


def format_output(req, fmt='json'):
    req.ret = json.dumps(req.ret)


def format_input(req, fmt=None):  #### req.ioinput,  req.iodata
    if req.debug:
        import pdb;pdb.set_trace()
    data = json.loads(req.data)
    req.data = data


loan_order = ['022', '0224', '0215', '0202', '0218', '025', '0204', '0223', '0226', '0217', '0206', '0219', '0225'
    , '0211', '0231', '0230', '0228', '0205', '0208', '0216', '0203', '027', '0212', '0207', '0229', '0222'
    , '0213', '0201', '024', '0227', '026', '023', '0232', '0221']
manage_order = ["031", "030"]
credit_order = ["050", "051"]

def process(req):
    ret = []
    for item in req.data:
        item['user_type'] = 'loan'
        loan_ids, credit_ids, manage_ids = item.pop('loan_ids', '').split(','), item.pop('credit_ids', '').split(','), item.pop('manage_ids', '').split(',')
        if loan_ids:
            item['loan_ids']   =','.join([i for i in loan_order   if i in loan_ids])

        if manage_ids:
            item['manage_ids'] =','.join([i for i in manage_order if i in manage_ids])

        if credit_ids:
            item['credit_ids'] =','.join([i for i in credit_order if i in credit_ids])

        ret.append(item)
    req.ret = ret

