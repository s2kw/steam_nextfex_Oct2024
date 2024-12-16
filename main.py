from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# ChromeDriverの自動ダウンロード設定
chrome_service = Service(ChromeDriverManager().install())
chrome_options = Options()
chrome_options.add_argument('--headless')  # ヘッドレスモード（必要に応じて解除）
chrome_options.add_argument('--start-maximized')

# WebDriverの初期化
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# 対象URL
url = "https://store.steampowered.com/sale/nextfestmostplayed_oct_2024"

# データ収集用リストとセット（重複防止用）
data = []

# 収集済みのアプリIDを保存するセット
seen_app_ids = set()

try:
    # SteamのNext Festページを開く
    driver.get(url)
    time.sleep(10)  # ページロードのための待機

    # 各ゲーム情報を取得
    game_items = driver.find_elements(By.CSS_SELECTOR, "div.Panel.Focusable")  # 各ゲーム全体の要素を選択

    for item in game_items:
        # 初期化（失敗時のデフォルト値）
        title = "No Title"
        game_url = "No URL"
        app_id = "No ID"
        price = "No Price"
        overall_reviews = "No Reviews"
        review_count = "0"
        tags_list = "No Tags"

        try:
            # URL取得
            url_element = item.find_element(By.CSS_SELECTOR, "a")
            game_url = url_element.get_attribute("href")
            app_id = game_url.split("/")[4].split("?")[0]  # クエリ文字列を除外

            # 収集済みならスキップ
            if app_id in seen_app_ids:
                continue
            seen_app_ids.add(app_id)  # 新しいアプリIDを記録

            # タイトル取得
            title = item.find_element(By.CSS_SELECTOR, "div._2ekpT6PjwtcFaT4jLQehUK.StoreSaleWidgetTitle").text

            # 価格取得
            try:
                price = item.find_element(By.CSS_SELECTOR, "div.StoreSalePriceWidgetContainer").text.strip()
            except:
                price = "Free"

            # レビュー情報
            try:
                review_section = item.find_element(By.CSS_SELECTOR, "a.ReviewScore")
                overall_reviews = review_section.find_element(By.CSS_SELECTOR, "div._2nuoOi5kC2aUI12z85PneA").text
                review_count = review_section.find_element(By.CSS_SELECTOR, "div._1wXL_MfRpdKQ3wZiNP5lrH").text.split()[0]
            except:
                overall_reviews = "No Reviews"
                review_count = "0"

            # タグ情報の取得（新しいタブで取得）
            try:
                driver.execute_script("window.open('');")  # 新しいタブを開く
                driver.switch_to.window(driver.window_handles[1])  # 新しいタブに切り替える
                driver.get(game_url)  # 個別ページに移動
                time.sleep(2)

                # タグを取得
                tags_section = driver.find_elements(By.CSS_SELECTOR, "div.glance_tags a.app_tag")
                tags = [tag.text.strip() for tag in tags_section if tag.text.strip()]
                tags_list = ", ".join(tags) if tags else "No Tags"

                driver.close()
                driver.switch_to.window(driver.window_handles[0])  # 元のタブに戻る
            except Exception as e:
                print(f"タグ取得エラー: {e}")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])  # エラー時も元のタブに戻る
                tags_list = "No Tags"

            # データをリストに追加
            data.append({
                "タイトル名": title,
                "アプリID": app_id,
                "対象ページのURL": game_url,
                "Overall Reviews": overall_reviews,
                "Reviewの数": review_count,
                "金額と単位（日本円）": price,
                "タグ一覧": tags_list
            })

        except Exception as e:
            print(f"データ取得エラー: {e}")

finally:
    # WebDriverを終了
    driver.quit()

# データをDataFrameに変換
df = pd.DataFrame(data)

# Markdown形式で保存
with open("steam_games.md", "w", encoding="utf-8") as md_file:
    # テーブルのヘッダー
    md_file.write("| タイトル名 | アプリID | Overall Reviews | Reviewの数 | 金額と単位（日本円） | タグ一覧 |\n")
    md_file.write("|---|---|---|---|---|---|\n")

    # 各行をMarkdown形式に変換して保存
    for _, row in df.iterrows():
        title_with_url = f"[{row['タイトル名']}]({row['対象ページのURL']})"
        price_cleaned = row['金額と単位（日本円）'].replace("\n", " ").replace("  ", " ")
        md_file.write(
            f"| {title_with_url} | {row['アプリID']} | {row['Overall Reviews']} | {row['Reviewの数']} | {price_cleaned} | {row['タグ一覧']} |\n"
        )

print("Markdown形式のテーブルを 'steam_games.md' に出力しました。")
