import http from "k6/http";
import { check } from "k6";
import { Trend } from "k6/metrics";

const queries = [
  "ai",
  "robot",
  "health",
  "education",
  "science",
  "data",
  "ethics",
  "blockchain",
];

const baseUrl = "http://localhost:3000/api/v1/stories?filter=";

const responseTimeTrend = new Trend("response_time");

export const options = {
  thresholds: {
    http_req_duration: ["p(95)<200"],
    http_req_failed: ["rate<0.1"],
  },
  stages: [
    { duration: "30s", target: 2 },
    { duration: "30s", target: 5 },
    { duration: "30s", target: 0 },
  ],
};

export default function () {
  const query = queries[Math.floor(Math.random() * queries.length)];
  const url = `${baseUrl}${query}&page=1&per_page=8&order=createdAt:desc`;

  const res = http.get(url);

  responseTimeTrend.add(res.timings.duration);

  check(res, {
    "status is 200": (r) => r.status === 200,
  });
}

export function handleSummary(data) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
  const fileName = `../summaries/summary-${timestamp}.json`;

  console.log(`Saving summary to ${fileName}`);
  return {
    [fileName]: JSON.stringify(data),
  };
}
