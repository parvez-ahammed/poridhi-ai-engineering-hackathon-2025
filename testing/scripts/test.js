import http from "k6/http";
import { check } from "k6";
import { Trend, Rate } from "k6/metrics";

// Array of search queries to test the API with
const queries = [
  "a",
  "b",
  "c",
  "d",
  "e",
  "f",
  "g",
  "h",
  "i",
  "j",
  "k",
  "l",
  "m",
  "n",
  "o",
  "p",
  "q",
  "r",
  "s",
  "t",
  "u",
  "v",
  "w",
  "x",
  "y",
  "z",
];

const BASE_URL = "http://localhost:8080/search?q=";
const responseTimeTrend = new Trend("response_time");
const successRate = new Rate("http_req_success");

// Test configuration: VUs, stages, and thresholds
export const options = {
  stages: [
    { duration: "5s", target: 2 }, // Ramp-up to 2 VUs in 5 seconds
    { duration: "5s", target: 5 }, // Ramp-up to 5 VUs in 5 seconds
    { duration: "5s", target: 0 }, // Ramp-down to 0 VUs in 5 seconds
  ],
};

// setup() function runs once before the test starts
export function setup() {
  console.log("Setup: Initializing test environment");
  return { baseUrl: BASE_URL }; // Returning base URL to be used in VUs
}

// Default function to run for each virtual user (VU)
export default function (data) {
  const baseUrl = data.baseUrl;
  const query = queries[Math.floor(Math.random() * queries.length)];
  const url = `${baseUrl}${query}`;

  // Send GET request and measure the response times
  const res = http.get(url);

  // Track key response timings
  responseTimeTrend.add(res.timings.duration); // Total response time

  // Track the success rate of requests
  successRate.add(res.status === 200);

  // Check if the response status is 200 (OK)
  check(res, {
    "status is 200": (r) => r.status === 200,
  });
}

// Teardown function runs once after the test ends
export function teardown() {
  console.log("Teardown: Cleaning up after the test");
}

// handleSummary() function to handle the final summary after the test run
export function handleSummary(data) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
  const fileName = `../summaries/summary-${timestamp}.json`;

  console.log(`Saving summary to ${fileName}`);
  return {
    [fileName]: JSON.stringify(data), // Save summary as a JSON file
  };
}
