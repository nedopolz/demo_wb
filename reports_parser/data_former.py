import datetime
import os

import pandas as pd
from asgiref.sync import async_to_sync

from reports_parser.config import DOCS_PATH
from reports_parser.utils import get_name, get_prev_monday


class ReportFormer:
    """this class converts csv database to csv report"""

    def get_files_list(self) -> list:
        """returns list of supplier folders and proper names"""
        files = [x[0] for x in os.walk(f'{DOCS_PATH}')]
        files.pop(0)
        ans = []
        for i in files:
            name = async_to_sync(get_name)(i.split('/')[-1])
            print(name)
            ans.append([f'{i}/report.csv', name[0].oldID])
        return ans

    def add_articule_data_to_report(self, articul, current_df, main_report_df, supplyer_name):
        needed_colums = ['Поставщик', 'Дата отчета', 'Склад', 'Артикул', 'URL главного фото', 'Наименование', 'Бренд',
                         'Артикул поставщика', 'Размер', 'Баркод', 'Тип документа', 'Кол-во', 'Сумма продаж',
                         'Сумма комиссии продаж',
                         'стоим хранен', 'None', 'Вознаграждение поставщику', 'Обоснование для оплаты',
                         'К перечислению за товар',
                         'Количество доставок', 'Количество возврата', 'Стоимость логистики, с НДС']

        insert_dict = dict.fromkeys(needed_colums)
        insert_dict['Поставщик'] = supplyer_name
        insert_dict['Дата отчета'] = get_prev_monday()
        insert_dict['Артикул'] = articul
        temp_df = current_df.loc[current_df['Код номенклатуры'] == articul]
        insert_dict['Бренд'] = temp_df['Бренд'].iloc[0]
        insert_dict['Артикул поставщика'] = temp_df['Артикул поставщика'].iloc[0]
        insert_dict['Баркод'] = temp_df['Баркод'].iloc[0]
        warehouse_df = temp_df[temp_df['Склад'].str.contains('Склад поставщика')]
        temp_df = temp_df[~temp_df['Склад'].str.contains('Склад поставщика')]
        if len(warehouse_df) > 0:
            insert_dict['Склад'] = 'Склад поставщика'
            insert_dict['Кол-во'] = int(
                warehouse_df['Кол-во'].where(warehouse_df['Тип документа'] == 'Продажа').sum() - warehouse_df['Кол-во'].where(
                    warehouse_df['Тип документа'] == 'Возврат').sum())
            insert_dict['Сумма продаж'] = round(
                warehouse_df['Вайлдберриз реализовал Товар (Пр)'].where(warehouse_df['Тип документа'] == 'Продажа').sum() -
                warehouse_df[
                    'Вайлдберриз реализовал Товар (Пр)'].where(warehouse_df['Тип документа'] == 'Возврат').sum(), 3)
            insert_dict['Сумма комиссии продаж'] = round(
                warehouse_df['Вознаграждение Вайлдберриз (ВВ), без НДС'].where(warehouse_df['Тип документа'] == 'Продажа').sum() -
                warehouse_df[
                    'Вознаграждение Вайлдберриз (ВВ), без НДС'].where(warehouse_df['Тип документа'] == 'Возврат').sum() +
                warehouse_df['Возмещение Расходов услуг поверенного'].where(
                    warehouse_df['Тип документа'] == 'Продажа').sum() - warehouse_df[
                    'Возмещение Расходов услуг поверенного'].where(warehouse_df['Тип документа'] == 'Возврат').sum() +
                warehouse_df['НДС с Вознаграждения Вайлдберриз'].where(warehouse_df['Тип документа'] == 'Продажа').sum() -
                warehouse_df[
                    'НДС с Вознаграждения Вайлдберриз'].where(warehouse_df['Тип документа'] == 'Возврат').sum(), 3)
            insert_dict['Вознаграждение поставщику'] = round(
                warehouse_df['К перечислению Продавцу за реализованный Товар'].where(
                    warehouse_df['Обоснование для оплаты'] == 'Продажа').sum() - warehouse_df[
                    'К перечислению Продавцу за реализованный Товар'].where(
                    warehouse_df['Обоснование для оплаты'] == 'Возврат').sum(), 3)
            insert_dict['К перечислению за товар'] = round(
                warehouse_df['К перечислению Продавцу за реализованный Товар'].where(
                    warehouse_df['Обоснование для оплаты'] == 'Продажа').sum() - warehouse_df[
                    'К перечислению Продавцу за реализованный Товар'].where(
                    warehouse_df['Обоснование для оплаты'] == 'Возврат').sum(), 3) - warehouse_df[
                                                         'Услуги по доставке товара покупателю'].sum()
            insert_dict['Количество доставок'] = warehouse_df['Количество доставок'].sum()
            insert_dict['Количество возврата'] = warehouse_df['Количество возврата'].sum()
            insert_dict['Стоимость логистики, с НДС'] = warehouse_df['Услуги по доставке товара покупателю'].sum()
            main_report_df = main_report_df.append(insert_dict, ignore_index=True)
        if len(temp_df) > 0:
            insert_dict['Склад'] = ''
            insert_dict['Кол-во'] = int(
                temp_df['Кол-во'].where(temp_df['Тип документа'] == 'Продажа').sum() - temp_df['Кол-во'].where(
                    temp_df['Тип документа'] == 'Возврат').sum())
            insert_dict['Сумма продаж'] = round(
                temp_df['Вайлдберриз реализовал Товар (Пр)'].where(temp_df['Тип документа'] == 'Продажа').sum() -
                temp_df[
                    'Вайлдберриз реализовал Товар (Пр)'].where(temp_df['Тип документа'] == 'Возврат').sum(), 3)
            insert_dict['Сумма комиссии продаж'] = round(
                temp_df['Вознаграждение Вайлдберриз (ВВ), без НДС'].where(temp_df['Тип документа'] == 'Продажа').sum() -
                temp_df[
                    'Вознаграждение Вайлдберриз (ВВ), без НДС'].where(temp_df['Тип документа'] == 'Возврат').sum() +
                temp_df['Возмещение Расходов услуг поверенного'].where(
                    temp_df['Тип документа'] == 'Продажа').sum() - temp_df[
                    'Возмещение Расходов услуг поверенного'].where(temp_df['Тип документа'] == 'Возврат').sum() +
                temp_df['НДС с Вознаграждения Вайлдберриз'].where(temp_df['Тип документа'] == 'Продажа').sum() -
                temp_df[
                    'НДС с Вознаграждения Вайлдберриз'].where(temp_df['Тип документа'] == 'Возврат').sum(), 3)
            insert_dict['Вознаграждение поставщику'] = round(
                temp_df['К перечислению Продавцу за реализованный Товар'].where(
                    temp_df['Обоснование для оплаты'] == 'Продажа').sum() - temp_df[
                    'К перечислению Продавцу за реализованный Товар'].where(
                    temp_df['Обоснование для оплаты'] == 'Возврат').sum(), 3)
            insert_dict['К перечислению за товар'] = round(
                temp_df['К перечислению Продавцу за реализованный Товар'].where(
                    temp_df['Обоснование для оплаты'] == 'Продажа').sum() - temp_df[
                    'К перечислению Продавцу за реализованный Товар'].where(
                    temp_df['Обоснование для оплаты'] == 'Возврат').sum(), 3) - temp_df[
                                                         'Услуги по доставке товара покупателю'].sum()
            insert_dict['Количество доставок'] = temp_df['Количество доставок'].sum()
            insert_dict['Количество возврата'] = temp_df['Количество возврата'].sum()
            insert_dict['Стоимость логистики, с НДС'] = temp_df['Услуги по доставке товара покупателю'].sum()
            main_report_df = main_report_df.append(insert_dict, ignore_index=True)
        return main_report_df

    def add_to_main_report(self, file, main_report_df):
        """forms file data and ads it ti main report"""
        df = pd.read_csv(file[0])
        articules = list(df['Код номенклатуры'].unique())
        for articul in articules:
            main_report_df = self.add_articule_data_to_report(articul, df, main_report_df, file[1])
        return main_report_df

    def create_main_file(self):
        """creates main report file"""
        file_name = datetime.date.today()
        with open(f'{DOCS_PATH}/{file_name}.csv', 'a+') as file:
            pass

    def add_supplyer_column(self):
        files = self.get_files_list()
        for file in files:
            file[0] = file[0].replace('/report.csv', '/remain.csv')
            default_text = file[1]
            with open(file[0], 'r') as csv_file:
                data = csv_file.readlines()
                if len(data[0].split(',')) > 2:
                    return
            for i in range(len(data)):
                data[i] = f'{default_text},{data[i]}'
            with open(file[0], 'w') as csv_file:
                csv_file.writelines(data)

    def start_convert(self) -> None:
        files_and_supplyers = self.get_files_list()
        self.create_main_file()
        needed_colums = ['Поставщик', 'Дата отчета', 'Склад', 'Артикул', 'URL главного фото', 'Наименование', 'Бренд',
                         'Артикул поставщика', 'Размер', 'Баркод', 'Кол-во', 'Сумма продаж',
                         'Сумма комиссии продаж',
                         'стоим хранен', 'None', 'Вознаграждение поставщику',
                         'К перечислению за товар',
                         'Количество доставок', 'Количество возврата', 'Стоимость логистики, с НДС']
        write_df = pd.DataFrame(columns=needed_colums, dtype='object')
        for file in files_and_supplyers:
            write_df = self.add_to_main_report(file, write_df)
        write_df.to_csv(path_or_buf=f'{DOCS_PATH}/{datetime.date.today()}.csv', index=False, header=False, sep=';',
                        decimal=",")

        self.add_supplyer_column()
