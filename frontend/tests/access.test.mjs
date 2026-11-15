import test from 'node:test';
import assert from 'node:assert/strict';
import { canVisit, homeFor, errorMessage } from '../src/utils/access.ts';
test('reader cannot visit administrative and staff routes', () => {
 assert.equal(canVisit('DOC_GIA', '/users'), false);
 assert.equal(canVisit('DOC_GIA', '/borrowings'), false);
 assert.equal(canVisit('DOC_GIA', '/books/12'), true);
 assert.equal(canVisit('THU_THU', '/users'), false);
 assert.equal(canVisit('THU_THU', '/my-fines'), false);
 assert.equal(canVisit('ADMIN', '/reports'), true);
});
test('role landing and safe API validation errors', () => {
 assert.equal(homeFor('DOC_GIA'), '/books');
 assert.equal(homeFor('ADMIN'), '/dashboard');
 assert.equal(errorMessage({response:{data:{detail:'Xung đột dữ liệu'}}}), 'Xung đột dữ liệu');
 assert.equal(errorMessage({response:{data:{detail:[{msg:'bad'}]}}}), 'Không thể thực hiện. Vui lòng kiểm tra dữ liệu và thử lại.');
});
