// plural(5, ["трек", "трека", "треков"]) -> "треков"
export function plural(n, forms) {
  const a = Math.abs(n) % 100, b = a % 10;
  if (a > 10 && a < 20) return forms[2];
  if (b > 1 && b < 5) return forms[1];
  if (b === 1) return forms[0];
  return forms[2];
}
export const tracksWord = n => `${n} ${plural(n, ["трек", "трека", "треков"])}`;
export const authorLink = name => `/author?name=${encodeURIComponent(name)}`;
export const tagLink = name => `/tags?tag=${encodeURIComponent(name)}`;

// Сервер отдаёт время в UTC без суффикса "Z" — добавляем, иначе браузер сочтёт его локальным
export function parseUtc(s) {
  if (!s) return null;
  return new Date(/[zZ]|[+-]\d\d:?\d\d$/.test(s) ? s : s + "Z");
}
export function formatDate(s) {
  const d = parseUtc(s);
  return d ? d.toLocaleDateString("ru-RU", {day: "numeric", month: "long", year: "numeric"}) : "";
}
export function timeAgo(s) {
  const d = parseUtc(s);
  if (!d) return "";
  const sec = Math.max(0, Math.floor((Date.now() - d.getTime()) / 1000));
  if (sec < 60) return "только что";
  if (sec < 3600) return `${Math.floor(sec / 60)} мин назад`;
  if (sec < 86400) return `${Math.floor(sec / 3600)} ч назад`;
  if (sec < 7 * 86400) return `${Math.floor(sec / 86400)} дн назад`;
  return d.toLocaleDateString("ru-RU");
}
