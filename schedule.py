# ------------------------------------------------------------------------------
# モジュールのインポート
# ------------------------------------------------------------------------------
# 標準モジュール
import calendar
import datetime

# ------------------------------------------------------------------------------
# Class & Function
# ------------------------------------------------------------------------------
# [第x曜日モード]      dayの値が入っていない場合、nthとdowより日付を算出してyyyy-MM-ddのfmtにして返す
# [日付指定モード処理] dayの値が入っている場合、単純にyyyy-MM-ddのfmtにして返す
def get_day_of_nth_dow(day, nth, dow):
    print('day: {}'.format(day))
    print('nth: {}'.format(nth))
    print('dow: {}'.format(dow))
    # 曜日の数値コード変換テーブル
    dow_table = {
        'mon' : 0,
        'tue' : 1,
        'wed' : 2,
        'thu' : 3,
        'fri' : 4,
        'sat' : 5,
        'sun' : 6,
    }
    # 本日の情報を取得
    today   = datetime.datetime.today()
    toyear  = int(today.strftime("%Y"))
    tomonth = int(today.strftime("%m"))

    if day == 0: # [第x曜日モード]
        if nth > 0 and dow > 0:
            nth = int(nth)               # nthを数値型に変換
            dow = int(dow_table[dow])    # dowを数値コードに変換

            if nth < 1 or dow < 0 or dow > 6:
                return None

            first_dow, n = calendar.monthrange(toyear, tomonth)
            day = 7 * (nth - 1) + (dow - first_dow) % 7 + 1
            res = datetime.date(toyear, tomonth, day)
            return res

        else:
            return None
    else: # [日付指定モード処理]
        day = int(day) # dayを数値型に変換
        res = datetime.date(toyear, tomonth, day)
        return res
