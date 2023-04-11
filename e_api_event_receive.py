# -*- coding: utf-8 -*-

# Copyright (c) 2022 Tachibana Securities Co., Ltd. All rights reserved.
# 2022.04.12, yo.

# 2021.07.08,   yo.
# 2023.04.11 reviced,   yo.
# Python 3.6.8 / centos7.4
# API v4r3 で動作確認
# 立花証券ｅ支店ＡＰＩ利用のサンプルコード
# 機能: ログイン、プッシュ送信される時価の取得、ログアウト を行ないます。
#
# 利用方法: コード後半にある「プログラム始点」以下の設定項目を自身の設定に変更してご利用ください。
#
# 参考資料（必ず最新の資料を参照してください。）--------------------------
# マニュアル
# Eventの資料は、API専用ページ
# ５．マニュアル、
# １．共通説明
# （５）注文約定通知（仮想ＵＲＬ（EVENT））
# 別紙「立花証券・ｅ支店・ＡＰＩ、EVENT I/F 利用方法、データ仕様」参照。
# (api_event_if.xlsx)
#
# == ご注意: ========================================
#   本番環境にに接続した場合、実際に市場に注文を出せます。
#   市場で約定した場合取り消せません。
# ==================================================
#

import urllib3
import datetime
import json
import time


#--- 共通コード ------------------------------------------------------

# request項目を保存するクラス。配列として使う。
# 'p_no'、'p_sd_date'は格納せず、func_make_url_requestで生成する。
class class_req :
    def __init__(self) :
        self.str_key = ''
        self.str_value = ''
        
    def add_data(self, work_key, work_value) :
        self.str_key = work_key
        self.str_value = work_value


# 口座属性クラス
class class_def_cust_property:
    def __init__(self):
        self.sUrlRequest = ''       # request用仮想URL
        self.sUrlMaster = ''        # master用仮想URL
        self.sUrlPrice = ''         # price用仮想URL
        self.sUrlEvent = ''         # event用仮想URL
        self.sZyoutoekiKazeiC = ''  # 8.譲渡益課税区分    1：特定  3：一般  5：NISA     ログインの返信データで設定済み。 
        self.sSecondPassword = ''   # 22.第二パスワード  APIでは第２暗証番号を省略できない。 関連資料:「立花証券・e支店・API、インターフェース概要」の「3-2.ログイン、ログアウト」参照
        self.sJsonOfmt = ''         # 返り値の表示形式指定
        


# 機能: システム時刻を"p_sd_date"の書式の文字列で返す。
# 返値: "p_sd_date"の書式の文字列
# 引数1: システム時刻
# 備考:  "p_sd_date"の書式：YYYY.MM.DD-hh:mm:ss.sss
def func_p_sd_date(int_systime):
    str_psddate = ''
    str_psddate = str_psddate + str(int_systime.year) 
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.month))[-2:]
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.day))[-2:]
    str_psddate = str_psddate + '-' + ('00' + str(int_systime.hour))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.minute))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.second))[-2:]
    str_psddate = str_psddate + '.' + (('000000' + str(int_systime.microsecond))[-6:])[:3]
    return str_psddate


# JSONの値の前後にダブルクオーテーションが無い場合付ける。
def func_check_json_dquat(str_value) :
    if len(str_value) == 0 :
        str_value = '""'
        
    if not str_value[:1] == '"' :
        str_value = '"' + str_value
        
    if not str_value[-1:] == '"' :
        str_value = str_value + '"'
        
    return str_value
    
    
# 受けたテキストの１文字目と最終文字の「"」を削除
# 引数：string
# 返り値：string
def func_strip_dquot(text):
    if len(text) > 0:
        if text[0:1] == '"' :
            text = text[1:]
            
    if len(text) > 0:
        if text[-1] == '\n':
            text = text[0:-1]
        
    if len(text) > 0:
        if text[-1:] == '"':
            text = text[0:-1]
        
    return text
    


# 機能: URLエンコード文字の変換
# 引数1: 文字列
# 返値: URLエンコード文字に変換した文字列
# 
# URLに「#」「+」「/」「:」「=」などの記号を利用した場合エラーとなる場合がある。
# APIへの入力文字列（特にパスワードで記号を利用している場合）で注意が必要。
#   '#' →   '%23'
#   '+' →   '%2B'
#   '/' →   '%2F'
#   ':' →   '%3A'
#   '=' →   '%3D'
def func_replace_urlecnode( str_input ):
    str_encode = ''
    str_replace = ''
    
    for i in range(len(str_input)):
        str_char = str_input[i:i+1]

        if str_char == ' ' :
            str_replace = '%20'       #「 」 → 「%20」 半角空白
        elif str_char == '!' :
            str_replace = '%21'       #「!」 → 「%21」
        elif str_char == '"' :
            str_replace = '%22'       #「"」 → 「%22」
        elif str_char == '#' :
            str_replace = '%23'       #「#」 → 「%23」
        elif str_char == '$' :
            str_replace = '%24'       #「$」 → 「%24」
        elif str_char == '%' :
            str_replace = '%25'       #「%」 → 「%25」
        elif str_char == '&' :
            str_replace = '%26'       #「&」 → 「%26」
        elif str_char == "'" :
            str_replace = '%27'       #「'」 → 「%27」
        elif str_char == '(' :
            str_replace = '%28'       #「(」 → 「%28」
        elif str_char == ')' :
            str_replace = '%29'       #「)」 → 「%29」
        elif str_char == '*' :
            str_replace = '%2A'       #「*」 → 「%2A」
        elif str_char == '+' :
            str_replace = '%2B'       #「+」 → 「%2B」
        elif str_char == ',' :
            str_replace = '%2C'       #「,」 → 「%2C」
        elif str_char == '/' :
            str_replace = '%2F'       #「/」 → 「%2F」
        elif str_char == ':' :
            str_replace = '%3A'       #「:」 → 「%3A」
        elif str_char == ';' :
            str_replace = '%3B'       #「;」 → 「%3B」
        elif str_char == '<' :
            str_replace = '%3C'       #「<」 → 「%3C」
        elif str_char == '=' :
            str_replace = '%3D'       #「=」 → 「%3D」
        elif str_char == '>' :
            str_replace = '%3E'       #「>」 → 「%3E」
        elif str_char == '?' :
            str_replace = '%3F'       #「?」 → 「%3F」
        elif str_char == '@' :
            str_replace = '%40'       #「@」 → 「%40」
        elif str_char == '[' :
            str_replace = '%5B'       #「[」 → 「%5B」
        elif str_char == ']' :
            str_replace = '%5D'       #「]」 → 「%5D」
        elif str_char == '^' :
            str_replace = '%5E'       #「^」 → 「%5E」
        elif str_char == '`' :
            str_replace = '%60'       #「`」 → 「%60」
        elif str_char == '{' :
            str_replace = '%7B'       #「{」 → 「%7B」
        elif str_char == '|' :
            str_replace = '%7C'       #「|」 → 「%7C」
        elif str_char == '}' :
            str_replace = '%7D'       #「}」 → 「%7D」
        elif str_char == '~' :
            str_replace = '%7E'       #「~」 → 「%7E」
        else :
            str_replace = str_char

        str_encode = str_encode + str_replace
        
    return str_encode



# 機能： API問合せ文字列を作成し返す。
# 戻り値： url文字列
# 第１引数： ログインは、Trueをセット。それ以外はFalseをセット。
# 第２引数： ログインは、APIのurlをセット。それ以外はログインで返された仮想url（'sUrlRequest'等）の値をセット。
# 第３引数： 要求項目のデータセット。クラスの配列として受取る。
def func_make_url_request(auth_flg, \
                          url_target, \
                          work_class_req) :
    work_key = ''
    work_value = ''

    str_url = url_target
    if auth_flg == True :
        str_url = str_url + 'auth/'
    
    str_url = str_url + '?{\n\t'
    
    for i in range(len(work_class_req)) :
        work_key = func_strip_dquot(work_class_req[i].str_key)
        if len(work_key) > 0:
            if work_key[:1] == 'a' :
                work_value = work_class_req[i].str_value
            else :
                work_value = func_check_json_dquat(work_class_req[i].str_value)

            str_url = str_url + func_check_json_dquat(work_class_req[i].str_key) \
                                + ':' + work_value \
                                + ',\n\t'
               
        
    str_url = str_url[:-3] + '\n}'
    return str_url



# 機能: API問合せ。通常のrequest,price用。
# 返値: API応答（辞書型）
# 第１引数： URL文字列。
# 備考: APIに接続し、requestの文字列を送信し、応答データを辞書型で返す。
#       master取得は専用の func_api_req_muster を利用する。
def func_api_req(str_url): 
    print('送信文字列＝')
    print(str_url)  # 送信する文字列

    # APIに接続
    http = urllib3.PoolManager()
    req = http.request('GET', str_url)
    print("req.status= ", req.status )

    # 取得したデータを、json.loadsを利用できるようにstr型に変換する。日本語はshift-jis。
    bytes_reqdata = req.data
    str_shiftjis = bytes_reqdata.decode("shift-jis", errors="ignore")

    print('返信文字列＝')
    print(str_shiftjis)

    # JSON形式の文字列を辞書型で取り出す
    json_req = json.loads(str_shiftjis)

    return json_req



# ログイン関数
# 引数1: p_noカウンター
# 引数2: アクセスするurl（'auth/'以下は付けない）
# 引数3: ユーザーID
# 引数4: パスワード
# 引数5: 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_login(int_p_no, my_url, str_userid, str_passwd, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p2/46 No.1 引数名:CLMAuthLoginRequest を参照してください。
    
    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sCLMID"'
    str_value = 'CLMAuthLoginRequest'
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sUserId"'
    str_value = str_userid
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    str_key = '"sPassword"'
    str_value = str_passwd
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_cust_property.sJsonOfmt    # "5"は "1"（1ビット目ＯＮ）と”4”（3ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # ログインとログイン後の電文が違うため、第１引数で指示。
    # ログインはTrue。それ以外はFalse。
    # このプログラムでの仕様。APIの仕様ではない。
    # URL文字列の作成
    str_url = func_make_url_request(True, \
                                     my_url, \
                                     req_item)
    # API問合せ
    json_return = func_api_req(str_url)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p2/46 No.2 引数名:CLMAuthLoginAck を参照してください。

    int_p_errno = int(json_return.get('p_errno'))    # p_erronは、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、利用方法、データ仕様」を参照ください。
    if not json_return.get('sResultCode') == None :
        int_sResultCode = int(json_return.get('sResultCode'))
    else :
        int_sResultCode = -1
    # sResultCodeは、マニュアル
    # 「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、注文入力機能引数項目仕様」
    # (api_request_if_order_vOrO.pdf)
    # の p13/42 「6.メッセージ一覧」を参照ください。
    #
    # 時間外の場合 'sResultCode' が返らないので注意
    # 参考例
    # {
    #         "p_no":"1",
    #         "p_sd_date":"2022.11.25-08:28:04.609",
    #         "p_rv_date":"2022.11.25-08:28:04.598",
    #         "p_errno":"-62",
    #         "p_err":"システム、情報提供時間外。",
    #         "sCLMID":"CLMAuthLoginRequest"
    # }




    if int_p_errno ==  0 and int_sResultCode == 0:    # ログインエラーでない場合
        # ---------------------------------------------
        # ログインでの注意点
        # 契約締結前書面が未読の場合、
        # 「int_p_errno = 0 And int_sResultCode = 0」で、
        # sUrlRequest=""、sUrlEvent="" が返されログインできない。
        # ---------------------------------------------
        if len(json_return.get('sUrlRequest')) > 0 :
            # 口座属性クラスに取得した値をセット
            class_cust_property.sZyoutoekiKazeiC = json_return.get('sZyoutoekiKazeiC')
            class_cust_property.sUrlRequest = json_return.get('sUrlRequest')        # request用仮想URL
            class_cust_property.sUrlMaster = json_return.get('sUrlMaster')          # master用仮想URL
            class_cust_property.sUrlPrice = json_return.get('sUrlPrice')            # price用仮想URL
            class_cust_property.sUrlEvent = json_return.get('sUrlEvent')            # event用仮想URL
            bool_login = True
        else :
            print('契約締結前書面が未読です。')
            print('ブラウザーで標準Webにログインして確認してください。')
    else :  # ログインに問題があった場合
        print('p_errno:', json_return.get('p_errno'))
        print('p_err:', json_return.get('p_err'))
        print('sResultCode:', json_return.get('sResultCode'))
        print('sResultText:', json_return.get('sResultText'))
        print()
        bool_login = False

    return bool_login


# ログアウト
# 引数1: p_noカウンター
# 引数2: class_cust_property（request通番）, 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_logout(int_p_no, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/46 No.3 引数名:CLMAuthLogoutRequest を参照してください。
    
    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sCLMID"'
    str_value = 'CLMAuthLogoutRequest'  # logoutを指示。
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_cust_property.sJsonOfmt    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # ログインとログイン後の電文が違うため、第１引数で指示。
    # ログインはTrue。それ以外はFalse。
    # このプログラムでの仕様。APIの仕様ではない。
    # URL文字列の作成
    str_url = func_make_url_request(False, \
                                     class_cust_property.sUrlRequest, \
                                     req_item)
    # API問合せ
    json_return = func_api_req(str_url)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/46 No.4 引数名:CLMAuthLogoutAck を参照してください。

    int_sResultCode = int(json_return.get('sResultCode'))    # p_erronは、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、利用方法、データ仕様」を参照ください。
    if int_sResultCode ==  0 :    # ログアウトエラーでない場合
        bool_logout = True
    else :  # ログアウトに問題があった場合
        bool_logout = False

    return bool_logout

#--- 以上 共通コード -------------------------------------------------





# Event
# 資料は、API専用ページ
# ５．マニュアル、
# １．共通説明
# （５）注文約定通知（仮想ＵＲＬ（EVENT））
# 別紙「立花証券・ｅ支店・ＡＰＩ、EVENT I/F 利用方法、データ仕様」参照。
# (api_event_if.xlsx)
#
# 問合せの例
# 2. 利用方法 p2/26
#「
# 仮想URL                     ※e支店・APIでの利用時の例。
# ?p_rid=0                      ※3.(3)【株価ボード・アプリケーション機能毎引数設定値表】参照。
# &p_board_no=1000              ※3.(3)【株価ボード・アプリケーション機能毎引数設定値表】参照。
# [&p_gyou_no=N[,N]]            ※必要時のみ設定。
# [&p_issue_code=NNNN[,NNNN]]   ※必要時のみ設定。
# [&p_mkt_code=NN[,NN]]         ※必要時のみ設定。
# &p_eno=0  ※1
# &p_evt_cmd=ST,KP,EC,SS,US ※2
# 」
#
# eventで時価情報(FD)を取得する場合、アプリケーション機能のNo2を利用する。
# 3. 通知データ仕様
# (3)FD     p5/26
# 【株価ボード・アプリケーション機能毎引数設定値表】
# No: 2
# 株価ボード・アプリケーション: e支店・API、時価配信機能あり
# p_rid: 22
# p_board_no: 1000
# p_gyou_no: 1-120
# p_issue_code: 銘柄コード[120]
# p_mkt_code: 市場コード[120]
#
# ----------------------
# 注意点:
# EVENTの場合、送信のURL内に'\n'や'\t'を入れないこと。
# 余計な制御文字を入れるとエラーになる。
# ----------------------

# p_evt_cmdは、以下の値をカンマ区切りで列挙する。
# p3/26
#No 値 説明                        備考
# 1 ST エラーステータス情報配信指定   発生時通知
# 2 KP キープアライブ情報配信指定    発生時通知(5秒間通知未送信時通知)
# 3 FD 時価情報配信指定             初回はメモリ内スナップショット(全データ)、以降は変化分のみ通知
# 4 EC 注文約定通知イベント配信指定   初回は当日営業日内の通知削除機能で削除していない全通知を接続毎に再送、以降は発生時通知
# 5 NS ニュース通知イベント配信指定   初回は当日営業日内の通知削除機能で削除していない全通知を接続毎に再送、以降は発生時通知
# 6 RR 画面リフレッシュ通知配信指定   現時点で不使用
# 7 SS システムステータス配信指定    初回は当日営業日内の通知削除機能で削除していない全通知を接続毎に再送、以降は発生時通知
# 8 US 運用ステータス配信指定      初回は当日営業日内の通知削除機能で削除していない全通知を接続毎に再送、以降は発生時通知




# 機能： event用のurlを作成する。
# 引数1：行番号 string
# 引数2：銘柄コード string
# 引数3：市場 string
# 引数4: class_cust_property（口座属性クラス）
# 返値： url string
# 備考: NS（ニュース）は重いため注意が必要。
def func_make_event_url(str_p_gyou_no, str_sIssueCode, str_sSizyouC, class_cust_property):
    str_url = ''
    str_url = str_url + class_cust_property.sUrlEvent
    str_url = str_url + '?'
    str_url = str_url + 'p_evt_cmd=ST,KP,FD'
##    str_url = str_url + 'p_evt_cmd=ST,KP,EC,SS,US,FD'
    str_url = str_url + '&' + 'p_eno=0'     # 配信開始したいイベント通知番号(ユニーク番号)、指定番号の次から送信する(0なら全て)。
    str_url = str_url + '&' + 'p_rid=22'    # 固定値
    str_url = str_url + '&' + 'p_board_no=1000'    # 固定値
    str_url = str_url + '&' + 'p_gyou_no=' + str_p_gyou_no      # 行番号。1-120で指定。
    str_url = str_url + '&' + 'p_issue_code=' + str_sIssueCode  # 銘柄コード
    str_url = str_url + '&' + 'p_mkt_code=' + str_sSizyouC      # 市場

    print('print(str_url):')
    print(str_url)
    return str_url
    


# 機能： event用のhttpアクセスを行い、プッシュされた情報を標準出力に出力する。
# 引数1：str_url string
# 引数2：int_work_minutes 数値型。動作を終了する分数を指定。
# 返値： 無し
# 備考:
# 仕様の解説は、API専用ページ
# ５．マニュアル、
# １．共通説明
# （５）注文約定通知（仮想ＵＲＬ（EVENT））
# 別紙「立花証券・ｅ支店・ＡＰＩ、EVENT I/F 利用方法、データ仕様」参照。
# (api_event_if.xlsx)
# 3. 通知データ仕様 p4/26
# 通知データは「^A」「^B」「^C」を区切り子とし文字列の羅列で送信する。
# 通知データ中の値として「^A^B^C」は使わない。
# 項目A1=値B1;項目A2=値B21,B22,B23;・・・を送信する場合、
# 項目A1^B値B1^A項目A2^B値B21^CB22^CB23^A・・・と送信する。
# ※区切り子「^A」は1項目値、「^B」は項目と値、「^C」は値と値の各区切り。
#
# 「型_行番号_情報コード」で、情報コードで示す値を設定する。
# 例、b'p_1_DPP^B3757' の場合、「p_1_DPP」は、p:プレーン文字列_1:行番号_DPP:現在値
#
def func_event_receive(str_url, int_work_minutes):

    byte_text = b''
    flg_p_date = False      # 取得した情報がp_dateの場合、Trueに設定し時刻を取得する。
    flg_end = False         # p_dateが指定時間を超えたら、Trueに設定し終了する。
    time_start = datetime.datetime.now()    # 開始時刻計測
    time_end = time_start + datetime.timedelta(minutes= int_work_minutes )  # 'minutes=10'を変更すれば時間を変更できる。
    

    # APIに接続
    http = urllib3.PoolManager()

    # ストリーム形式で接続（** 重要 **）
    resp = http.request(
        'GET',
        str_url,
        preload_content=False)
    
    for chunk in resp.stream(1024):
        for i in range(len(chunk)):
            # 項目区切り'^A'と改行が来た場合
            if chunk[i:i+1] == b'\x01' or chunk[i:i+1] == b'\n' :
                print(byte_text)

                # 停止判定
                if flg_p_date == True :
                    str_p_date = str(byte_text[7:], 'shift-jis')       # b'p_date:2022.12.20-11:20:34.200'
                    time_now = datetime.datetime.strptime(str_p_date, '%Y.%m.%d-%H:%M:%S.%f')
                    # print('経過時間:', time_now - time_start)
                    flg_p_date = False
                    # 停止時間経過で停止フラグをTrueに変更。
                    if time_now > time_end :
                        flg_end = True
                    
                byte_text = b''
            else :
                # 項目と値の区切り'^B'が来た場合、':'に置き換え（置き換え文字は任意）。
                if chunk[i:i+1] == b'\x02' :
                    byte_text = byte_text + b':'
                    if byte_text == b'p_date:' :
                        flg_p_date = True
                    
                # 値区切り文字'^C'が来た場合、','に置き換え（置き換え文字は任意）。
                elif chunk[i:i+1] == b'\x03' :
                    byte_text = byte_text + b','
                else :                        
                    byte_text = byte_text + chunk[i:i+1]
        if flg_end == True :
            print(str(int_work_minutes) + '分経過で終了')
            break

    resp.release_conn()









    
# ======================================================================================================
# ==== プログラム始点 =================================================================================
# ======================================================================================================

# 必要な設定項目
# 接続先:  my_url 
# ユーザーID:   my_userid 
# パスワード:    my_passwd （ログイン時に使うパスワード）
# 第2パスワード: my_2pwd （発注時に使うパスワード）
# 行番号: my_p_gyou_no  （1-120の整数）
# 銘柄コード: my_sIssueCode （通常銘柄は4桁、優先株等は5桁。例、伊藤園'2593'、伊藤園優先株'25935'）
# 市場: my_sSizyouC （00:東証   現在(2021/07/01)、東証のみ可能。）
# 稼働時間: my_work_minutes

# --- 利用時に変数を設定してください -------------------------------------------------------

# 接続先 設定 --------------
# デモ環境（新バージョンになった場合、適宜変更）
my_url = 'https://demo-kabuka.e-shiten.jp/e_api_v4r3/'

# 本番環境（新バージョンになった場合、適宜変更）
# ＊＊！！実際に市場に注文を出せるので注意！！＊＊
# my_url = 'https://kabuka.e-shiten.jp/e_api_v4r3/'

# ＩＤパスワード設定 ---------
my_userid = 'MY_USERID' # 自分のuseridに書き換える
my_passwd = 'MY_PASSWD' # 自分のpasswordに書き換える
my_2pwd = 'MY_2PASSWD'  # 自分の第２passwordに書き換える


# コマンド用パラメーター -------------------    
# 仕様では120銘柄まで指定できますが、負荷が高くなるため、サンプルコードでは1銘柄のみを指定。

# 1銘柄で取得
my_p_gyou_no = '1'        # 行を指定する。string型。1-120の整数で、銘柄毎に違う行を指定する。時価取得時の銘柄の識別番号。
my_sIssueCode = '1234'  # 2.銘柄コード。string型。通常銘柄、4桁。優先株等、5桁。例、伊藤園'2593'、伊藤園優先株'25935'
my_sSizyouC = '00'      # 3.市場。string型。  00:東証   現在(2021/07/01)、東証のみ可能。

# 2銘柄で取得
##my_p_gyou_no = '1,2'        # 行を指定する。string型。1-120の整数で、銘柄毎に違う行を指定する。時価取得時の銘柄の識別番号。
##my_sIssueCode = '1301,1332'  # 2.銘柄コード。通常銘柄、4桁。優先株等、5桁。例、伊藤園'2593'、伊藤園優先株'25935'
##my_sSizyouC = '00,00'      # 3.市場。  00:東証   現在(2021/07/01)、東証のみ可能。

# 3銘柄で取得
##my_p_gyou_no = '1,2,3'        # 行を指定する。string型。1-120の整数で、銘柄毎に違う行を指定する。時価取得時の銘柄の識別番号。
##my_sIssueCode = '1301,1332,1333'  # 2.銘柄コード。通常銘柄、4桁。優先株等、5桁。例、伊藤園'2593'、伊藤園優先株'25935'
##my_sSizyouC = '00,00,00'      # 3.市場。  00:東証   現在(2021/07/01)、東証のみ可能。

my_work_minutes = 2     # 時価を取得する時間を分単位で指定。 


# --- 以上設定項目 -------------------------------------------------------------------------


class_cust_property = class_def_cust_property()     # 口座属性クラス

# ID、パスワード、第２パスワードのURLエンコードをチェックして変換
my_userid = func_replace_urlecnode(my_userid)
my_passwd = func_replace_urlecnode(my_passwd)
class_cust_property.sSecondPassword = func_replace_urlecnode(my_2pwd)

# 返り値の表示形式指定
class_cust_property.sJsonOfmt = '5'
# "5"は "1"（1ビット目ＯＮ）と”4”（3ビット目ＯＮ）の指定となり
# ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定

print('-- login -----------------------------------------------------')
# 送信項目、戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
# p2/46 No.1 引数名:CLMAuthLoginRequest を参照してください。
int_p_no = 1
# ログイン処理
bool_login = func_login(int_p_no, my_url, my_userid, my_passwd,  class_cust_property)

# ログインOKの場合
if bool_login :
    
    print()
    print('-- event 受信 -------------------------------------------------------------')
    # event用urlの作成
    my_url = func_make_event_url(my_p_gyou_no, my_sIssueCode, my_sSizyouC, class_cust_property)
    
    # eventでのプッシュ情報の受信
    func_event_receive(my_url, my_work_minutes)
    
    print()
    print('-- logout -------------------------------------------------------------')
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/46 No.3 引数名:CLMAuthLogoutRequest を参照してください。
    int_p_no = int_p_no + 1
    bool_logout = func_logout(int_p_no, class_cust_property)
   
else :
    print('ログインに失敗しました')
