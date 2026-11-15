// Runs in front of every page on Cloudflare Pages. It serves the page exactly
// as built, then records the visit in the background (analytics/log.js).
// Images, the stylesheet and the data files are excluded in _routes.json and
// never reach this.
//
// Rows go to the same D1 database as ryanbwatt.com, labelled with SITE, and
// are read at ryanbwatt.com/admin. This site has no report page of its own.
//
// If the D1 binding `DB` is missing, or the write fails, the reader gets the
// same page either way: logging can never break the site.

import { logVisit, shouldLog } from "../analytics/log.js";

const SITE = "art-moves";

export async function onRequest(context) {
  const response = await context.next();
  try {
    if (context.env.DB && shouldLog(context.request, response)) {
      context.waitUntil(logVisit(context.env.DB, context.request, SITE).catch(() => {}));
    }
  } catch {
    // Never let logging affect the response.
  }
  return response;
}
