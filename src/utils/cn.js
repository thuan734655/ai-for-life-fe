import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Kết hợp nhiều class Tailwind linh hoạt, ưu tiên class cuối cùng
 * @param  {...any} inputs
 * @returns {string}
 */
export function cn(...inputs) {
  return twMerge(clsx(...inputs));
}
