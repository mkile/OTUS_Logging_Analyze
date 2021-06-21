import argparse
import re
import json
import os
from functools import reduce

""" 
Парсер логов
    TODO:
        топ 3 самых долгих запросов (сохранять ссылку, метод, ip, время запроса)        
"""

parser = argparse.ArgumentParser(description='Обработка логов.')
parser.add_argument('--path', dest='path', action='store', help='Путь к файлу/папке логов', required=True)
args = parser.parse_args()


def parse_file(file, ip_list, request_type):
    # 109.184.11.34 - - [12/Dec/2015:18:32:56 +0100] "GET /administrator/ HTTP/1.1" 200 4263 "-" "Mozilla/5.0 (Windows NT 6.0; rv:34.0) Gecko/20100101 Firefox/34.0" "-"
    print('Обрабатываем файл:', file)
    with open(file, mode='r') as log_file:
        for line in log_file.readlines():
            ip_match = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line)
            if ip_match is not None:
                ip = ip_match.group()
                method = re.search(r'\] \"({})'.format("|".join(request_type.keys())), str(line).upper())
                if method is not None:
                    method = method.groups()[0]
                else:
                    print('Не найден метод в строке:', line)
                pattern = r'(?:{}).[^\"]+'.format("|".join(request_type.keys()))
                link = re.findall(pattern, str(line).upper())
                if link is not None:
                    try:
                        link = str(link[0]).split()[1]
                    except Exception as Err:
                        print('Ошибка поиска ссылки в строке:', line)
                        print('Найдено:', link)
                else:
                    print('Отсутствует ссылка в строке:', line)
                timeout = re.search(r'\" \d{4}', line)
                if ip in ip_list:
                    ip_list[ip] += 1
                else:
                    ip_list[ip] = 1
                if method in request_type.keys():
                    request_type[method] += 1
                else:
                    request_type['UNLISTED METHOD'] += 1
    return ip_list, request_type


ip_list = dict()
request_type = {"GET": 0,
                "POST": 0,
                "PUT": 0,
                "DELETE": 0,
                "HEAD": 0,
                "OPTIONS": 0,
                "PROPFIND": 0,
                "FOO": 0,
                "UNLISTED METHOD": 0,
                "OST": 0,
                "T": 0,
                "INDEX": 0,
                "SEARCH": 0,
                "TEST": 0}

if os.path.isfile(args.path):
    ip_list, request_type = parse_file(args.path, ip_list, request_type)
else:
    for file in os.listdir(args.path):
        ip_list, request_type = parse_file(os.path.join(args.path, file), ip_list, request_type)

requests_count = 0
for value in request_type:
    requests_count += request_type[value]

top_ips = []
for ip in range(3):
    max_uses = max(ip_list.values())  # maximum value
    max_ip = ''.join([k for k, v in ip_list.items() if v == max_uses])
    top_ips.append({max_ip: max_uses})
    ip_list[max_ip] = 0

print('Адреса с которых наиболее часто обращались:', top_ips)
print('Количество запросов:', requests_count)
print('Запросы по типам:', request_type)

