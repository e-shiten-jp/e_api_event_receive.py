# -*- coding: utf-8 -*-

# Copyright (c) 2022 Tachibana Securities Co., Ltd. All rights reserved.
# 2022.04.12, yo.

# 2021.07.08,   yo.
# 2023.04.11 reviced, yo.
# 2025.08.09 reviced, yo.
# 2026.02.18 reviced, yo.
#
# 立花証券ｅ支店ＡＰＩ利用のサンプルコード
#
# 動作確認
# Python 3.11.2 / debian12
# API v4r7
#
# 機能: プッシュ送信される時価の取得
#
#
# 必要な設定項目
# 行番号: my_p_gyou_no  （1-120の整数）
# 銘柄コード: my_sIssueCode （通常銘柄は4桁、優先株等は5桁。例、伊藤園'2593'、伊藤園優先株'25935'）
# 市場: my_sSizyouC （00:東証   現在(2021/07/01)、東証のみ可能。）
# 稼働時間: my_work_minutes
#
# 
# 1銘柄で取得の場合のサンプル
## my_p_gyou_no = '1'        # 行を指定する。string型。1-120の整数で、銘柄毎に違う行を指定する。時価取得時の銘柄の識別番号。
## my_sIssueCode = '1234'  # 2.銘柄コード。string型。通常銘柄、4桁。優先株等、5桁。例、伊藤園'2593'、伊藤園優先株'25935'
## my_sSizyouC = '00'      # 3.市場。string型。  00:東証   現在(2021/07/01)、東証のみ可能。
#
# 2銘柄で取得の場合のサンプル
##my_p_gyou_no = '1,2'        # 行を指定する。string型。1-120の整数で、銘柄毎に違う行を指定する。時価取得時の銘柄の識別番号。
##my_sIssueCode = '1301,1332'  # 2.銘柄コード。通常銘柄、4桁。優先株等、5桁。例、伊藤園'2593'、伊藤園優先株'25935'
##my_sSizyouC = '00,00'      # 3.市場。  00:東証   現在(2021/07/01)、東証のみ可能。
#
# 3銘柄で取得の場合のサンプル
##my_p_gyou_no = '1,2,3'        # 行を指定する。string型。1-120の整数で、銘柄毎に違う行を指定する。時価取得時の銘柄の識別番号。
##my_sIssueCode = '1301,1332,1333'  # 2.銘柄コード。通常銘柄、4桁。優先株等、5桁。例、伊藤園'2593'、伊藤園優先株'25935'
##my_sSizyouC = '00,00,00'      # 3.市場。  00:東証   現在(2021/07/01)、東証のみ可能。
#
#
#
# 利用方法: 
# 事前に「e_api_login_tel.py」を実行して、
# 仮想URL（1日券）等を取得しておいてください。
# 「e_api_login_tel.py」と同じディレクトリで実行してください。
# 停止は、ctrl+Cを押してください。
#
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
#
# == ご注意: ========================================
#   本番環境にに接続した場合、実際に市場に注文が出ます。
#   市場で約定した場合取り消せません。
# ==================================================
#

import urllib3
import datetime
import json
import time


#--- 共通コード ------------------------------------------------------

# request項目を保存するクラス。配列として使う。
class class_req :
    def __init__(self) :
        self.str_key = ''
        self.str_value = ''
        
    def add_data(self, work_key, work_value) :
        self.str_key = func_check_json_dquat(work_key)
        self.str_value = func_check_json_dquat(work_value)


# 口座属性クラス
class class_def_account_property:
    def __init__(self):
        self.sUserId = ''           # userid
        self.sPassword = ''         # password
        self.sSecondPassword = ''   # 第2パスワード
        self.sUrl = ''              # 接続先URL
        self.sJsonOfmt = 5          # 返り値の表示形式指定
        
# ログイン属性クラス
class class_def_login_property:
    def __init__(self):
        self.p_no = 0                       # 累積p_no
        self.sJsonOfmt = ''                 # 返り値の表示形式指定
        self.sResultCode = ''               # 結果コード
        self.sResultText = ''               # 結果テキスト
        self.sZyoutoekiKazeiC = ''          # 譲渡益課税区分  1：特定  3：一般  5：NISA
        self.sSecondPasswordOmit = ''       # 暗証番号省略有無Ｃ  22.第二パスワード  APIでは第2暗証番号を省略できない。 関連資料:「立花証券・e支店・API、インターフェース概要」の「3-2.ログイン、ログアウト」参照
        self.sLastLoginDate = ''            # 最終ログイン日時
        self.sSogoKouzaKubun = ''           # 総合口座開設区分  0：未開設  1：開設
        self.sHogoAdukariKouzaKubun = ''    # 保護預り口座開設区分  0：未開設  1：開設
        self.sFurikaeKouzaKubun = ''        # 振替決済口座開設区分  0：未開設  1：開設
        self.sGaikokuKouzaKubun = ''        # 外国口座開設区分  0：未開設  1：開設
        self.sMRFKouzaKubun = ''            # ＭＲＦ口座開設区分  0：未開設  1：開設
        self.sTokuteiKouzaKubunGenbutu = '' # 特定口座区分現物  0：一般  1：特定源泉徴収なし  2：特定源泉徴収あり
        self.sTokuteiKouzaKubunSinyou = ''  # 特定口座区分信用  0：一般  1：特定源泉徴収なし  2：特定源泉徴収あり
        self.sTokuteiKouzaKubunTousin = ''  # 特定口座区分投信  0：一般  1：特定源泉徴収なし  2：特定源泉徴収あり
        self.sTokuteiHaitouKouzaKubun = ''  # 配当特定口座区分  0：未開設  1：開設
        self.sTokuteiKanriKouzaKubun = ''   # 特定管理口座開設区分  0：未開設  1：開設
        self.sSinyouKouzaKubun = ''         # 信用取引口座開設区分  0：未開設  1：開設
        self.sSakopKouzaKubun = ''          # 先物ＯＰ口座開設区分  0：未開設  1：開設
        self.sMMFKouzaKubun = ''            # ＭＭＦ口座開設区分  0：未開設  1：開設
        self.sTyukokufKouzaKubun = ''       # 中国Ｆ口座開設区分  0：未開設  1：開設
        self.sKawaseKouzaKubun = ''         # 為替保証金口座開設区分  0：未開設  1：開設
        self.sHikazeiKouzaKubun = ''        # 非課税口座開設区分  0：未開設  1：開設  ※ＮＩＳＡ口座の開設有無を示す。
        self.sKinsyouhouMidokuFlg = ''      # 金商法交付書面未読フラグ  1：未読（標準Ｗｅｂを起動し書面確認実行必須）  0：既読  ※未読の場合、ｅ支店・ＡＰＩは利用不可のため    仮想ＵＲＬは発行されず""を設定。  ※既読の場合、ｅ支店・ＡＰＩは利用可能となり    仮想ＵＲＬを発行し設定。  
        self.sUrlRequest = ''               # 仮想URL（REQUEST)  業務機能    （REQUEST I/F）仮想URL
        self.sUrlMaster = ''                # 仮想URL（MASTER)  マスタ機能  （REQUEST I/F）仮想URL
        self.sUrlPrice = ''                 # 仮想URL（PRICE)  時価情報機能（REQUEST I/F）仮想URL
        self.sUrlEvent = ''                 # 仮想URL（EVENT)  注文約定通知（EVENT I/F）仮想URL
        self.sUrlEventWebSocket = ''        # 仮想URL（EVENT-WebSocket)  注文約定通知（EVENT I/F WebSocket版）仮想URL
        self.sUpdateInformWebDocument = ''  # 交付書面更新予定日  標準Ｗｅｂの交付書面更新予定日決定後、該当日付を設定。  【注意】参照
        self.sUpdateInformAPISpecFunction = ''  # ｅ支店・ＡＰＩリリース予定日  ｅ支店・ＡＰＩリリース予定日決定後、該当日付を設定。  【注意】参照

        

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


# 機能： ファイルから文字情報を読み込み、その文字列を返す。
# 戻り値： 文字列
# 第１引数： ファイル名
# 備考： json形式のファイルを想定。
def func_read_from_file(str_fname):
    str_read = ''
    try:
        with open(str_fname, 'r', encoding = 'utf_8') as fin:
            while True:
                line = fin.readline()
                if not len(line):
                    break
                str_read = str_read + line
        return str_read
    except IOError as e:
        print('ファイルを読み込めません!!! ファイル名：',str_fname)
        print(type(e))


# 機能: ファイルに書き込む
# 引数1: 出力ファイル名
# 引数2: 出力するデータ
# 備考:
def func_write_to_file(str_fname_output, str_data):
    try:
        with open(str_fname_output, 'w', encoding = 'utf-8') as fout:
            fout.write(str_data)
    except IOError as e:
        print('ファイルに書き込めません!!!  ファイル名：',str_fname_output)
        print(type(e))


# 機能: class_req型データをjson形式の文字列に変換する。
# 返値: json形式の文字
# 第１引数： class_req型データ
def func_make_json_format(work_class_req):
    work_key = ''
    work_value = ''
    str_json_data =  '{\n\t'
    for i in range(len(work_class_req)) :
        work_key = func_strip_dquot(work_class_req[i].str_key)
        if len(work_key) > 0:
            if work_key[:1] == 'a' :
                work_value = work_class_req[i].str_value
                str_json_data = str_json_data + work_class_req[i].str_key \
                                    + ':' + func_strip_dquot(work_value) \
                                    + ',\n\t'
            else :
                work_value = func_check_json_dquat(work_class_req[i].str_value)
                str_json_data = str_json_data + func_check_json_dquat(work_class_req[i].str_key) \
                                    + ':' + work_value \
                                    + ',\n\t'
    str_json_data = str_json_data[:-3] + '\n}'
    return str_json_data


# 機能： API問合せ文字列を作成し返す。
# 戻り値： api問合せのurl文字列
# 第１引数： ログインは、Trueをセット。それ以外はFalseをセット。
# 第2引数： ログインは、APIのurlをセット。それ以外はログインで返された仮想url（'sUrlRequest'等）の値をセット。
# 第３引数： 要求項目のデータセット。クラスの配列として受取る。
def func_make_url_request(auth_flg, \
                          url_target, \
                          work_class_req) :
    str_url = url_target
    if auth_flg == True :   # ログインの場合
        str_url = str_url + 'auth/'
    str_url = str_url + '?'
    str_url = str_url + func_make_json_format(work_class_req)
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


# 機能： アカウント情報をファイルから取得する
# 引数1: 口座情報を保存したファイル名
# 引数2: 口座情報（class_def_account_property型）データ
def func_get_acconut_info(fname, class_account_property):
    str_account_info = func_read_from_file(fname)
    # JSON形式の文字列を辞書型で取り出す
    json_account_info = json.loads(str_account_info)

    class_account_property.sUserId = json_account_info.get('sUserId')
    class_account_property.sPassword = json_account_info.get('sPassword')
    class_account_property.sSecondPassword = json_account_info.get('sSecondPassword')
    class_account_property.sUrl = json_account_info.get('sUrl')

    # 返り値の表示形式指定
    class_account_property.sJsonOfmt = json_account_info.get('sJsonOfmt')
    # "5"は "1"（1ビット目ON）と”4”（3ビット目ON）の指定となり
    # ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定


# 機能： ログイン情報をファイルから取得する
# 引数1: ログイン情報を保存したファイル名（fname_login_response = "e_api_login_response.txt"）
# 引数2: ログインデータ型（class_def_login_property型）
def func_get_login_info(str_fname, class_login_property):
    str_login_respons = func_read_from_file(str_fname)
    dic_login_respons = json.loads(str_login_respons)

    class_login_property.sResultCode = dic_login_respons.get('sResultCode')                 # 結果コード
    class_login_property.sResultText = dic_login_respons.get('sResultText')                 # 結果テキスト
    class_login_property.sZyoutoekiKazeiC = dic_login_respons.get('sZyoutoekiKazeiC')       # 譲渡益課税区分  1：特定  3：一般  5：NISA
    class_login_property.sSecondPasswordOmit = dic_login_respons.get('sSecondPasswordOmit')     # 暗証番号省略有無Ｃ
    class_login_property.sLastLoginDate = dic_login_respons.get('sLastLoginDate')               # 最終ログイン日時
    class_login_property.sSogoKouzaKubun = dic_login_respons.get('sSogoKouzaKubun')             # 総合口座開設区分  0：未開設  1：開設
    class_login_property.sHogoAdukariKouzaKubun = dic_login_respons.get('sHogoAdukariKouzaKubun')       # 保護預り口座開設区分  0：未開設  1：開設
    class_login_property.sFurikaeKouzaKubun = dic_login_respons.get('sFurikaeKouzaKubun')               # 振替決済口座開設区分  0：未開設  1：開設
    class_login_property.sGaikokuKouzaKubun = dic_login_respons.get('sGaikokuKouzaKubun')               # 外国口座開設区分  0：未開設  1：開設
    class_login_property.sMRFKouzaKubun = dic_login_respons.get('sMRFKouzaKubun')                       # ＭＲＦ口座開設区分  0：未開設  1：開設
    class_login_property.sTokuteiKouzaKubunGenbutu = dic_login_respons.get('sTokuteiKouzaKubunGenbutu') # 特定口座区分現物  0：一般  1：特定源泉徴収なし  2：特定源泉徴収あり
    class_login_property.sTokuteiKouzaKubunSinyou = dic_login_respons.get('sTokuteiKouzaKubunSinyou')   # 特定口座区分信用  0：一般  1：特定源泉徴収なし  2：特定源泉徴収あり
    class_login_property.sTokuteiKouzaKubunTousin = dic_login_respons.get('sTokuteiKouzaKubunTousin')   # 特定口座区分投信  0：一般  1：特定源泉徴収なし  2：特定源泉徴収あり
    class_login_property.sTokuteiHaitouKouzaKubun = dic_login_respons.get('sTokuteiHaitouKouzaKubun')   # 配当特定口座区分  0：未開設  1：開設
    class_login_property.sTokuteiKanriKouzaKubun = dic_login_respons.get('sTokuteiKanriKouzaKubun')     # 特定管理口座開設区分  0：未開設  1：開設
    class_login_property.sSinyouKouzaKubun = dic_login_respons.get('sSinyouKouzaKubun')         # 信用取引口座開設区分  0：未開設  1：開設
    class_login_property.sSinyouKouzaKubun = dic_login_respons.get('sSinyouKouzaKubun')         # 信用取引口座開設区分  0：未開設  1：開設
    class_login_property.sSakopKouzaKubun = dic_login_respons.get('sSakopKouzaKubun')           # 先物ＯＰ口座開設区分  0：未開設  1：開設
    class_login_property.sMMFKouzaKubun = dic_login_respons.get('sMMFKouzaKubun')               # ＭＭＦ口座開設区分  0：未開設  1：開設
    class_login_property.sTyukokufKouzaKubun = dic_login_respons.get('sTyukokufKouzaKubun')     # 中国Ｆ口座開設区分  0：未開設  1：開設
    class_login_property.sKawaseKouzaKubun = dic_login_respons.get('sKawaseKouzaKubun')         # 為替保証金口座開設区分  0：未開設  1：開設
    class_login_property.sHikazeiKouzaKubun = dic_login_respons.get('sHikazeiKouzaKubun')       # 非課税口座開設区分  0：未開設  1：開設  ※ＮＩＳＡ口座の開設有無を示す。
    class_login_property.sKinsyouhouMidokuFlg = dic_login_respons.get('sKinsyouhouMidokuFlg')   # 金商法交付書面未読フラグ  1：未読（標準Ｗｅｂを起動し書面確認実行必須）  0：既読  ※未読の場合、ｅ支店・ＡＰＩは利用不可のため    仮想ＵＲＬは発行されず""を設定。  ※既読の場合、ｅ支店・ＡＰＩは利用可能となり    仮想ＵＲＬを発行し設定。  
    class_login_property.sUrlRequest = dic_login_respons.get('sUrlRequest')     # 仮想URL（REQUEST)  業務機能    （REQUEST I/F）仮想URL
    class_login_property.sUrlMaster = dic_login_respons.get('sUrlMaster')       # 仮想URL（MASTER)  マスタ機能  （REQUEST I/F）仮想URL
    class_login_property.sUrlPrice = dic_login_respons.get('sUrlPrice')         # 仮想URL（PRICE)  時価情報機能（REQUEST I/F）仮想URL
    class_login_property.sUrlEvent = dic_login_respons.get('sUrlEvent')         # 仮想URL（EVENT)  注文約定通知（EVENT I/F）仮想URL
    class_login_property.sUrlEventWebSocket = dic_login_respons.get('sUrlEventWebSocket')    # 仮想URL（EVENT-WebSocket)  注文約定通知（EVENT I/F WebSocket版）仮想URL
    class_login_property.sUpdateInformWebDocument = dic_login_respons.get('sUpdateInformWebDocument')    # 交付書面更新予定日  標準Ｗｅｂの交付書面更新予定日決定後、該当日付を設定。  【注意】参照
    class_login_property.sUpdateInformAPISpecFunction = dic_login_respons.get('sUpdateInformAPISpecFunction')    # ｅ支店・ＡＰＩリリース予定日  ｅ支店・ＡＰＩリリース予定日決定後、該当日付を設定。  【注意】参照
    

# 機能： p_noをファイルから取得する
# 引数1: p_noを保存したファイル名（fname_info_p_no = "e_api_info_p_no.txt"）
# 引数2: login情報（class_def_login_property型）データ
def func_get_p_no(fname, class_login_property):
    str_p_no_info = func_read_from_file(fname)
    # JSON形式の文字列を辞書型で取り出す
    json_p_no_info = json.loads(str_p_no_info)
    class_login_property.p_no = int(json_p_no_info.get('p_no'))
        
    
# 機能: p_noを保存するためのjson形式のテキストデータを作成します。
# 引数1: p_noを保存するファイル名（fname_info_p_no = "e_api_info_p_no.txt"）
# 引数2: 保存するp_no
# 備考:
def func_save_p_no(str_fname_output, int_p_no):
    # "p_no"を保存する。
    str_info_p_no = '{\n'
    str_info_p_no = str_info_p_no + '\t' + '"p_no":"' + str(int_p_no) + '"\n'
    str_info_p_no = str_info_p_no + '}\n'
    func_write_to_file(str_fname_output, str_info_p_no)
    print('現在の"p_no"を保存しました。 p_no =', int_p_no)            
    print('ファイル名:', str_fname_output)

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


# 機能： 受信データを区切り文字で分割し辞書型で返す。
# 引数1：str_url string
# 返値： 辞書型データ
# 備考:
# 受信データは、
#       websocket: string型
#       event: byte型
 
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
# 例、b'p_1_DPP^B3757' の場合、「p_1_DPP」は、p:プレーン文字列、_1:行番号、_DPP:現在値
#
def func_punctuate_message(chunk):
    dict_message = {}
    str_message = ''
    flg_p_date = False      # 取得した情報がp_dateの場合、Trueに設定し時刻を取得する。
    flg_end = False         # p_dateが指定時間を超えたら、Trueに設定し終了する。
    
    chunk_ctrl = ""         # 元電文で制御コードとなっている区切子^A,^B,^Cを文字列"^A","^B","^C"に置き換えた電文を格納する。

    for i in range(len(chunk)):
        if chunk[i:i+1] != '\x01' and chunk[i:i+1] != '\n' :
            # 項目と値の区切り'^B'が来た場合、':'に置き換え（置き換え文字は任意）。
            if chunk[i:i+1] == '\x02' :
                str_key = str_message
                str_message = ''
                chunk_ctrl = chunk_ctrl + '^B'
            # 値区切り文字'^C'が来た場合、','に置き換え（置き換え文字は任意）。
            elif chunk[i:i+1] == '\x03' :
                str_message = str_message + ','
                chunk_ctrl = chunk_ctrl + '^C'
            else :                        
                str_message = str_message + chunk[i:i+1]
                chunk_ctrl = chunk_ctrl + chunk[i:i+1]

        # 項目区切り'^A'と改行が来た場合
        else:   # if chunk[i:i+1] == '\x01' or chunk[i:i+1] == '\n' :
            dict_message[str_key] = str_message
            str_message = ''
            if chunk[i:i+1] == '\x01' :
                chunk_ctrl = chunk_ctrl + '^A'
            if chunk[i:i+1] == '\n' :
                chunk_ctrl = chunk_ctrl + '\n'
    
    print("受信電文　区切子^A^B^Cは非表示：")
    print(chunk)
    print('区切子^A^B^Cを文字列"^A","^B","^C"に置換：')
    print(chunk_ctrl)
    return dict_message


# 機能： event用のurlを作成する。
# 引数1：行番号 string
# 引数2：銘柄コード string
# 引数3：市場 string
# 引数4: class_login_property（口座属性クラス）
# 返値： url string
# 備考: NS（ニュース）は重いため注意が必要。
def func_make_event_url(str_p_gyou_no, str_sIssueCode, str_sSizyouC, class_login_property):
    str_url = ''
    str_url = str_url + class_login_property.sUrlEvent
    str_url = str_url + '?'
#    str_url = str_url + 'p_evt_cmd=ST,KP,FD'
    str_url = str_url + 'p_evt_cmd=ST,KP,EC,SS,US,FD'
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
# 例、b'p_1_DPP^B3757' の場合、「p_1_DPP」は、p:プレーン文字列、_1:行番号、_DPP:現在値
#
def func_event_receive(str_url):
    byte_text = b''
    flg_p_date = False      # 取得した情報がp_dateの場合、Trueに設定し時刻を取得する。
    flg_end = False         # p_dateが指定時間を超えたら、Trueに設定し終了する。

    # APIに接続
    http = urllib3.PoolManager()

    # ストリーム形式で接続（** 重要 **）
    resp = http.request(
        'GET',
        str_url,
        preload_content=False)
    
    for byte_chunk in resp.stream(2048):
        str_chunk = byte_chunk.decode()
        print()
        print('---------------')
        dict_my_message = func_punctuate_message(str_chunk)
        
        for key, value in dict_my_message.items():
            print(key, ': ', value)
            if key == 'p_errno' and value == '2' :
                print()
                print(key, ': ', value)
                print("仮想URLが有効ではありません。")
                print("電話認証 + e_api_login_tel.py実行")
                print("を再度行い、新しく仮想URL（1日券）を取得してください。")
                print()
    
    resp.release_conn()



    
# ======================================================================================================
# ==== プログラム始点 =================================================================================
# ======================================================================================================
# 必要な設定項目
# 行番号: my_p_gyou_no  （1-120の整数）
# 銘柄コード: my_sIssueCode （通常銘柄は4桁、優先株等は5桁。例、伊藤園'2593'、伊藤園優先株'25935'）
# 市場: my_sSizyouC （00:東証   現在(2021/07/01)、東証のみ可能。）


if __name__ == "__main__":

    # --- 利用時に変数を設定してください -------------------------------------------------------
    # コマンド用パラメーター -------------------    
    # 仕様では120銘柄まで指定できますが、負荷が高くなるため、サンプルコードでは1 - 3銘柄を用意。

    # 1銘柄で取得の場合のサンプル
    #my_p_gyou_no = '1'        # 行を指定する。string型。1-120の整数で、銘柄毎に違う行を指定する。時価取得時の銘柄の識別番号。
    #my_sIssueCode = '1234'  # 2.銘柄コード。string型。通常銘柄、4桁。優先株等、5桁。例、伊藤園'2593'、伊藤園優先株'25935'
    #my_sSizyouC = '00'      # 3.市場。string型。  00:東証   現在(2021/07/01)、東証のみ可能。
 
    # 2銘柄で取得の場合のサンプル
    my_p_gyou_no = '1,2'        # 行を指定する。string型。1-120の整数で、銘柄毎に違う行を指定する。時価取得時の銘柄の識別番号。
    my_sIssueCode = '6501,9432'  # 2.銘柄コード。通常銘柄、4桁。優先株等、5桁。例、伊藤園'2593'、伊藤園優先株'25935'
    my_sSizyouC = '00,00'      # 3.市場。  00:東証   現在(2021/07/01)、東証のみ可能。

    # 3銘柄で取得の場合のサンプル
    ##my_p_gyou_no = '1,2,3'        # 行を指定する。string型。1-120の整数で、銘柄毎に違う行を指定する。時価取得時の銘柄の識別番号。
    ##my_sIssueCode = '1301,1332,1333'  # 2.銘柄コード。通常銘柄、4桁。優先株等、5桁。例、伊藤園'2593'、伊藤園優先株'25935'
    ##my_sSizyouC = '00,00,00'      # 3.市場。  00:東証   現在(2021/07/01)、東証のみ可能。

    # --- 以上設定項目 -------------------------------------------------------------------------


    # --- ファイル名等を設定（実行ファイルと同じディレクトリ） ---------------------------------------
    fname_account_info = "./e_api_account_info.txt"
    fname_login_response = "./e_api_login_response.txt"
    fname_info_p_no = "./e_api_info_p_no.txt"
    # --- 以上ファイル名設定 -------------------------------------------------------------------------

    my_account_property = class_def_account_property()
    my_login_property = class_def_login_property()
    
    # 口座情報をファイルから読み込む。
    func_get_acconut_info(fname_account_info, my_account_property)
    
    # ログイン応答を保存した「e_api_login_response.txt」から、仮想URLと課税flgを取得
    func_get_login_info(fname_login_response, my_login_property)

    my_login_property.sJsonOfmt = my_account_property.sJsonOfmt                   # 返り値の表示形式指定
    my_login_property.sSecondPassword = func_replace_urlecnode(my_account_property.sSecondPassword)        # 22.第二パスワード  APIでは第2暗証番号を省略できない。 関連資料:「立花証券・e支店・API、インターフェース概要」の「3-2.ログイン、ログアウト」参照
    
    # 現在（前回利用した）のp_noをファイルから取得する
    func_get_p_no(fname_info_p_no, my_login_property)
    my_login_property.p_no = my_login_property.p_no + 1
    # "p_no"を保存する。
    func_save_p_no(fname_info_p_no, my_login_property.p_no)

    print()
    print('-- event 受信 -------------------------------------------------------------')
    # event用urlの作成
    my_url = func_make_event_url(my_p_gyou_no, my_sIssueCode, my_sSizyouC, my_login_property)
    
    # eventでのプッシュ情報の受信
    try:
        func_event_receive(my_url)
    except	KeyboardInterrupt:
        print	("info, Ctrl^C interrupt.")
    except	Exception as p_exception:
        print   (f'error, exception catched:[{p_exception}]')
