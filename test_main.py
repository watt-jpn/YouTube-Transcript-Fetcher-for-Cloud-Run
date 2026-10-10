# -------------------------------------------------------------------
# テストはvenvをアクティブにしてからCLIにて実行
#
# ユニットテストのみの実行コード: pytest -m "not integration"
#
# 結合テストのみの実行コード: pytest -s -m "integration"
#
# 全テストの一括実行コード: pytest -s
# -------------------------------------------------------------------

from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import pytest
from main import app

# FastAPI公式推奨のテストクライアント作成
client = TestClient(app)

# -------------------------------------------------------------------
# 1. ユニットテスト（モック使用：外部API通信なしで高速・安定動作）
# -------------------------------------------------------------------

@patch("main.get_best_transcript")
def test_fetch_transcript_success(mock_get_transcript):
    """正常系：字幕が正常に取得できた場合のテスト"""
    # モックの戻り値を設定
    mock_get_transcript.return_value = "これはテスト用の字幕テキストです"

    response = client.post("/transcript", json={"video_id": "dummy_video_id"})

    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "video_id": "dummy_video_id",
        "transcript": "これはテスト用の字幕テキストです",
    }
    mock_get_transcript.assert_called_once_with("dummy_video_id")


@patch("main.get_best_transcript")
def test_fetch_transcript_not_found(mock_get_transcript):
    """異常系：字幕が見つからず ValueError が発生した場合（404エラー）のテスト"""
    # モックで ValueError を発生させる
    mock_get_transcript.side_effect = ValueError(
        "動画ID 'dummy_video_id' に利用可能な字幕が見つかりませんでした。"
    )

    response = client.post("/transcript", json={"video_id": "dummy_video_id"})

    assert response.status_code == 404
    assert response.json() == {
        "detail": "動画ID 'dummy_video_id' に利用可能な字幕が見つかりませんでした。"
    }


# -------------------------------------------------------------------
# 2. 結合テスト（実API通信：実際のYouTube動画IDを使った動作確認）
# -------------------------------------------------------------------

@pytest.mark.integration
def test_fetch_transcript_real_video():
    """実環境結合テスト：実際のYouTube動画IDを使用して字幕取得とクレンジングを確認"""
    real_video_id = "ktdbUIZKeSE"
    response = client.post("/transcript", json={"video_id": real_video_id})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["video_id"] == real_video_id
    assert isinstance(data["transcript"], str)
    assert len(data["transcript"]) > 0

    # 取得・クレンジング済みの字幕テキストを出力（先頭300文字および全容）
    print("\n" + "=" * 50)
    print("【実環境テスト：取得・整形完了テキスト（先頭300文字）】")
    print(data["transcript"][:300] + "...")
    print("=" * 50)