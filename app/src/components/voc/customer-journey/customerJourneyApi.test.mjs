import assert from 'node:assert/strict';
import fs from 'node:fs';

const source = fs.readFileSync(new URL('../../../lib/customer-journey-api.ts', import.meta.url), 'utf8');

assert.match(source, /getJourneyOverview/);
assert.match(source, /getJourneyMatrix/);
assert.match(source, /getJourneyTouchpoints/);
assert.match(source, /getJourneyPainpoints/);
assert.doesNotMatch(source, /mock/i);
assert.doesNotMatch(source, /fallback/i);

console.log('customer journey api tests passed');
