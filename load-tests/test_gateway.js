import http from 'k6/http';
import { check, sleep } from 'k6';

const CUSTOMER_ID = "1bd20f7b-4d5a-4c88-b68b-0971cd9d865c";

export let options = {
    stages: [
        { duration: '30s', target: 100 },
        { duration: '1m',  target: 300 },
        { duration: '30s', target: 0 },
    ],
    thresholds: {
        http_req_duration: ['p(95)<500'],
    },
};

export default function () {
    // Appel DIRECT
    let direct = http.get(
        `http://localhost:8002/v1/usage/${CUSTOMER_ID}`,
        { tags: { trajet: 'direct' } }
    );
    check(direct, { 'direct 200': (r) => r.status === 200 });

    sleep(0.05);

    // Appel via GATEWAY
    let gateway = http.get(
        `http://localhost:8080/v1/usage/${CUSTOMER_ID}`,
        { tags: { trajet: 'gateway' } }
    );
    check(gateway, { 'gateway 200': (r) => r.status === 200 });

    sleep(0.05);
}
