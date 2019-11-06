# ------------------------------------------------------------------------------
# モジュールのインポート
# ------------------------------------------------------------------------------
# 標準モジュール
import json
import urllib.request

# ------------------------------------------------------------------------------
# Class & Function
# ------------------------------------------------------------------------------
class BackLog:
    def __init__(self, space_name, project_key, api_key):
        self.space_name  = space_name
        self.project_key = project_key
        self.api_key     = api_key
        self.base_url    = 'https://' + self.space_name + '.backlog.jp/api/v2/{}'

        # インスタンス作成と同時にbacklogの各情報を取得
        self.projects   = self.__get_projects()
        self.project_id = self.__get_project_id()
        self.users      = self.__get_users()
        self.issuetypes = self.__get_issuetypes()
        self.categories = self.__get_categories()
        self.milestones = self.__get_milestones()

#----- プロジェクト関連
    def __get_projects(self):
        api    = 'projects'
        url    = self.base_url.format(api)
        params = {'apiKey': self.api_key}
    
        req = urllib.request.Request('{}?{}'.format(url, urllib.parse.urlencode(params)))
        res = urllib.request.urlopen(req).read().decode("utf-8")
        return json.loads(res)
    
    def __get_project_id(self):
        id = [i['id'] for i in self.projects if i['projectKey'] == self.project_key][0]
        return id

#----- ユーザー関連
    def __get_users(self):
        api    = 'projects/{}/users'.format(self.project_id)
        url    = self.base_url.format(api)
        params = {'apiKey': self.api_key}
    
        req = urllib.request.Request('{}?{}'.format(url, urllib.parse.urlencode(params)))
        res = urllib.request.urlopen(req).read().decode("utf-8")
        return json.loads(res)
    
    def get_user_id(self, mailaddress):
        id = [i['id'] for i in self.users if i['mailAddress'] == mailaddress][0]
        return id

#----- 種別関連
    def __get_issuetypes(self):
        api    = 'projects/{}/issueTypes'.format(self.project_id)
        url    = self.base_url.format(api)
        params = {'apiKey': self.api_key}
    
        req = urllib.request.Request('{}?{}'.format(url, urllib.parse.urlencode(params)))
        res = urllib.request.urlopen(req).read().decode("utf-8")
        return json.loads(res)
    
    def get_issuetype_id(self, issuetype_name):
        id = [i['id'] for i in self.issuetypes if i['name'] == issuetype_name][0]
        return id

#----- カテゴリー関連
    def __get_categories(self):
        api    = 'projects/{}/categories'.format(self.project_id)
        url    = self.base_url.format(api)
        params = {'apiKey': self.api_key}
    
        req = urllib.request.Request('{}?{}'.format(url, urllib.parse.urlencode(params)))
        res = urllib.request.urlopen(req).read().decode('utf-8')
        return json.loads(res)

    def create_category(self, category_name):
        api     = 'projects/{}/categories'.format(self.project_id)
        url     = self.base_url.format(api)
        params  = {'apiKey': self.api_key}
        headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
        data    = 'name={}'.format(category_name).encode("utf-8")
        method  = 'POST'
    
        req = urllib.request.Request('{}?{}'.format(url, urllib.parse.urlencode(params)),
                                             data=data,
                                             headers=headers,
                                             method=method
              )
        res = urllib.request.urlopen(req).read().decode('utf-8')
        return json.loads(res)
    
    def get_category_id(self, category_name):
        category_names_list = [i.get('name') for i in self.categories ]

        if category_name in category_names_list:
            id = [i['id'] for i in self.categories if i['name'] == category_name][0]
            return id
        else:
            return None

    def get_category_ids_list(self, category_names):
        ids_list = [ self.get_category_id(i.strip()) for i in category_names.split(',') if not category_names == '']
        return ids_list


#----- バージョン(マイルストーン)関連
    def __get_milestones(self):
        api    = 'projects/{}/versions'.format(self.project_id)
        url    = self.base_url.format(api)
        params = {'apiKey': self.api_key}

        req = urllib.request.Request('{}?{}'.format(url, urllib.parse.urlencode(params)))
        res = urllib.request.urlopen(req).read().decode("utf-8")
        return json.loads(res)

    def create_milestone(self, milestone_name):
        api     = 'projects/{}/versions'.format(self.project_id)
        url     = self.base_url.format(api)
        params  = {'apiKey': self.api_key}
        headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
        data    = 'name={}'.format(milestone_name).encode("utf-8")
        method  = 'POST'

        req = urllib.request.Request('{}?{}'.format(url, urllib.parse.urlencode(params)),
                                             data=data,
                                             headers=headers,
                                             method=method
              )
        res = urllib.request.urlopen(req).read().decode('utf-8')
        return json.loads(res)

    def get_milestone_id(self, milestone_name):
        milestone_names_list = [i.get('name') for i in self.milestones ]

        if milestone_name in milestone_names_list:
            id = [i['id'] for i in self.milestones if i['name'] == milestone_name][0]
            return id
        else:
            return None

    def get_milestone_ids_list(self, milestone_names):
        ids_list = [ self.get_milestone_id(i.strip()) for i in milestone_names.split(',') if not milestone_names == '']
        return ids_list


#----- 課題関連
    def add_issue(self, summary, issueTypeId, description, startDate, dueDate,
                  assigneeId, categoryIds,  milestoneIds, notifiedUserId):

        api = 'issues'
        url = self.base_url.format(api)

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        params  = {
            'apiKey'          : self.api_key,
            'projectId'       : self.project_id,
            'summary'         : summary,
            'description'     : description,
            'startDate'       : startDate,
            'dueDate'         : dueDate,
            'issueTypeId'     : issueTypeId,
            'priorityId'      : '3',
            'assigneeId'      : assigneeId,
        }

        # カテゴリーのリストを分解する
        params_category = {}
        for i, value in enumerate(categoryIds):
          params_category['categoryId[{}]'.format(i)] = value

        # マイルストーンのリストを分解する
        params_milestone = {}
        for i, value in enumerate(milestoneIds):
          params_category['milestoneId[{}]'.format(i)] = value

        # params辞書の連結
        params = {**params, **params_category, **params_milestone}
        print(params)

        params = urllib.parse.urlencode(params)
        req    = urllib.request.Request('{}?{}'.format(url, params), method="POST", headers=headers)
        print(req)
        res    = urllib.request.urlopen(req)
