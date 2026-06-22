"use client";

import { useEffect, useMemo, useState } from "react";

import { apiBaseUrl } from "@/config/navigation";
import type { EmojiListPayload, EmojiMapping } from "@/types/system";

type EmojiTextPart =
  | { type: "text"; value: string }
  | { type: "emoji"; mapping: EmojiMapping };

let emojiCache: EmojiMapping[] | null = null;
let emojiPromise: Promise<EmojiMapping[]> | null = null;

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

async function fetchEmojiMappings() {
  if (emojiCache) return emojiCache;
  if (!emojiPromise) {
    emojiPromise = fetch(`${apiBaseUrl}/system/emojis?enabled_only=true`, { cache: "no-store" })
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json() as Promise<EmojiListPayload>;
      })
      .then((payload) => {
        emojiCache = payload.emojis ?? [];
        return emojiCache;
      })
      .catch(() => {
        emojiCache = [];
        return emojiCache;
      });
  }
  return emojiPromise;
}

export function tokenizeCommentText(text: string, mappings: EmojiMapping[]): EmojiTextPart[] {
  const enabledMappings = mappings.filter((item) => item.is_enabled && item.emoji_code && item.emoji_value);
  if (!text || !enabledMappings.length) return [{ type: "text", value: text }];

  const mappingByCode = new Map(enabledMappings.map((item) => [item.emoji_code, item]));
  const pattern = enabledMappings
    .map((item) => item.emoji_code)
    .sort((a, b) => b.length - a.length)
    .map(escapeRegExp)
    .join("|");
  const matcher = new RegExp(`(${pattern})`, "g");
  const parts: EmojiTextPart[] = [];
  let cursor = 0;

  for (const match of text.matchAll(matcher)) {
    const code = match[0];
    const index = match.index ?? 0;
    if (index > cursor) parts.push({ type: "text", value: text.slice(cursor, index) });
    const mapping = mappingByCode.get(code);
    parts.push(mapping ? { type: "emoji", mapping } : { type: "text", value: code });
    cursor = index + code.length;
  }

  if (cursor < text.length) parts.push({ type: "text", value: text.slice(cursor) });
  return parts.length ? parts : [{ type: "text", value: text }];
}

export function CommentTextWithEmojis({ text, className = "" }: { text: string; className?: string }) {
  const [mappings, setMappings] = useState<EmojiMapping[]>(emojiCache ?? []);

  useEffect(() => {
    let isCancelled = false;
    fetchEmojiMappings().then((items) => {
      if (!isCancelled) setMappings(items);
    });
    return () => {
      isCancelled = true;
    };
  }, []);

  const parts = useMemo(() => tokenizeCommentText(text, mappings), [mappings, text]);

  return (
    <span className={className}>
      {parts.map((part, index) => {
        if (part.type === "text") return <span key={`${part.value}-${index}`}>{part.value}</span>;
        const mapping = part.mapping;
        if (mapping.emoji_type === "image") {
          return (
            <img
              key={`${mapping.emoji_code}-${index}`}
              src={mapping.emoji_value}
              alt={mapping.display_name || mapping.emoji_code}
              title={mapping.display_name || mapping.emoji_code}
              className="mx-0.5 inline h-[18px] w-[18px] align-[-3px] object-contain"
            />
          );
        }
        return (
          <span key={`${mapping.emoji_code}-${index}`} title={mapping.display_name || mapping.emoji_code} className="mx-0.5 inline-block align-[-1px]">
            {mapping.emoji_value}
          </span>
        );
      })}
    </span>
  );
}
