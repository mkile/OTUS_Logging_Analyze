import argparse
import re
import json
import os

""" 
Парсер логов
    TODO:
        топ 3 самых долгих запросов (сохранять ссылку, метод, ip, время запроса)        
"""

parser = argparse.ArgumentParser(description='Обработка логов.')
parser.add_argument('--path', dest='path', action='store', help='Путь к файлу/папке логов', required=True)
args = parser.parse_args()


def generate_report(file):
    def parse_file(file, request_type):
        ip_list = dict()
        line_num = 0  # DEBUG
        max_timeout = 0
        timeouts = list()

        print('Обрабатываем файл:', file)
        with open(file, mode='r') as log_file:
            for line in log_file.readlines():
                if len(line.strip()) == 0:
                    continue
                ip_match = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line)

                line_num += 0  # DEBUG
                if line_num > 1000:  # DEBUG
                    break  # DEBUG

                if ip_match is not None:
                    ip = ip_match.group()
                    method = re.search(r'\] \"({})'.format("|".join(request_type.keys())), str(line).upper())
                    if method is not None:
                        method = method.groups()[0]
                    else:
                        print('Не распознан метод в строке:', line)
                        method = 'OTHER METHODS'
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
                    # Get 3 longest requests
                    timeout = 0
                    try:
                        timeout = int(re.search(r'\" (\d{3,5})$', line).groups()[0])
                    except Exception as Err:
                        print('Ошибка поиска таймаута:', line)
                    if timeout > max_timeout:
                        if len(timeouts) >= 3:
                            timeouts.pop(2)
                        timeouts.insert(0, {"timeout": timeout, "ip": ip, "link": link, "method": method})
                        max_timeout = timeout
                    if ip in ip_list:
                        ip_list[ip] += 1
                    else:
                        ip_list[ip] = 1
                    request_type[method] += 1
        return ip_list, request_type, timeouts

    def pprint(header, data):
        if header != '':
            print(header)
        for key in data.keys():
            print("   ", key, ":", data[key])

    request_type = {"GET": 0,
                    "POST": 0,
                    "PUT": 0,
                    "DELETE": 0,
                    "HEAD": 0,
                    "OTHER METHODS": 0}

    ip_list, request_type, timeout_data = parse_file(file, request_type)

    if len(ip_list) == 0:
        print('Данные в файле отсутствуют.')
        return

    requests_count = 0
    for value in request_type:
        requests_count += request_type[value]

    top_ips = {}
    for ip in range(3):
        max_uses = max(ip_list.values())  # maximum value
        for k, v in ip_list.items():
            if v == max_uses:
                top_ips[k] = v
                ip_list[k] = 0
                break
    print('Общее количество запросов:', requests_count)
    pprint('Адреса с которых наиболее часто обращались:', top_ips)
    pprint('Запросы по типам:', request_type)
    print('Самые долгие запросы:')
    for line in timeout_data:
        pprint('', line)
        print('---')
    result_json = dict()
    result_json['requests_count'] = requests_count
    result_json['top_ips'] = top_ips
    result_json['requests_by_type'] = request_type
    result_json['longest_requests'] = timeout_data
    with open(os.path.basename(file) + '.json', 'w') as f:
        json.dump(result_json, f, indent=4)


if os.path.isfile(args.path):
    generate_report(args.path)
else:
    for file in os.listdir(args.path):
        generate_report(os.path.join(args.path, file))
