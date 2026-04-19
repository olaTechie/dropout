import { describe, it, expect } from 'vitest';
import { formatNaira, formatPct, formatNumber } from './format.js';

describe('format', () => {
  it('formats Naira', () => {
    expect(formatNaira(500)).toBe('₦500');
    expect(formatNaira(1500)).toBe('₦1,500');
    expect(formatNaira(500_000_000)).toBe('₦500M');
    expect(formatNaira(1_200_000_000)).toBe('₦1.2B');
  });
  it('formats percent', () => {
    expect(formatPct(0.85)).toBe('85%');
    expect(formatPct(0.8567, 1)).toBe('85.7%');
  });
  it('formats number with commas', () => {
    expect(formatNumber(3194)).toBe('3,194');
  });
});
