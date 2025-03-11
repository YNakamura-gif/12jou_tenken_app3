import streamlit as st
import pandas as pd
import os
import json
import datetime
from pathlib import Path

# ページ設定
st.set_page_config(
    page_title="12条点検 Web アプリ",
    layout="wide",
    initial_sidebar_state="expanded"
)

# セッション状態の初期化
if 'deterioration_items' not in st.session_state:
    st.session_state.deterioration_items = []
if 'deterioration_counter' not in st.session_state:
    st.session_state.deterioration_counter = 1
if 'location_input' not in st.session_state:
    st.session_state.location_input = ""
if 'deterioration_name_input' not in st.session_state:
    st.session_state.deterioration_name_input = ""
if 'photo_number_input' not in st.session_state:
    st.session_state.photo_number_input = ""

# マスターデータの読み込み
def load_master_data(file_path, encoding='utf-8'):
    # 試すエンコーディングのリスト
    encodings = ['utf-8', 'shift_jis', 'cp932', 'utf-8-sig']
    
    if not os.path.exists(file_path):
        st.warning(f"マスターデータファイルが見つかりません: {file_path}")
        return []
    
    # 複数のエンコーディングを試す
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            return df.iloc[:, 0].tolist()
        except Exception as e:
            continue
    
    # すべてのエンコーディングが失敗した場合
    st.error(f"マスターデータの読み込みに失敗しました: {file_path}")
    return []

# 予測変換機能
def get_suggestions(input_text, master_list):
    if not input_text:
        return []
    
    # 入力テキストで始まる項目を検索（大文字小文字を区別しない）
    suggestions = [item for item in master_list if item.lower().startswith(input_text.lower())]
    
    # 部分一致も検索（入力テキストが含まれる項目）
    if not suggestions:
        suggestions = [item for item in master_list if input_text.lower() in item.lower()]
    
    return suggestions

# マスターデータの読み込み
locations = load_master_data('master/locations.csv')
deteriorations = load_master_data('master/deteriorations.csv')

# タイトル
st.title("12条点検 Web アプリ")

# タブの作成
tab1, tab2 = st.tabs(["点検入力", "データ閲覧"])

# 点検入力タブ
with tab1:
    st.header("点検情報入力")
    
    # 基本情報セクション
    col1, col2 = st.columns(2)
    with col1:
        inspection_date = st.date_input("点検日", value=datetime.date.today())
        inspector_name = st.text_input("点検者名")
    
    with col2:
        site_id = st.text_input("現場ID")
        remarks = st.text_area("備考", height=100)
    
    st.divider()
    
    # 劣化内容セクション
    st.subheader("劣化内容入力")
    
    # 入力フォーム
    with st.form(key="deterioration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # 劣化番号の表示
            st.write(f"劣化番号: {st.session_state.deterioration_counter}")
            
            # 場所の入力（予測変換機能付き）
            location_input = st.text_input(
                "場所",
                value=st.session_state.location_input,
                key="location_input_field",
                help="入力すると候補が表示されます。スマホのフリック入力にも対応しています。"
            )
            
            # 場所の予測候補表示
            location_suggestions = get_suggestions(location_input, locations)
            if location_suggestions and location_input:
                location = st.radio(
                    "場所の候補:",
                    options=location_suggestions,
                    key="location_suggestions",
                    horizontal=True
                )
            else:
                location = location_input
            
        with col2:
            # 劣化名の入力（予測変換機能付き）
            deterioration_name_input = st.text_input(
                "劣化名",
                value=st.session_state.deterioration_name_input,
                key="deterioration_name_input_field",
                help="入力すると候補が表示されます。スマホのフリック入力にも対応しています。"
            )
            
            # 劣化名の予測候補表示
            deterioration_suggestions = get_suggestions(deterioration_name_input, deteriorations)
            if deterioration_suggestions and deterioration_name_input:
                deterioration_name = st.radio(
                    "劣化名の候補:",
                    options=deterioration_suggestions,
                    key="deterioration_suggestions",
                    horizontal=True
                )
            else:
                deterioration_name = deterioration_name_input
            
            # 写真番号の入力
            photo_number = st.text_input(
                "写真番号",
                value=st.session_state.photo_number_input,
                key="photo_number_input"
            )
        
        # 追加ボタン
        submit_button = st.form_submit_button("追加")
        
        if submit_button:
            if location and deterioration_name:
                # 劣化項目の追加
                deterioration_item = {
                    "deterioration_id": st.session_state.deterioration_counter,
                    "location": location,
                    "deterioration_name": deterioration_name,
                    "photo_number": photo_number
                }
                
                st.session_state.deterioration_items.append(deterioration_item)
                st.session_state.deterioration_counter += 1
                
                # 入力フィールドのクリア
                st.session_state.location_input = ""
                st.session_state.deterioration_name_input = ""
                st.session_state.photo_number_input = ""
                
                st.success("劣化項目を追加しました")
                st.experimental_rerun()
            else:
                st.error("場所と劣化名は必須項目です")
    
    # 追加された劣化項目の表示
    if st.session_state.deterioration_items:
        st.subheader("追加済み劣化項目")
        
        # データフレームの作成
        deterioration_df = pd.DataFrame(st.session_state.deterioration_items)
        st.dataframe(deterioration_df, use_container_width=True)
        
        # 削除機能
        if st.button("選択した劣化項目を削除"):
            st.session_state.deterioration_items = []
            st.session_state.deterioration_counter = 1
            st.success("すべての劣化項目を削除しました")
            st.experimental_rerun()
    
    # 保存ボタン
    if st.button("点検データを保存", type="primary"):
        if not st.session_state.deterioration_items:
            st.warning("保存する劣化項目がありません")
        else:
            try:
                # データの準備
                inspection_data = {
                    "inspection_date": inspection_date.strftime("%Y-%m-%d"),
                    "inspector_name": inspector_name,
                    "site_id": site_id,
                    "remarks": remarks,
                    "deterioration_items": st.session_state.deterioration_items
                }
                
                # データフレームの作成
                rows = []
                for item in st.session_state.deterioration_items:
                    row = {
                        "点検日": inspection_date.strftime("%Y-%m-%d"),
                        "点検者名": inspector_name,
                        "現場ID": site_id,
                        "備考": remarks,
                        "劣化番号": item["deterioration_id"],
                        "場所": item["location"],
                        "劣化名": item["deterioration_name"],
                        "写真番号": item["photo_number"]
                    }
                    rows.append(row)
                
                df = pd.DataFrame(rows)
                
                # 保存先ディレクトリの確認
                data_dir = Path("data")
                data_dir.mkdir(exist_ok=True)
                
                # CSVファイルへの保存
                file_path = data_dir / "inspection_data.csv"
                
                # 既存ファイルがある場合は追記
                if file_path.exists():
                    try:
                        existing_df = pd.read_csv(file_path, encoding='utf-8-sig')
                        df = pd.concat([existing_df, df], ignore_index=True)
                    except Exception as e:
                        st.warning(f"既存データの読み込みに失敗しました。新しいファイルを作成します: {e}")
                
                # CSVファイルに保存（Excel貼り付け対応）
                try:
                    df.to_csv(file_path, index=False, encoding='utf-8-sig')
                    st.success(f"点検データを保存しました: {file_path}")
                    
                    # Streamlit Cloudでの運用のためのメッセージ
                    if os.environ.get('STREAMLIT_SHARING') or os.environ.get('STREAMLIT_CLOUD'):
                        st.info("Streamlit Cloud上で実行中です。データの永続化のためには、保存されたCSVファイルをダウンロードして、GitHubリポジトリに追加してください。")
                    
                    # セッション状態のリセット
                    st.session_state.deterioration_items = []
                    st.session_state.deterioration_counter = 1
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"データ保存中にエラーが発生しました: {e}")
                
            except Exception as e:
                st.error(f"データ保存中にエラーが発生しました: {e}")

# データ閲覧タブ
with tab2:
    st.header("点検データ閲覧")
    
    # データファイルの読み込み
    data_file = Path("data/inspection_data.csv")
    
    if data_file.exists():
        try:
            df = pd.read_csv(data_file, encoding='utf-8-sig')
            
            # 検索・フィルタリング機能
            st.subheader("データ検索")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                search_date = st.date_input("点検日で検索", value=None, key="search_date", help="点検日で絞り込み")
            
            with col2:
                search_site = st.text_input("現場IDで検索", key="search_site", help="現場IDで部分一致検索")
            
            with col3:
                search_photo = st.text_input("写真番号で検索", key="search_photo", help="写真番号で部分一致検索")
            
            # 検索条件の適用
            filtered_df = df.copy()
            
            if search_date:
                filtered_df = filtered_df[filtered_df["点検日"] == search_date.strftime("%Y-%m-%d")]
            
            if search_site:
                filtered_df = filtered_df[filtered_df["現場ID"].str.contains(search_site, na=False)]
            
            if search_photo:
                filtered_df = filtered_df[filtered_df["写真番号"].astype(str).str.contains(search_photo, na=False)]
            
            # 検索結果の表示
            st.subheader("検索結果")
            st.dataframe(filtered_df, use_container_width=True)
            
            # CSVダウンロード機能
            csv = filtered_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="CSVダウンロード",
                data=csv,
                file_name="inspection_data_export.csv",
                mime="text/csv",
            )
            
        except Exception as e:
            st.error(f"データ読み込み中にエラーが発生しました: {e}")
    else:
        st.info("保存された点検データがありません。点検入力タブからデータを入力してください。")

# フッター
st.divider()
st.caption("© 2025 12条点検 Web アプリ") 