import test from 'node:test';
import assert from 'node:assert/strict';
import { useSession } from '../src/stores/session.ts';
test('session exists only in memory and clear removes user and bearer token', () => {
 const user={id:1,ho_ten:'Độc giả',email:'reader@example.com',so_dien_thoai:null,vai_tro:'DOC_GIA',trang_thai:true,must_change_password:false};
 assert.equal(useSession.getState().token,null);
 useSession.getState().setSession('test-token',user);
 assert.equal(useSession.getState().user.id,1);
 assert.equal(useSession.getState().token,'test-token');
 useSession.getState().clear();
 assert.equal(useSession.getState().token,null);
 assert.equal(useSession.getState().user,null);
});
