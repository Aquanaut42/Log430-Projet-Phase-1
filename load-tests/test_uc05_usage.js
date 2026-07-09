import http from 'k6/http';
import { check, sleep } from 'k6';
import { uuidv4 } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';

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
    let res = http.post(
        'http://localhost:8002/v1/orders',
        JSON.stringify({
            customer_id: CUSTOMER_ID,
            plan_id: 'plan-basic'
        }),
        {
            headers: {
                'Content-Type': 'application/json',
                'Idempotency-Key': uuidv4(),
            }
        }
    );
    check(res, {
        'status 201': (r) => r.status === 201,
          'latence < 500ms': (r) => r.timings.duration < 500,
    });
    sleep(0.1);
}
