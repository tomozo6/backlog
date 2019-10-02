# ------------------------------------------------------------------------------
# モジュールのインポート
# ------------------------------------------------------------------------------
#----- サードパーティー製モジュール
import boto3
from boto3.dynamodb.conditions import Key, Attr

# ------------------------------------------------------------------------------
# クラス&関数
# ------------------------------------------------------------------------------
class DynamoDB:
    def __init__(self, tbl):
        self.dynamodb = boto3.resource('dynamodb')
        self.tbl      = self.dynamodb.Table(tbl)

    def scan_all(self):
        table = self.tbl
        res = table.scan(
            ConsistentRead=True,
        )
        return res.get('Items')

    def put_item(self, item):
        table = self.tbl
        res = table.put_item(Item=item)
        return res

    def get_item(self, key, value):
        table = self.tbl
        res = table.get_item(
            Key={
                key : value
            },
            ConsistentRead=True
            )
        return res.get('Item')
