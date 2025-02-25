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
- ユーザーネームは半角英数字2文字以上
- パスワードは半角英数字8文字以上

## 3. ホーム画面
![Image](https://github.com/user-attachments/assets/d8d480e1-0c16-4739-971a-8fb8f3f106a9)

## 4. 記録開始画面
![Image](https://github.com/user-attachments/assets/fe8204f2-4788-4a77-b437-d83ae5710e07)

![Image](https://github.com/user-attachments/assets/8069fe4c-775f-467f-8734-4eec465b4c6a)
- 名前は1文字以上
- 名前はドロップダウンで選ぶか、任意で設定
- 説明・メモは0～150字以内

## 5. 記録画面
![3a](https://github.com/user-attachments/assets/1dafdfd1-1977-4228-9b18-e9ab50c082ba)
![3b](https://github.com/user-attachments/assets/cf19dc33-5554-4dbd-8a0c-c468221e5c04)
- ターゲット部位を選択する
- 部位ごとに予め用意された王道種目を選択するか、任意の種目を設定する
- 回数・重量を入力して「追加」を押すと、1セット分が記録される



# Lisence

This project is licensed under the MIT License, see the LICENSE.txt file for details
