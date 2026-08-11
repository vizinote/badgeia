const assert = require('assert');
const { describe, it } = require('node:test');
const { normalizeUrl, validateUrl, scanWithRetry } = require('../scanner');

describe('normalizeUrl', () => {
  it('ajoute https:// si absent', () => {
    assert.strictEqual(normalizeUrl('mon-site.fr'), 'https://mon-site.fr/');
  });
  it('conserve https://', () => {
    assert.strictEqual(normalizeUrl('https://example.com'), 'https://example.com/');
  });
});

describe('validateUrl', () => {
  it('rejette localhost', () => {
    assert.ok(validateUrl('http://localhost:3000'));
  });
  it('rejette IP privée', () => {
    assert.ok(validateUrl('http://192.168.1.1'));
  });
  it('accepte un domaine public', () => {
    assert.strictEqual(validateUrl('https://example.com'), null);
  });
});
