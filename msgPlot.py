import os
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from collections import Counter
from datetime import datetime
from bs4 import BeautifulSoup

html_files_dir = "./"
mean_window = 10

dates = []
ls = os.listdir(html_files_dir)
if "allDates.txt" in ls: 
    dates = open('allDates.txt', 'r', encoding='utf-8').read().split()
else:
    for file in ls:
        if file.endswith(".html"):
            print(f"Processing {file}")
            html_file_path = os.path.join(html_files_dir, file)
            with open(html_file_path, "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file, "html.parser")
                messages = soup.find_all("div", class_="message")
                real_messages = [m for m in messages if "service" not in m.get("class", [])]

                for msg in real_messages:
                    date_div = msg.find("div", class_="date")
                    if date_div and "title" in date_div.attrs:
                        title = date_div["title"]
                        date = re.match(r"(\d{2}\.\d{2}\.\d{4})", title)
                        if date:
                            dates.append(date.group(1))

    with open(os.path.join(html_files_dir, 'allDates.txt'), 'w', encoding='utf-8') as file:
        file.write("\n".join(dates))

count_by_date = Counter(dates)

sorted_items = sorted(count_by_date.items(), key=lambda x: datetime.strptime(x[0], "%d.%m.%Y"))
ranked_items = sorted(count_by_date.items(), key=lambda x: x[1], reverse=True)
for d, c in ranked_items:
    print(f"{d}: {c}")

df = pd.DataFrame(sorted_items, columns=['date','count'])
df['date'] = pd.to_datetime(df['date'], format="%d.%m.%Y")
df.set_index('date', inplace=True)

df['count_smooth'] = df['count'].rolling(window=mean_window, min_periods=1).mean()

plt.figure(figsize=(14,7))
plt.plot(df.index, df['count_smooth'], linewidth=2) 
plt.title("Telegram Chat Plot")
plt.xlabel("Dates")
plt.ylabel("Messages")
plt.grid(True)
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()