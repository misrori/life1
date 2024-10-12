from scrapethat import *
import pandas as pd
from datetime import datetime, timedelta

today = datetime.today()
today_date_file_name = f"data/life1_class_{today.strftime('%Y-%m-%d')}.csv"
 
# 'https://booking.life1.hu/allee/orarend/'

def get_time_table(url):

    t = read_html(url)

    # Get today's date
    today = datetime.today()

    # Find the start of the current week (Monday)
    start_of_week = today - timedelta(days=today.weekday())

    # Generate the list of dates for this week
    this_week_dates = [(start_of_week + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]

    # Generate the list of dates for next week
    next_week_dates = [(start_of_week + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7, 14)]

    days = ["Hétfő", "Kedd", "Szerda", "Csütörtök", "Péntek", "Szombat", "Vasárnap"]
    all_class = []

    tablak  = t.find_all(class_='actualWeek')

    for day_period in range(len(tablak)):
        sorok = tablak[day_period]
        sorok_data = sorok.find_all('tr')

        for i in range(1, len(sorok_data)):
            egysor_data = sorok_data[i].find_all('td')
            for j in range(len(egysor_data)):
                try:
                    for many_class in range(len(egysor_data[j].select(".timetableSport"))): # in one row multiple class
                        new_data_class = {
                            "day":days[j],
                            "date": this_week_dates[j],
                            "sport": egysor_data[j].select(".timetableSport")[many_class].text,
                            "time": egysor_data[j].select(".timetableHour")[many_class].text,
                            "edző": egysor_data[j].select(".timetableCoach")[many_class].text
                        }
                        all_class.append(new_data_class)  
                except:
                    pass

    # next week 
    tablak  = t.find_all(class_='nextWeek')

    for day_period in range(len(tablak)):
        sorok = tablak[day_period]
        sorok_data = sorok.find_all('tr')

        for i in range(1, len(sorok_data)):
            egysor_data = sorok_data[i].find_all('td')
            for j in range(len(egysor_data)):
                try:
                    for many_class in range(len(egysor_data[j].select(".timetableSport"))): # in one row multiple class
                        new_data_class = {
                            "day":days[j],
                            "date": next_week_dates[j],
                            "sport": egysor_data[j].select(".timetableSport")[many_class].text,
                            "time": egysor_data[j].select(".timetableHour")[many_class].text,
                            "edző": egysor_data[j].select(".timetableCoach")[many_class].text
                        }
                        all_class.append(new_data_class)  
                except:
                    pass

    df = pd.DataFrame(all_class)
    df["klub"] = url.split("/")[3]
    return df

data = get_time_table('https://booking.life1.hu/nyugati/orarend/')

places = ['https://booking.life1.hu/allee/orarend/', 'https://booking.life1.hu/nyugati/orarend/', 'https://booking.life1.hu/corvin/orarend/',
          'https://booking.life1.hu/springday/orarend/', 'https://booking.life1.hu/etele/orarend/', 'https://booking.life1.hu/gilda/orarend/', 
          'https://booking.life1.hu/vaci35/orarend/']


dfs_list = list(map(get_time_table, places))
all_data = pd.concat(dfs_list, ignore_index=True)

all_data
all_data.to_csv("orarend.csv", index=False)
all_data.to_csv(today_date_file_name, index=False)

