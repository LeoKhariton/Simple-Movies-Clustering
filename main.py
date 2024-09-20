import requests
from bs4 import BeautifulSoup
import csv
from tqdm import tqdm

headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3' }

def get_movie_data(url):
  response = requests.get(url, headers=headers)
  response.raise_for_status()

  soup = BeautifulSoup(response.text, "html.parser")

  title = soup.find("span", class_="hero__primary-text").text.strip()
  year = soup.find("ul", "ipc-inline-list ipc-inline-list--show-dividers sc-ec65ba05-2 joVhBE baseAlt").find("li").find("a").text.strip()
  genres = ", ".join([g.text for g in soup.find_all("span", class_="ipc-chip__text")])
  rating = soup.find("span", class_="sc-eb51e184-1 ljxVSS").text.strip()
  directors_list = [d.find("a").text.strip() for d in soup.find("ul", class_="ipc-inline-list ipc-inline-list--show-dividers ipc-inline-list--inline ipc-metadata-list-item__list-content baseAlt").find_all("li")]
  directors = ", ".join(directors_list)
  description = soup.find("span", class_="sc-2d37a7c7-2 ggeRnl").text.strip()

  return {
    "title": title,
    "year": year,
    "genres": genres,
    "rating": rating,
    "directors": directors,
    "description": description
  }

with open("movies.csv", "w", newline='', encoding="utf-8") as csvfile:
  writer = csv.DictWriter(csvfile, fieldnames=["title", "year", "genres", "rating", "directors", "description"])
  writer.writeheader()

  max_count = 500
  count = 0
  pbar = tqdm(total=max_count)
  i = 33093
  while count < max_count:
    url = f"https://www.imdb.com/title/tt01{i}"
    try:
      movie_data = get_movie_data(url)
      writer.writerow(movie_data)
      count += 1
      pbar.update()
    except: pass
    finally: i += 1
  pbar.close()
  print("Фильмы были успешно записаны.")