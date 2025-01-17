import sys  # 追加
import streamlit as st
from PIL import Image, ImageOps
import io
from database import add_post, update_likes, get_all_posts, search_posts, get_all_tags, setup_database, upload_file_to_s3, DATABASE_PATH
from streamlit_tags import st_tags
import base64

# デバッグモードのチェック
debug_mode = '-d' in sys.argv  # 追加
# データベースをセットアップ
setup_database()

# Base64エンコードされた画像を生成する関数
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()
# 画像を縮小する関数
def resize_image(image_data, max_width=1200):
    image = Image.open(io.BytesIO(image_data))
    if image.width > max_width:
        ratio = max_width / float(image.width)
        new_height = int(float(image.height) * ratio)
        resized_image = image.resize((max_width, new_height), Image.LANCZOS)
        
        # RGBAからRGBへの変換
        if resized_image.mode == 'RGBA':
            # 透過部分を白で塗りつぶす
            background = Image.new('RGB', resized_image.size, (255, 255, 255))
            background.paste(resized_image, (0, 0), resized_image)
            resized_image = background
        
        output = io.BytesIO()
        resized_image.save(output, format='JPEG')
        return output.getvalue()
    return image_data

# UIの設定
st.set_page_config(layout="wide")

st.title('介護福祉のアイデアサイト')
st.write("""
このサイトは、介護福祉に関する様々なアイデアや情報を共有し、
多くの人々が役立つ情報を見つけることができる場を提供することを目的としています。
介護に関する知識や経験を共有することで、介護現場の改善や新しいアイデアの創出に寄与します。
         
公式ドキュメントはこちらをご覧ください: [公式ドキュメント](https://kakeru58.github.io/KaigoIdeas/)
         
このサイトを作ろうと思ったきっかけはこちらをご覧ください: [柴田教授ブログ](https://tom-shibata.hatenablog.com/entry/2024/07/10/203109)
""")

# 新しい投稿の入力フォーム
st.header('新しい投稿を追加')
title = st.text_input('タイトル')
image = st.file_uploader('画像（オプション）', type=['jpg', 'jpeg', 'png'])
details = st.text_area('詳細')

# すべてのタグを取得
all_tags = get_all_tags()

# タグの入力（自動補完）
tags = st_tags(
    label='タグを追加',
    text='タグを入力',
    value=[],
    suggestions=all_tags,
    maxtags=10,
    key='tags_input'
)

if st.button('投稿'):
    if title and details:
        image_data = image.read() if image else None
        if image_data:
            image_data = resize_image(image_data)
        add_post(title, image_data, details, tags)
        st.success('投稿が追加されました')
        if not debug_mode:  # 追加
            upload_file_to_s3(DATABASE_PATH, 'ideas.db')  # データベースをS3にアップロード
    else:
        st.error('タイトルと詳細を入力してください')

# 投稿検索機能
st.header('投稿を検索')
st.write('検索キーワードを入力するか、タグを追加して検索してください。')
query = st.text_input('検索キーワード')
search_tags = st.multiselect(
    'タグを選択',
    options=all_tags,
    default=[],
    key='search_tags_input'
)

if st.button('検索'):
    if query or search_tags:
        search_query = query
        if search_tags:
            if query:
                search_query += ' '
            search_query += ' '.join(search_tags)
        posts = search_posts(search_query)
    else:
        posts = get_all_posts()
else:
    posts = get_all_posts()

# タグを丸く囲んで表示するスタイル
tag_style = """
<style>
.tag {
    display: inline-block;
    background-color: #f3f4f6;
    border-radius: 12px;
    padding: 5px 10px;
    margin: 5px;
    font-size: 14px;
    color: #333;
}
</style>
"""
# 投稿を表示
st.header('投稿一覧')
st.markdown(tag_style, unsafe_allow_html=True)
liked_posts = st.session_state.get('liked_posts', set())
for post in posts:
    st.markdown("---")
    if post['image']:
        col1, col2 = st.columns([3, 1.5])
        with col2:
            st.image(Image.open(io.BytesIO(post['image'])), use_column_width=True)
        with col1:
            st.subheader(post['title'])
            st.write(post['details'])
            tags_html = ''.join(f'<span class="tag">{tag}</span>' for tag in post['tags'].split(','))
            st.markdown(tags_html, unsafe_allow_html=True)
            st.write(f"いいね: {post['likes']}")
            if st.button('いいね', key=f"like_{post['id']}", disabled=(post['id'] in liked_posts)):
                update_likes(post['id'])
                liked_posts.add(post['id'])
                st.session_state['liked_posts'] = liked_posts
                if not debug_mode:  # 追加
                    upload_file_to_s3(DATABASE_PATH, 'ideas.db')  # いいねを反映したDBをS3にアップロード
                st.experimental_rerun()
    else:
        st.subheader(post['title'])
        st.write(post['details'])
        tags_html = ''.join(f'<span class="tag">{tag}</span>' for tag in post['tags'].split(','))
        st.markdown(tags_html, unsafe_allow_html=True)
        st.write(f"いいね: {post['likes']}")
        if st.button('いいね', key=f"like_{post['id']}", disabled=(post['id'] in liked_posts)):
            update_likes(post['id'])
            liked_posts.add(post['id'])
            st.session_state['liked_posts'] = liked_posts
            upload_file_to_s3(DATABASE_PATH, 'ideas.db')  # いいねを反映したDBをS3にアップロード
            st.experimental_rerun()


# コントリビューターセクション
st.markdown("""<hr style="height:2px;border:none;color:#333;background-color:#333;" />""", unsafe_allow_html=True)
st.header('システム開発における貢献者')

# コントリビューターの情報
contributors = [
    {"name": "Kakeru Yamasaki", "github": "https://github.com/kakeru58"},
    # 追加のコントリビューターがいればここに追加
]

# スタイルの定義
contributor_style = """
<style>
.contributor {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
}
.contributor img {
    border-radius: 50%;
    width: 50px;
    height: 50px;
    margin-right: 20px;
}
.contributor a {
    text-decoration: none;
    color: #007BFF;
    font-weight: bold;
}
.contributor a:hover {
    text-decoration: underline;
}
</style>
"""

st.markdown(contributor_style, unsafe_allow_html=True)

# コントリビューターを表示
for contributor in contributors:
    github_username = contributor["github"].split("/")[-1]
    profile_image_url = f"https://github.com/{github_username}.png"
    st.markdown(
        f"""
        <div class="contributor">
            <img src="{profile_image_url}" alt="{contributor['name']}" width="50">
            <a href="{contributor['github']}" target="_blank">{contributor['name']}</a>
        </div>
        """,
        unsafe_allow_html=True
    )
# フッターに著作権情報とロゴを表示
st.markdown("---")
# ロゴ画像をBase64エンコード
logo1_path = "logo1.png"  # それぞれのロゴのパスに変更
logo2_path = "logo2.png"
logo3_path = "logo3.png"

logo1_base64 = get_base64_image(logo1_path)
logo2_base64 = get_base64_image(logo2_path)
logo3_base64 = get_base64_image(logo3_path)

# フッターに著作権情報とBase64エンコードされたロゴを表示
footer_col1, footer_col2 = st.columns([8, 1])

with footer_col1:
    st.write("© 2024 Kakeru Yamasaki. Licensed under the MIT License.")

with footer_col2:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center;">
            <a href="https://yamasaki5868688.wixsite.com/hsc-site/%E3%81%99%E3%81%90%E5%89%B5%E3%82%8B%E8%AA%B2" target="_blank">
                <img src="data:image/png;base64,{logo1_base64}" alt="Logo" style="width: 70px; margin-left: 20px;">
            </a>
            <a href="https://slc3lab.jp/" target="_blank">
                <img src="data:image/png;base64,{logo2_base64}" alt="Logo" style="width: 70px; margin-left: 20px;">
            </a>
            <a href="https://yamasaki5868688.wixsite.com/cctechnology" target="_blank">
                <img src="data:image/png;base64,{logo3_base64}" alt="Logo" style="width: 70px; margin-left: 20px;">
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )