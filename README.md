# ap-control

AirStation WSR-A2533DHP3 の設定変更ページを操作するスクリプト

## 要件

- slackをUIとする
- slackでbotを指定して add/del ホスト名 を指定すると，システムが airstation の設定画面を操作し，設定変更後，ログアウトする
- システムはホスト名とMacアドレスの対応表を持つ
- システムはホストの登録状況を確認しエラーを起こさないよう指示を実行する

## ユースケース図

![](out/figure/usecase.png)

## シーケンス図

削除シーケンス
![](out/figure/del_func.png)

追加シーケンス
![](out/figure/add_func.png)

## フローチャート

del_func
![](out/figure/del_proc.png)