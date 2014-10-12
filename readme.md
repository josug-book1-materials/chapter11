# Chapter11
## playbooks/book1
- プレイブック内で定義済みの品目(web,app,dbs)の中から目的にあわせた仮想マシンを作成します。
- 品目は -e オプションの後にtargetとして指定します。
- webサーバ作成時にはneutronからfloating_ipアドレスを新規に割り当てます。

```
[前提条件]
1. sample_openrcを自身の環境にしてsourceコマンドで反映させてください
2. ansible-playbookコマンド実行時にはカレントディレクトリをplaybooksに変更してください

[書式]
ansible-playbook -i sample_app_inventory.py -e target=web|app|dbs book1/create_sample_vm.yml
```

## playbooks/book2
データベースサーバグループ(dbs)に所属するサーバ上で稼働しているsample-app用のデータベースをバックアップします。
プレイブックは４つに分かれており、それぞれ以下のような役割をもっています。
  
1. create_snapshot.yml - LVMを利用したスナップショットを作成します。   
1. backup_snapshot.yml - スナップショット上のデータベースファイルをアーカイブしてバックアップします。  
1. restart_rest_service.yml - appサーバ上のrestサービスをリスタートします。  
1. db_backup.yml - 他の３つのプレイブックをインクルードして順に実行するプレイブック本体です。  

```
[前提条件]
1. sample_openrcを自身の環境にしてsourceコマンドで反映させてください
2. ansible-playbookコマンド実行時にはカレントディレクトリをplaybooksに変更してください

[書式]
ansible-playbook -i sample_app_inventory.py -t snapshot,backup book2/db_backup.yml
```
