# YouTube Transcript API

YouTube動画の字幕を取得・整形するAPIである。

当初はGoogle Cloud Runへのデプロイを前提として開発したが、クラウド環境からの字幕取得がIPアドレスによる制限を受けることが判明したため、現在はローカル環境での実行を前提とする方針に変更している。

本リポジトリは、当初の開発成果と技術的な検証履歴を保存し、後継プロジェクトで再利用するためのレガシーリポジトリである。

## 1. 概要と開発背景

### 開発目的

当初、Google Apps Script（以下、GAS）をメインとしてYouTube動画の要約アプリを開発していた。その際、字幕取得処理にPythonライブラリである`youtube-transcript-api`を利用するため、GASから呼び出すバックエンドAPIとして本プログラムを開発した。

本プログラムは、YouTube動画のURLを受け取り、字幕を取得・整形して返すAPIとして設計した。

### 技術構成

| 技術 | 用途 |
|---|---|
| Python 3.12 | アプリケーション実装 |
| FastAPI | APIサーバー |
| Pydantic | リクエストデータの検証 |
| youtube-transcript-api | YouTube字幕の取得 |
| Uvicorn | ASGIサーバー |
| Docker | 実行環境の構築 |
| pytest | テスト |

## 2. 実装機能

### 字幕取得

`POST /transcript`エンドポイントにYouTube動画のURLを渡すことで、対象動画の字幕を取得する。

字幕の選択には以下の優先順位を設定している。

1. 手動生成字幕の日本語
2. 手動生成字幕の英語
3. その他の手動生成字幕
4. 自動生成字幕の日本語
5. 自動生成字幕の英語

上記の条件に該当する字幕が存在しない場合は、エラーを返す。

### テキスト整形

取得した字幕に対して、以下の処理を実施する。

- Unicode NFKC正規化
- 角括弧・丸括弧内の文字列の削除
- 日本語の句読点等の削除
- 空白文字の整理

### API仕様

エンドポイント：

```http
POST /transcript
```

リクエスト例：

```json
{
  "video_id": "https://www.youtube.com/watch?v=XXXXXXXXXXX"
}
```

正常時のレスポンス例：

```json
{
  "status": "success",
  "video_id": "https://www.youtube.com/watch?v=XXXXXXXXXXX",
  "transcript": "取得した字幕テキスト"
}
```

## 3. 実行方法

### ローカル環境

依存パッケージをインストールする。

```bash
pip install -r requirements.txt
```

APIサーバーを起動する。

```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

### Docker

Dockerイメージをビルドする。

```bash
docker build -t youtube-transcript-api .
```

コンテナを起動する。

```bash
docker run -p 8080:8080 youtube-transcript-api
```

## 4. テスト

pytestを使用してテストを実施する。

ユニットテスト（結合テストを除く）：

```bash
pytest -m "not integration"
```

YouTube APIとの結合テスト：

```bash
pytest -s -m "integration"
```

結合テストでは実際のYouTube動画にアクセスして字幕取得を検証する。そのため、実行環境やYouTube側の制限によって失敗する可能性がある。

## 5. 技術的制約と方針転換

### Cloud Runへのデプロイ

当初はGoogle Cloud Runに本プログラムをデプロイし、GASからAPIを呼び出す構成を想定していた。

Cloud RunへのデプロイおよびAPIサーバーの起動は正常に動作する。しかし、YouTube字幕の取得処理を実行すると、IPアドレスがYouTube側の制限を受け、字幕を取得できないことが判明した。

### 方針転換

以上の検証結果を踏まえ、クラウド環境からの字幕取得を断念し、PCのローカル環境で手動実行する方式へ方針を変更した。

本リポジトリは、Cloud Runへのデプロイを想定して構築したアプリケーションと、その検証過程を保存する目的で維持する。

なお、ここでの結論は本プロジェクトで検証した環境に基づくものであり、すべてのクラウド環境で字幕取得が不可能であることを示すものではない。

## 6. 開発過程で得られた資産

本プロジェクトでは、以下の成果を得た。

- 初めてのDocker環境構築
- Dockerfileの作成と実行環境の検証
- YouTube字幕取得ライブラリの利用・検証
- Cloud Runへのデプロイ

また、Docker環境の構築過程で得られた知見を、以下の技術記事にまとめた。

- [Google Cloud RunにおけるDockerfile CMD命令形式の考察](https://zenn.dev/watt_dev/articles/8ff89938bcec24)

## 7. 今後の利用方針

本リポジトリは、後継プロジェクトの開発における参考資産として維持する。

後継プロジェクトでは、本リポジトリをForkし、既存の字幕取得処理などを必要に応じて再利用する方針である。

Fork後の開発・変更は後継プロジェクト側で行い、本リポジトリ自体では新規機能の開発を行わない。