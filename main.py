# ------------------------------------------------------------------------------
# モジュールのインポート
# ------------------------------------------------------------------------------
# 標準モジュール
import os
import json
import logging
import pprint

# 自作モジュール
from backlog  import BackLog
from dynamodb import DynamoDB
import schedule

# ------------------------------------------------------------------------------
# 前処理
# ------------------------------------------------------------------------------
# ログ設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 環境変数の読み込み
api_key     = os.environ['api_key']
space_name  = os.environ['space_name']
project_key = os.environ['project_key']
dynamo_tbl  = os.environ['dynamo_tbl']

# DynamoDBの項目
column_fmt = {
  'No':              1,
  'issuetype_name':  'dummy',
  'category_names':  'dummy',
  'milestone_names': 'dummy',
  'summary':         'dummy',
  'description':     'dummy',
  'assignee_name':   'dummy',
  'start_day':       0,
  'start_dow_nth':   0,
  'start_dow_dow':   0,
  'due_day':         0,
  'due_dow_nth':     0,
  'due_dow_dow':     0
}

# ------------------------------------------------------------------------------
# 主処理
# ------------------------------------------------------------------------------
# DynamoDBに入れる予定のデータ
assignee_name   = 't-sasaki'
category_names  = 'vgj ,kfs'
milestone_names = '月次作業, AWS保守運用'
issuetype_name  = '月次'
summary         = 'test1'
description     = '''
test
テスト
|てすと|テスト|h
|1|2|
|3|4|
'''
start_day     = ''
start_dow_nth = '1'
start_dow_dow = 'sun'
due_day       = ''
due_dow_nth   = '3'
due_dow_dow   = 'mon'


logging.info('start')
def monthlywork(event, context):
    try:
        logging.info('lambda_handler start')
        logging.info('Event: {}'.format(json.dumps(event)))

        # BackLogクラス生成
        backlog = BackLog(space_name, project_key, api_key)
        # DynamoDBクラス作成
        dynamodb = DynamoDB(dynamo_tbl)
        
        #----- Step1
        logging.info('[Step1]DynamoDBにカラムを追加する')

        index_record = dynamodb.get_item('No', 1)
        logging.info('index_record: {}'.format(index_record))
        if index_record is None:
            logging.info('index_recordが存在しないためカラムを登録します')
            index_record = dynamodb.put_item(column_fmt)
            logging.info('index_record: {}'.format(index_record))
            logging.info('カラム登録が完了したため処理を終了します')
            return
        else:
            logging.info('index_recordが存在したため処理をスキップします')

        #----- Step2
        logging.info('[Step2]DynamoDBの全データを抽出します')
        records = dynamodb.scan_all()

        #----- Step3
        logging.info('[Step3]各レコード情報を元にバックログに起票します')
        for record in records:
            logging.info('record: {}'.format(record))

            # 日付情報の取得
            start_date = schedule.get_day_of_nth_dow(
                             int(record.get('start_day')),
                             int(record.get('start_dow_nth')),
                             int(record.get('start_dow_dow')),
                         )
            logging.info('start_date: {}'.format(start_date))

            due_date = schedule.get_day_of_nth_dow(
                             int(record.get('due_day')),
                             int(record.get('due_dow_nth')),
                             int(record.get('due_dow_dow')),
                         )
            logging.info('due_date: {}'.format(due_date))

            issuetype_id  = backlog.get_issuetype_id(record.get('issuetype_name'))
            assignee_id   = backlog.get_user_id(record.get('assignee_name'))
            category_ids  = [ backlog.get_category_id(i.strip())  for i in record.get('category_names').split(',')  if not record.get('category_names') == '']
            milestone_ids = [ backlog.get_milestone_id(i.strip()) for i in record.get('milestone_names').split(',') if not record.get('milestone_names') == '']
 
            # 課題登録API実行
            res = backlog.add_issue(
                      record.get('summary'),
                      issuetype_id,
                      record.get('description'),
                      start_date,
                      due_date, 
                      assignee_id,
                      category_ids,
                      milestone_ids,
                      []
            )

        logging.info('lambda_handler Normal end')
        return

    except Exception as error:
        logging.error(error)
        logging.info('lambda_handler Abnormal end')
        return