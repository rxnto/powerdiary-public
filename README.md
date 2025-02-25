# 📌 PowerDiary
このプロジェクトは、日常のトレーニングの記録を実現するWebアプリです。

## 🛠 使用技術
- **フロントエンド:** HTML, CSS, JavaScript
- **バックエンド:** Python (Django)
- **データベース:** SQLite
- **デプロイ:** PythonAnywhere

## 🚀 インストール方法
- このリポジトリをクローンする:
```sh
   git clone https://github.com/rxnto/powerdiary-public.git
```
- 仮想環境を構築&仮想環境に入る（Windows）
```sh
   python -m venv venv
   source venv/Scripts/activate
```
- 仮想環境を構築&仮想環境に入る（Mac）
```sh
   python -m venv venv
   source venv/bin/activate
```
- 必要なパッケージをインストール:
```sh
   pip install -r requirements.txt
```

- ローカルで実行する
```sh
   python manage.ppy runserver
```

## 1. ログイン画面
![Image](https://github.com/user-attachments/assets/8f235ef8-efce-406e-835f-10e593dbe81a)

## 2. 新規登録画面
![Image](https://github.com/user-attachments/assets/80975a7a-580f-4c16-bf01-d855ec8a9d3b)
- ユーザーネームは半角英数字2文字以上。
- パスワードは半角英数字8文字以上。

## 3. ホーム画面
![Image](https://github.com/user-attachments/assets/d8d480e1-0c16-4739-971a-8fb8f3f106a9)

## 4. 記録開始画面
![Image](https://github.com/user-attachments/assets/fe8204f2-4788-4a77-b437-d83ae5710e07)

![Image](https://github.com/user-attachments/assets/8069fe4c-775f-467f-8734-4eec465b4c6a)
- 名前は1文字以上。
- 名前はドロップダウンで選ぶか、任意で設定。
- 説明・メモは0～150字以内。

## 5. 記録画面
![3a](https://github.com/user-attachments/assets/1dafdfd1-1977-4228-9b18-e9ab50c082ba)
![3b](https://github.com/user-attachments/assets/cf19dc33-5554-4dbd-8a0c-c468221e5c04)
- ターゲット部位を選択する
- 部位ごとに予め用意された王道種目を選択するか、任意の種目を設定する。
- 回数・重量を入力して「追加」を押すと、1セット分が記録される。
![3c](https://github.com/user-attachments/assets/ea1fa50c-747c-4ba3-850d-408c5bb99984)
- 追加を押すと、図のようになり、動作を確認したい場合は、YouTubeアイコンをクリックすると、種目名の検索結果のYouTubeページに遷移。
- コピーボタンを押すと、繰り返し行った種目をコピーできる。
- ×ボタンは削除。

## 6. 記録一覧表
![4](https://github.com/user-attachments/assets/1b385196-99d6-4b40-bd05-fe9846fb2f46)

## 7. 模型
![5](https://github.com/user-attachments/assets/d1a35994-b6fc-4fba-a2b4-826ff74077ee)
![5a](https://github.com/user-attachments/assets/176365fe-121f-441c-a2a4-289bccc0b72f)
- 鍛えた部位に色がつき、一目でどこを鍛えているか、トレーニング状況がわかるようになっている。
- 各回数10回で色の濃さが最大になる。（図は胸筋が10回、腹筋が5回）
- 2D解剖モデル部分をクリックすると、前面・背面それぞれの拡大図が表示される。

## 8. 履歴
![6](https://github.com/user-attachments/assets/61ba8078-3f7f-4dcc-b3b2-3c1cbe59a26e)
- 履歴には、月が替わったタイミングで、更新され今月分のトレーニング内容が保存される。
- 月が替わったタイミングで、今月分の記録はリセット。

## 9. タンパク質摂取量計算
![7](https://github.com/user-attachments/assets/bd4cba2f-1c66-42ff-a073-c5a0a6bfe5df)
![7a](https://github.com/user-attachments/assets/b6c180fa-85e0-4216-bf6b-4e8a1ed22600)
- その日に接種したタンパク質が、筋肥大に効果的かを判定。
- 体重×2.0～gの場合は緑色の顔文字
- 体重×1.4～1.9gの場合は水色の顔文字
- 体重×1.3～1.0gの場合は黄色の顔文字
- 体重×1.0g未満の場合は赤色の顔文字

## 10. グッズ紹介
![8](https://github.com/user-attachments/assets/c65eeda5-7136-402f-b50d-5f203d63ceae)
- どのようなグッズを買えばいいかわからない初心者のアドバイス的機能。

# 11. チャットAI
![9](https://github.com/user-attachments/assets/7275abe0-1127-4dc3-a1d8-fb0450d9ade3)
- AzureOpenAIのAPIの期限が切れているので現在使用できません。

# Lisence

This project is licensed under the MIT License, see the LICENSE.txt file for details
