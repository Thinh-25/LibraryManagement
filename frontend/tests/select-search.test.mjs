import test from 'node:test';
import assert from 'node:assert/strict';
import { filterSelectOption } from '../src/utils/selectSearch.ts';

test('dropdown search matches Vietnamese labels without accents and without case sensitivity', () => {
  assert.equal(filterSelectOption('  van HOC ', {label:'Văn học',value:2}),true);
  assert.equal(filterSelectOption('doc gia', {label:'Độc giả',value:'DOC_GIA'}),true);
  assert.equal(filterSelectOption('dang muon', {label:'Đang mượn',value:'BORROWED'}),true);
  assert.equal(filterSelectOption('khong ton tai', {label:'Văn học',value:2}),false);
});

test('dropdown search handles identifiers, clear search and missing options', () => {
  assert.equal(filterSelectOption('bc0002', {label:'BC0002 · Kệ A1',value:7}),true);
  assert.equal(filterSelectOption('', {label:'Tất cả'}),true);
  assert.equal(filterSelectOption('test',undefined),false);
});
