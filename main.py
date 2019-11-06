# ------------------------------------------------------------------------------
# モジュールのインポート
# ------------------------------------------------------------------------------
# 標準モジュール
import os
import json
import logging

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
  'mailaddress':     'dummy',
  'start_day':       0,
  'start_dow_nth':   0,
  'start_dow_dow':   'dummy',
  'due_day':         0,
  'due_dow_nth':     0,
  'due_dow_dow':     'dummy'
}

# ------------------------------------------------------------------------------
# 主処理
# ------------------------------------------------------------------------------
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
                             str(record.get('start_dow_dow')),
                         )
            logging.info('start_date: {}'.format(start_date))

            due_date = schedule.get_day_of_nth_dow(
                             int(record.get('due_day')),
                             int(record.get('due_dow_nth')),
                             str(record.get('due_dow_dow')),
                         )
            logging.info('due_date: {}'.format(due_date))

            # ----- Issuetype
            issuetype_name = record.get('issuetype_name')
            issuetype_id  = backlog.get_issuetype_id(issuetype_name)
            logging.info('The {0} IssuetypeID: {1}.'.format(issuetype_name, issuetype_id))

            # ----- Assignee 
            mailaddress = record.get('mailaddress')
            assignee_id = backlog.get_user_id(mailaddress)
            logging.info('The {0} AssigneeId: {1}'.format(mailaddress, assignee_id))

            # ----- Category(複数指定が可能なのでちょっと面倒)
            # 引っ張ってきたデータをカンマ区切りで配列に詰め、それぞれの要素に対して先頭末尾の空白を削除
            category_names =  list(map(str.strip, record.get('category_names').split(',')))

            # カテゴリIDリストの作成
            category_ids = []
            for category_name in category_names:
                category_id = backlog.get_category_id(category_name)
                logging.info('The {0} CategoryID: {1}.'.format(category_name, category_id))
                #指定されたカテゴリが無ければ作成する
                if category_id is None:
                  logging.info('a new category create because The specified category do not define.')
                  res = backlog.create_category(category_name)
                  logging.info('create category result: {}'.format(res))
                  category_id = res.get('id')
                  logging.info('The {0} CategoryID: {1}.'.format(category_name, category_id))
                category_ids.append(category_id)
            logging.info('category_ids: {}.'.format(category_ids))

            # ----- MileStone(複数指定が可能なのでちょっと面倒)
            # 引っ張ってきたデータをカンマ区切りで配列に詰め、それぞれの要素に対して先頭末尾の空白を削除
            milestone_names =  list(map(str.strip, record.get('milestone_names').split(',')))

            # マイルストンIDリストの作成
            milestone_ids = []
            for milestone_name in milestone_names:
                milestone_id = backlog.get_milestone_id(milestone_name)
                logging.info('The {0} milestoneID: {1}.'.format(milestone_name, milestone_id))
                #指定されたマイルストンが無ければ作成する
                if milestone_id is None:
                  logging.info('a new milestone create because The specified milestone do not define.')
                  res = backlog.create_milestone(milestone_name)
                  logging.info('create milestone result: {}'.format(res))
                  milestone_id = res.get('id')
                  logging.info('The {0} milestoneID: {1}.'.format(milestone_name, milestone_id))
                milestone_ids.append(milestone_id)
            logging.info('milestone_ids: {}.'.format(milestone_ids))
 
            # 課題登録API実行
            logging.info('Execute the issue registration API.')
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
            logging.info('Execute the issue registration API Result: {}'.format(res))

        logging.info('lambda_handler Normal end')
        return 'lambda_handler Normal end'

    except Exception as error:
        logging.info('lambda_handler Abnormal end')
        logging.error(error)
        raise error
