import pandas as pd
# requirement - pip install openpyxl
from bs4 import BeautifulSoup
import requests
import re
# requirement - pip install xlsxwriter


pd.set_option('display.width', 400)
pd.set_option('display.max_columns', 10)
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_colwidth', 1000)

url = 'https://en.wikipedia.org/wiki/List_of_Game_of_the_Year_awards'
score_url = 'https://www.gamespot.com/games/'

url_response = requests.get(url)
wikipedia_content = url_response.content

soup = BeautifulSoup(wikipedia_content, 'html.parser')

element_h3 = soup.find_all('h3')
wiki_tables = soup.find_all('table', class_='wikitable')

dataframes = []

for h3, table in zip(element_h3, wiki_tables):
    h3_element = h3.text
    df = pd.read_html(str(table))[0]
    dataframes.append((h3_element, df))

excluded = ['Console: ', 'Handheld: ', 'PC: ']


def gamespot_url(game):
    game_url = re.sub(r'[:,\[\][0-9]+]', "", game).strip()
    game_url = game_url.replace(":", "")
    game_url = game_url.replace(" ", "-")
    game_url = game_url.replace("–", "-")
    game_url = game_url.replace("é", "e")
    game_url = game_url.replace("ö", "o")
    game_url = game_url.replace("'", "")
    return 'https://www.gamespot.com/games/' + game_url.lower() + "/reviews"


def modify_game_name(value):
    for word in excluded:
        value = value.replace(word, '')
    return value.strip()


def game_links(dataframes):
    game_links_list = []
    for h3_element, df in dataframes:
        if 'Game' in df.columns:
            df['Game_links'] = df['Game'].apply(gamespot_url)
            df['Game_links'] = df['Game_links'].apply(modify_game_name)
            game_links_list.append(df['Game_links'])
    return game_links_list


def get_scores_from_url(game_links):
    scores_list = []
    for urls in game_links:
        request = requests.get(urls)
        soup = BeautifulSoup(request.text, 'html.parser')

        gamespot_score = soup.find("div", class_="gs-score__cell text-bold")
        gamespot_score = gamespot_score.find("span").text.strip() \
            if gamespot_score and gamespot_score.find("span") else 'N/A'

        metacritic_score = soup.find("dl", class_="reviewObject__metacritic")
        metacritic_score = metacritic_score.find("a").text.strip() \
            if metacritic_score and metacritic_score.find("a") else 'N/A'

        user_avg_score = soup.find("dl", class_="reviewObject__userAvg")
        user_avg_score = user_avg_score.find("a").text.strip() \
            if user_avg_score and user_avg_score.find("a") else 'N/A'

        scores_list.append({
            'GameSpot': gamespot_score,
            'Metacritic': metacritic_score,
            'UserAvg': user_avg_score
        })

    return scores_list


all_dataframes = []

for h3_element, df in dataframes:
    for column in df.columns:
        if 'Game' in column or 'Year' in column:
            df[column] = df[column].apply(
                lambda value: modify_game_name(value) if isinstance(value, str) else value)
            df[column] = df[column].apply(
                lambda value: re.sub(r'\[\d+\]$', '', value) if isinstance(value, str) else value)

        if 'Game' in column:
            df['Review Url'] = df['Game'].apply(
                lambda url_var: gamespot_url(url_var) if isinstance(url_var, str) else None)

            df['GameSpot Rating'] = df['Review Url'].apply(
                lambda url: get_scores_from_url([url])[0]['GameSpot'] if url else 'N/A')
            df['Metacritic Rating'] = df['Review Url'].apply(
                lambda url: get_scores_from_url([url])[0]['Metacritic'] if url else 'N/A')
            df['UserAvg Rating'] = df['Review Url'].apply(
                lambda url: get_scores_from_url([url])[0]['UserAvg'] if url else 'N/A')

        if 'Ref' in df.columns:
            df = df.drop('Ref', axis=1)

    all_dataframes.append(df)

print(all_dataframes)

dataframe = pd.concat(all_dataframes, ignore_index=True)

excel_file = 'game_awards_dataframe.xlsx'

with pd.ExcelWriter(excel_file, engine='xlsxwriter') as w:
    dataframe.to_excel(w, sheet_name='page_1', index=False)
    excel_data = w.sheets['page_1']

    for i, column in enumerate(dataframe.columns):
        excel_column_width = max(dataframe[column].astype(str).str.len().max(), len(column))
        excel_data.set_column(i, i, excel_column_width + 2)
