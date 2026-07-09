import http from 'k6/http';
import { check, sleep } from 'k6';

const CUSTOMER_ID = "1bd20f7b-4d5a-4c88-b68b-0971cd9d865c";

export let options = {
    stages: [
        { duration: '30s', target: 50 },
        { duration: '1m',  target: 200 },
        { duration: '30s', target: 600 },
        { duration: '30s', target: 0 },
    ],
    thresholds: {
        http_req_duration: ['p(95)<500'],
        http_req_failed:   ['rate<0.05'],
    },
};

export default function () {
    let res = http.get(
        `http://localhost:8002/v1/usage/${CUSTOMER_ID}`
    );
    check(res, {
        'status 200': (r) => r.status === 200,
          'latence < 500ms': (r) => r.timings.duration < 500,
    });
    sleep(0.1);
}
