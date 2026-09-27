import { defineConfig, devices } from '@playwright/test'

// No env-var branching here on purpose: this config has one job, which is to run the
// primary-surface suite against a dev server on a fixed strict port. A CI runner that
// needs different behaviour passes flags rather than reading the environment, so the
// file type-checks under the app's own tsconfig without pulling in Node globals.
const PORT = 5312

export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  retries: 0,
  workers: 1,
  reporter: [['list']],
  // The first run pays for Vite's dependency optimisation; 30s is not enough for it.
  timeout: 90_000,
  use: {
    baseURL: `http://localhost:${PORT}`,
    colorScheme: 'light',
    viewport: { width: 1440, height: 950 },
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: {
    command: `npx vite --port ${PORT} --strictPort`,
    url: `http://localhost:${PORT}/`,
    reuseExistingServer: true,
    timeout: 120_000,
  },
})
