from tkinter import *
import json
import os
import read_pdf


class Timetable:
    def __init__(self):
        self.chart = {}
        self.week = {
            'Pn': 'Poniedziałek',
            'Wt': 'Wtorek',
            'Sr': "Środa",
            'Cz': 'Czwartek',
            'Pt': 'Piątek'
        }
        self.shorter_names = {
            'Systemy operacyjne': 'SysOpy',
            'Programowanie skryptowe': 'Skrypty',
            'Wstęp do zwalczania cyberprzestepczości': 'Przestepczość',
            'Bezpieczeństwo aplikacji webowych i mobilnych': 'Webówka',
            'Bezpieczeństwo lokalnych sieci komputerowych': 'Lokalne',
            'Kryptografia': 'Krypto',
            'Fizyka 2': 'Fizyka',
            'Informatyka śledcza': 'Śledcza',
            'Inżynieria społeczna': 'Społeczna',
            'Wychowanie fizyczne': 'WF',
            'Język obcy': 'Angielski'
        }
        self.disabled_lectures = ['Język obcy', 'Wstęp do zwalczania cyberprzestepczości', 'Informatyka śledcza']
        self.disabled_labs = {
            'Skrypty': [1, 2, 4],
            'SysOpy': [2, 3, 4],
            'Lokalne': [1, 3, 4],
            'Webówka': [2],
            'Krypto': [1, 2, 4],
            'Fizyka': [1, 3, 4]
        }
        self.disabled_projects = {
            'Webówka': [2],
            'Krypto': [1, 2, 4]
        }
        self.disabled_recitation = {
            'Fizyka': [2]
        }
        self.disabled = {
            'L': self.disabled_labs,
            'C': self.disabled_recitation,
            'P': self.disabled_projects
        }

    def add_class(self, class_data):
        """
        :param class_data: list containing name, type, group number, time and lecturer
        :type class_data: list
        """
        if class_data[1]['text'] == 'E' \
                or class_data[4]['text'] == '' \
                or class_data[0]['text'] in self.disabled_lectures:
            return

        start_hour = class_data[4]['text'].split(' ')[1]
        start_hour = int(start_hour.split(':')[0]) * 60 + int(start_hour.split(':')[1])
        end_hour = start_hour + 90
        class_data = {
            'name': class_data[0]['text'],
            'type': class_data[1]['text'],
            'num_of_hours': class_data[2]['text'],
            'group': class_data[3]['text'],
            'day': class_data[4]['text'].split(' ')[0] if class_data[4]['text'] != '' else '',
            'start_time': start_hour,
            'end_time': end_hour,
            'earlier_collisions': 0,
            'later_collisions': 0,
            'same_time_collisions': 0
        }
        self.remove_disabled_class(class_data)

    def remove_disabled_class(self, class_data):

        # Get rid of unwanted classes
        if class_data['type'] not in ['W', 'WF', 'Lek']:
            cls_type = class_data['type']
            cls_name = self.shorter_names[class_data['name']]
            disabled_class = self.disabled[cls_type]

            if cls_name in disabled_class.keys() and \
                    class_data['group'] in f'{disabled_class[cls_name]}':
                return

        # Add to chart if wanted
        if class_data['day'] in self.chart.keys():
            if class_data not in self.chart[class_data['day']]:
                self.chart[class_data['day']].append(class_data)
        else:
            self.chart[class_data['day']] = [class_data]

    def check_colisions(self):
        for day in self.chart.keys():
            same_day_classes = self.chart[day]
            same_day_classes = sorted(same_day_classes,
                                      key=lambda day_classes: day_classes['start_time'])

            for current_lesson in same_day_classes:
                for another_lesson in same_day_classes:
                    if another_lesson == current_lesson:
                        continue

                    if another_lesson['start_time'] < current_lesson['start_time'] < another_lesson['end_time']:
                        current_lesson['earlier_collisions'] += 1
                    elif current_lesson['start_time'] < another_lesson['start_time'] < current_lesson['end_time']:
                        current_lesson['later_collisions'] += 1
                    elif current_lesson['start_time'] == another_lesson['start_time']:
                        current_lesson['same_time_collisions'] += 1

            self.chart[day] = same_day_classes


class GraphicalView(Timetable):
    def __init__(self):
        super().__init__()
        self.timetable_frame = None
        self.colors = {
            'W': '#D2691E',
            'P': '#2b8e34',
            'L': '#2b578e',
            'C': '#7e1818',
            'WF': 'red',
            'Lek': 'orange'
        }
        self.class_types = {
            'W': 'Wykład',
            'C': 'Ćwiczenia',
            'P': 'Projekt',
            'L': 'Laby',
            'WF': 'WF',
            'Lek': 'Lektorat'
        }

        self.root = Tk()
        self.configure_root(1280, 960)
        self.init_timetable_view()

    def configure_root(self,
                       width,
                       height,
                       bg_color="black"):
        self.root.configure(bg=bg_color)
        self.root.title("Plan")
        self.root.minsize(width, height)
        self.root.geometry(f"{width}x{height}+500+200")

    def init_timetable_view(self):
        self.timetable_frame = LabelFrame(self.root, text="Plan zajęć:")
        self.timetable_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        hours_label_frame = LabelFrame(self.timetable_frame, text="Godziny", bd=2, relief='groove')
        hours_label_frame.place(relx=0, rely=0, relwidth=0.05, relheight=1)

        for hour in range(8, 22):
            offset_y = hour * 60 - 470
            Label(hours_label_frame, text=f'{hour}:00').place(relx=0.5, y=offset_y, anchor=CENTER)

    @staticmethod
    def change_time_format(start_time,
                           end_time):
        start_hour = start_time // 60
        start_minute = start_time % 60 if start_time % 60 != 0 else f'0{start_time % 60}'
        end_hour = end_time // 60
        end_minute = end_time % 60 if end_time % 60 >= 10 else f'0{end_time % 60}'

        return f'{start_hour}:{start_minute} - {end_hour}:{end_minute}'

    def init_lecture_label(self,
                           day_label_frame,
                           today_class,
                           offset_y,
                           x,
                           width):

        group = f"Grupa: {today_class['group']}\n"

        if today_class['type'] == "W":
            group = ''

        Label(day_label_frame,
              text=f"{self.shorter_names[today_class['name']]}\n"
                   f"{self.class_types[today_class['type']]}\n"
                   f"{group}"
                   f"{self.change_time_format(today_class['start_time'], today_class['end_time'])}",
              bd=2,
              relief='groove',
              bg=self.colors[today_class['type']]
              ).place(y=offset_y,
                      relx=x,
                      relwidth=width,
                      height=90)

    @staticmethod
    def align_colliding_lectures(crnt_class,
                                 prev_x,
                                 prev_width,
                                 prev_max_width,
                                 prev_hour):
        max_width = 1
        if min(crnt_class['earlier_collisions'], crnt_class['later_collisions']) != 0:

            max_collisions = max(crnt_class['earlier_collisions'] + 1,
                                 crnt_class['later_collisions'] + 1)
            max_collisions += crnt_class['same_time_collisions']

        elif crnt_class['earlier_collisions'] != 0 \
                and crnt_class['later_collisions'] == 0:

            max_collisions = crnt_class['same_time_collisions'] + 1
            max_width = max(prev_x, prev_width) \
                if prev_hour != crnt_class['start_time'] \
                else prev_max_width

        else:

            max_collisions = crnt_class['earlier_collisions'] + \
                             crnt_class['later_collisions'] + \
                             crnt_class['same_time_collisions'] + 1

        offset_y = crnt_class['start_time'] - 470
        width = max_width / max_collisions

        x = prev_x + prev_width
        x = 0 if x + width > 1 else x

        return x, offset_y, width, max_width

    def add_classes_view(self):

        for day_index, day in enumerate(self.week.keys()):

            day_label_frame = LabelFrame(self.timetable_frame,
                                         text=f"{self.week[day]}",
                                         bd=2,
                                         relief='groove')
            day_label_frame.place(relx=0.05 + day_index * 0.95 / 5,
                                  rely=0,
                                  relwidth=0.95 / 5,
                                  relheight=1)

            crnt_day_lectures = self.chart[day]
            prev_x = 0
            prev_width = 0
            for idx, crnt_class in enumerate(crnt_day_lectures):

                if idx == 0:
                    prev_hour = None
                    prev_max_width = None

                x, offset_y, width, max_width = \
                    self.align_colliding_lectures(crnt_class,
                                                  prev_x,
                                                  prev_width,
                                                  prev_max_width,
                                                  prev_hour)
                self.init_lecture_label(day_label_frame,
                                        crnt_class,
                                        offset_y,
                                        x, width)
                prev_x = x
                prev_width = width
                prev_hour = crnt_class['start_time']
                prev_max_width = max_width


if __name__ == '__main__':

    if not os.path.isfile('table.json'):
        read_pdf.read_pdf()

    with open('table.json', 'r') as file:
        table = json.loads(file.read())

    timetable = GraphicalView()
    for idx, row in enumerate(table):
        class_name = row[0]['text']
        if idx != 0:
            timetable.add_class(row)
    timetable.check_colisions()
    timetable.add_classes_view()
    timetable.root.mainloop()
