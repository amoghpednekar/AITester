import type {
  FullConfig,
  FullResult,
  Reporter,
  Suite,
  TestCase,
  TestResult,
} from '@playwright/test/reporter';

interface Counts {
  passed: number;
  failed: number;
  skipped: number;
  flaky: number;
}

function emptyCounts(): Counts {
  return { passed: 0, failed: 0, skipped: 0, flaky: 0 };
}

class SummaryReporter implements Reporter {
  private counts: Counts = emptyCounts();
  private failures: Array<{ title: string; location: string; error: string }> = [];
  private startedAt = 0;

  onBegin(_config: FullConfig, _suite: Suite): void {
    this.startedAt = Date.now();
  }

  onTestEnd(test: TestCase, result: TestResult): void {
    switch (result.status) {
      case 'passed':
        this.counts.passed += 1;
        break;
      case 'skipped':
        this.counts.skipped += 1;
        break;
      case 'failed':
      case 'timedOut':
        this.counts.failed += 1;
        this.failures.push({
          title: test.title,
          location: `${test.location.file}:${test.location.line}`,
          error: (result.error?.message ?? '').split('\n')[0],
        });
        break;
      case 'interrupted':
        break;
    }
    if (result.status === 'passed' && result.retry > 0) {
      this.counts.flaky += 1;
    }
  }

  onEnd(_result: FullResult): void {
    const durationSec = ((Date.now() - this.startedAt) / 1000).toFixed(1);
    const total = this.counts.passed + this.counts.failed + this.counts.skipped;
    const line = '='.repeat(60);
    // eslint-disable-next-line no-console
    console.log(`\n${line}`);
    // eslint-disable-next-line no-console
    console.log(`  Summary: ${total} tests in ${durationSec}s`);
    // eslint-disable-next-line no-console
    console.log(`  Passed: ${this.counts.passed} | Failed: ${this.counts.failed} | Skipped: ${this.counts.skipped} | Flaky: ${this.counts.flaky}`);
    if (this.failures.length > 0) {
      // eslint-disable-next-line no-console
      console.log(`\n  Failures:`);
      for (const failure of this.failures) {
        // eslint-disable-next-line no-console
        console.log(`    - ${failure.title} (${failure.location})\n      ${failure.error}`);
      }
    }
    // eslint-disable-next-line no-console
    console.log(line);
  }
}

export default SummaryReporter;
