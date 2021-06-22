# OTUS_Logging_Analyze
Анализ лога веб-сервера

Используется для анализа файлов логов в формате:<br>
%h %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\" %D<br>
%h - имя удаленного хоста<br>
%t - время получения запроса<br>
%r - тип запроса, его содержимое и версия<br>
%s - код состояния HTTP<br>
%b - количество отданных сервером байт<br>
%{Referer} - URL-источник запроса<br>
%{User-Agent} - HTTP-заголовок, содержащий информацию о запросе<br>
%D - длительность запроса в микросекундах<br>

<h3>Использование:</h3> 
    python parser.py --path "путь к файлу или папке с файлами логов"<br>

После выполнения сохраняет для каждого обработанного файла логов в папке со скриптом файл json,
содержащий следующую информацию:<br>
    общее количество выполненных запросов<br>
    количество запросов по типу: GET - 20, POST - 10 и т.п.<br>
    топ 3 IP адресов, с которых были сделаны запросы<br>
    топ 3 самых долгих запросов, должно быть видно метод, url, ip, время запроса
