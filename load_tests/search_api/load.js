import http from 'k6/http';
import { sleep, check } from 'k6';
import { Trend, Rate, Counter } from 'k6/metrics';
import { SharedArray } from 'k6/data';

// Custom metrics
const searchLatency = new Trend('search_latency');
const failRate = new Rate('failed_requests');
const successfulSearches = new Counter('successful_searches');

// Configure the test
export const options = {
  stages: [
    { duration: '5s', target: 10 }, // Ramp-up to 10 users
    { duration: '20s', target: 50 }, // Ramp-up to 50 users
    { duration: '30s', target: 50 }, // Stay at 50 users for 30s
    { duration: '5s', target: 0 }, // Ramp-down to 0 users
  ],
  thresholds: {
    'search_latency': ['p95<500'], // 95% of requests should be below 500ms
    'failed_requests': ['rate<0.1'], // Less than 10% of requests should fail
    'http_req_duration': ['p95<500'], // 95% of requests should be below 500ms
  },
};

// Define popular search terms (20% of queries that drive 80% of traffic)
// Using intent-based queries for popular items
const popularSearchTerms = new SharedArray('popularSearches', function() {
  return [
    'best budget smartphone 2025',
    'lightweight laptop for students',
    'wireless headphones with long battery life',
    'affordable 4k smart tv',
  ];
});

// Define long-tail search terms (80% of queries that drive 20% of traffic)
// Using intent-based queries that reflect real user search behavior
const longTailSearchTerms = new SharedArray('longTailSearches', function() {
  return [
    'best wireless mouse for fps gaming',
    'quietest mechanical keyboard with rgb for night gaming',
    'affordable curved ultrawide monitor for productivity',
    'headphones for airplane travel with noise cancellation',
    'most powerful gaming laptop under $2000',
    'energy efficient smart refrigerator with family hub',
    'waterproof speaker for pool parties',
    'best value 4k oled tv for movie watching',
    'smart watch that tracks sleep and heart rate',
    'robot vacuum for pet hair on carpets',
    'healthiest air fryer for family of four',
    'office chair for back pain relief',
    'fastest external ssd for video editing',
    'wifi system for large house with thick walls',
    'portable power station for camping trips',
    'doorbell camera with package theft detection',
  ];
});

// Helper function to select search terms with 20/80 distribution
function getSearchTerm() {
  // 80% of the time, use a popular search term
  if (Math.random() < 0.8) {
    return popularSearchTerms[Math.floor(Math.random() * popularSearchTerms.length)];
  } else {
    // 20% of the time, use a long-tail search term
    return longTailSearchTerms[Math.floor(Math.random() * longTailSearchTerms.length)];
  }
}

// Headers
const headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  // Add your authentication token if needed
  // 'Authorization': 'Bearer YOUR_API_TOKEN',
};

export default function() {
  // Select a search term
  const searchTerm = getSearchTerm();
  
  // Define the URL with the search term as a query parameter
  // Replace with your actual API endpoint
  const url = `https://your-laravel-api.com/api/products/search?q=${encodeURIComponent(searchTerm)}`;
  
  // Additional parameters - modify as needed for your API
  const params = {
    page: 1,
    per_page: 20,
    sort_by: 'relevance',
  };
  
  // Make the HTTP request
  const response = http.get(url, { headers: headers, tags: { name: 'SearchAPI' } });
  
  // Check if the request was successful
  const success = check(response, {
    'status is 200': (r) => r.status === 200,
    'response contains products': (r) => {
      const body = JSON.parse(r.body);
      return body.data && Array.isArray(body.data);
    },
  });
  
  // Record metrics
  searchLatency.add(response.timings.duration);
  failRate.add(!success);
  
  if (success) {
    successfulSearches.add(1);
  }
  
  // Sleep between requests to simulate real user behavior
  sleep(Math.random() * 3 + 1); // Random sleep between 1-4 seconds
}

// Add a teardown function to log a summary at the end of the test
export function teardown() {
  console.log('Load test completed.');
}