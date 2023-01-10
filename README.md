# e_api_event_receive.py
ｅ支店APIで、Event I/F を使い、約定や株価の変動等のプッシュ通知をリアルタイムに受信する。

ファイル名: e_api_event_receive.py


APIバージョン： v4r3で動作確認

ご注意！！ ================================

	本番環境に接続した場合、実際に注文等が出せます。
	市場で条件が一致して約定した場合、取り消せません。
	十分にご注意いただき、ご利用ください。

=========================================


1）動作テストを実行した環境は、os: Centos7.4、python: 3.6.8 です。

２）事前に立花証券ｅ支店に口座開設が必要です。

３）利用時に変数を設定してください。

	コードの開始部分の「利用時に変数を設定してください」のセクションで、
  
	変数、url_base、my_userid等を実際のurl、ご自身のユーザーID、パスワード等に変更してください。
  
	変更しない場合、APIを利用できません。


４)実行はコマンドプロンプト等からpython環境で起動してください。


５）実行内容は、以下になります。

	5-1）ログインして仮想URL（request, master, price, event）を取得します。

	5-2）Event I/F で、指定したプッシュ情報を受信します（約定、株価の変動等のプッシュ通知）。
  
  	5-3）指定時間経過後にログアウトを実行します。
	
	上記に付随して、送信データや受信データを適宜print()文で出力します。


６）取得した文字列に日本語が入った場合、文字コードはshift-jisです。

７）利用時間外に接続した場合、"p_errno":"9"（システム、サービス停止中。）が返されます。

	詳しくは「立花証券・ｅ支店・ＡＰＩ、EVENT I/F 利用方法、データ仕様」4ページをご参照ください。
  
	なおデモ環境のご利用時間はデモ環境の案内ページでください。
  
８）本サンプルプログラムは、事務方の者が休日や空き時間に作成したため、色々足りておりません。ご容赦ください。

９）本プログラムはライセンスの範囲内で自由にご使用ください。

１０）このソフトウェアを使用したことによって生じたすべての障害・損害・不具合等に関して、私と私の関係者および私の所属するいかなる団体・組織とも、一切の責任を負いません。各自の責任においてご使用ください。
