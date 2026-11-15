import test from 'node:test';
import assert from 'node:assert/strict';
import { validateCoverFile, resolveImageUrl } from '../src/utils/images.ts';

test('cover file accepts supported MIME types up to 5 MiB and rejects other content', () => {
  for (const type of ['image/jpeg', 'image/png', 'image/webp']) {
    assert.equal(validateCoverFile({ type, size: 5 * 1024 * 1024 }), null);
  }
  assert.ok(validateCoverFile({ type: 'image/png', size: 5 * 1024 * 1024 + 1 }));
  assert.ok(validateCoverFile({ type: 'image/svg+xml', size: 40 }));
  assert.ok(validateCoverFile({ type: '', size: 40 }));
  assert.ok(validateCoverFile({ type: 'image/png', size: 0 }));
});

test('image URL uses API origin for generated media and preserves external images', () => {
  const base = 'http://localhost:8001/api/v1';
  const path = '/media/covers/0123456789abcdef0123456789abcdef.webp';
  assert.equal(resolveImageUrl(path, base), `http://localhost:8001${path}`);
  assert.equal(resolveImageUrl('https://images.example/book.png', base), 'https://images.example/book.png');
  assert.equal(resolveImageUrl('http://images.example/book.jpg', base), 'http://images.example/book.jpg');
  for (const invalid of [null, '', 'javascript:alert(1)', '//other/cover.png', '/media/covers/../secret', '/other/image']) {
    assert.equal(resolveImageUrl(invalid, base), undefined);
  }
});
