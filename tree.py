from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os

def print_element_tree(element, depth=0):
    """
    再帰的にツリー構造を作成する関数
    """
    # タグ名、class属性、id属性を取得
    tag_name = element.name
    class_attr = " ".join(element.get("class", []))
    id_attr = element.get("id", "")
    
    # インデントを調整し出力
    indent = "│   " * depth
    line = f"{indent}├── {tag_name}"
    if class_attr:
        line += f" .{class_attr}"
    if id_attr:
        line += f" #{id_attr}"
    print(line)
    
    # 子要素を再帰的に処理
    for child in element.find_all(recursive=False):
        print_element_tree(child, depth + 1)


def main():
    # URLの指定
    url = "https://store.steampowered.com/sale/nextfestmostplayed_oct_2024"  # 任意のURLに変更してください

    # Selenium設定
    chrome_service = Service(ChromeDriverManager().install())
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # ヘッドレスモード
    chrome_options.add_argument('--start-maximized')

    # WebDriverの起動
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    try:
        # 指定したURLにアクセス
        driver.get(url)
        html = driver.page_source  # HTMLソースを取得

        # BeautifulSoupで解析
        soup = BeautifulSoup(html, "html.parser")

        # ツリー構造を出力
        print("HTML要素ツリー:")
        print_element_tree(soup.body)  # bodyタグを基点にツリー構造を出力

    finally:
        # WebDriverを終了
        driver.quit()


if __name__ == "__main__":
    main()
