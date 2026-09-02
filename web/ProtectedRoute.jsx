import React from 'react';

/**
 * Thin auth gate.
 *
 * The app currently gates the whole shell at the App() root, so this wrapper is
 * not on the critical path — it's here for when an individual section needs its
 * own guard, e.g. a future admin-only page:
 *
 *   <ProtectedRoute authed={!!token} fallback={<LoginPage onAuthed={setToken} />}>
 *     <AdminPanel />
 *   </ProtectedRoute>
 *
 * Renders `children` when `authed` is truthy, otherwise `fallback` (default: nothing).
 */
export default function ProtectedRoute({ authed, fallback = null, children }) {
  return authed ? children : fallback;
}
