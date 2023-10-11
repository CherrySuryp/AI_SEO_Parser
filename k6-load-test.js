import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  vus: 5, // Количество виртуальных пользователей (VUs)
  duration: '120s', // Продолжительность теста
};

export default function () {
  let url = 'http://127.0.0.1:8000/143845628?mode=v1';

  // Заголовки запроса
  let headers = {
    'accept': 'application/json',
    'x-api-key': 'qwe',
  };

  // Выполняем GET-запрос
  let res = http.get(url, { headers: headers });

  // Проверяем, что статус-код ответа равен 200 (OK)
  check(res, {
    'status is 200': (r) => r.status === 200,
  });

  // Можно добавить дополнительные проверки, например, на содержимое ответа, если необходимо
  let randomSleep = Math.random() * 3;
  sleep(1);
}

