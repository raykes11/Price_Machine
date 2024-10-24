import os

import pandas as pd


class PriceMachine():

    def __init__(self):
        self.data = []  # Общая таблица
        self.result = []  # Найденные позиции
        self.input_text = ''  # Наименование позиции

    def load_prices(self, file_path=''):
        '''
            Сканирует указанный каталог. Ищет файлы со словом price в названии.
            В файле ищет столбцы с названием товара, ценой и весом.
            Допустимые названия для столбца с товаром:
                товар
                название
                наименование
                продукт
                
            Допустимые названия для столбца с ценой:
                розница
                цена
                
            Допустимые названия для столбца с весом (в кг.)
                вес
                масса
                фасовка
        '''
        true_product_title = ["название", "продукт", "товар", "наименование"]
        true_price_title = ["цена", "розница"]
        true_mass_title = ["фасовка", "масса", "вес"]

        if file_path != '':  # Если указан путь к файлу, изменить директорию
            os.chdir(file_path)

        # Получаем список всех файлов в директории
        list_file = os.listdir()
        price_file = [price_file for price_file in list_file if '.csv' in price_file and 'price' in price_file.lower()]

        # Создание пустого DataFrame с заранее определенными типами столбцов
        column_types = {'Наименование': 'object', 'цена': 'float64', 'вес': 'float64', 'файл': 'object',
                        'цена за кг.': 'float64'}
        column = pd.DataFrame(columns=column_types.keys()).astype(column_types)

        # Создание  таблиц из найденых счетов
        df_list = []
        df_list.append(column)
        for file in price_file:
            df = pd.read_csv(file)
            title = df.columns.tolist()
            columns_rename = {}
            for name in title:
                if name.lower() in true_product_title:
                    columns_rename[name] = 'Наименование'
                elif name.lower() in true_price_title:
                    columns_rename[name] = 'цена'
                elif name.lower() in true_mass_title:
                    columns_rename[name] = 'вес'
                else:
                    df = df.drop(name, axis=1)
            df = df.rename(columns=columns_rename)
            df['файл'] = file
            df['цена за кг.'] = round(df['цена'] / df['вес'], 2)
            df_list.append(df)

        # Объединение всех таблиц в одну
        all_price = pd.concat(df_list, ignore_index=True)
        self.data = all_price

        # Обработка пустой таблицы
        if len(self.data) == 0:
            print(f'''
            Не найдены счета или столбцы имеют не правильное значение.
            Вставте счета в папку с файлом "project.py".
            Путь к файлу: {os.getcwd()} 
            Cчета должны иметь в назывании "price"
            Cчета должны быть формата ".csv"
            Правильные названия столбца для Наименования: {true_product_title}
            Правильные названия столбца для цены: {true_price_title}
            Правильные названия столбца для веса: {true_mass_title}
            ''')
            raise "Не создана таблица"

        # Вывод таблицы
        print(f'Количество позиций {len(self.data)}')
        return self

    def find_text(self, text):
        '''
        Поиск по слову
        text: частичное или полное слово для поиска в столбце: Наименование
        '''
        self.input_text = text
        # Поиск в столбце: Наименование
        self.result = self.data.loc[self.data['Наименование'].str.contains(text, case=False)]
        self.result = self.result.sort_values('цена за кг.', axis=0)

        # Обработка пустого вывода
        if self.result.empty:
            print('Позиция не найдена')
            return self
        # Подгатовка к выводу на консоль и к экспорту в формате html
        self.result.insert(0, "№", [number + 1 for number in range(len(self.result))])
        print(self.result.to_string(index=False))
        return self

    def export_to_html(self, fname='output.html'):
        '''
        Создание таблицы в формате html
        fname:  название файла по умолчанию output.html
        '''
        with open(fname, 'w', encoding='utf-8') as f:
            html_table = self.result.sort_values('цена за кг.', axis=0).to_html(
                classes=["table-bordered", "table-striped", "table-hover"], index=False)
            html_output = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewporуt" content="width=device-width, initial-scale=1.0">
                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
                <style>
                td, th {{
                    padding: 7px;
                }}
            </style>
                <title>DataFrame with Bootstrap</title>
            </head>
            <body>
                <div class="container">
                    <h2>Список цен в порядке возрастания</h2>
                    <h4>Поиск по ключевому слову: {self.input_text}</h4>
                    {html_table}
                </div>
            </body>
            </html>
            """
            f.write(html_output)
            print('Экспорт завершен')


pm = PriceMachine()
pm.load_prices()

print('''
Для вывода списока всех команд введите: help
Команду ввести вместо поиска позиции
''')

'''
    Начало работы программы
'''
while True:
    text = input('Какую позицию вы ищете: ')
    if text.lower() == 'exit' or text.lower() == 'выход':
        break
    elif text.lower() == 'export' or text.lower() == 'экспорт':
        fname = input('Введите желаемое имя файла:  ')
        if fname == '':
            pm.export_to_html()
        else:
            pm.export_to_html(fname=f'{fname}.html')
    elif text.lower() == 'help' or text.lower() == 'помощь':
        print('''
            Команды на
         en           rus
        exit    или  выход   - Выйти из программы
        export  или  экспорт - Вывести результат в формате html
        help    или  помощь  - Вывод всех команд
        -------------------------------------------
        Нажать  на   enter   - Получить весь список        
        ''')
    else:
        pm.find_text(text)

'''
    Конец работы программы
'''
print('Поиск завершен')
