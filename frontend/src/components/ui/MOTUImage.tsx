import React, { useState, useEffect, useMemo, useRef } from 'react';

interface MOTUImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  productId?: number;
  fallbackSrc?: string;
}

const MAX_BLOB_CACHE_SIZE = 150;
const globalBlobUrlMap = new Map<string, string>();
let motuCachePromise: Promise<Cache> | null = null;

function isMixedContentHttp(url: string): boolean {
  return (
    typeof window !== 'undefined' &&
    window.location.protocol === 'https:' &&
    url.toLowerCase().startsWith('http://')
  );
}

function getSupabaseJpgSibling(url: string): string {
  if (!url) return '';
  const qIndex = url.indexOf('?');
  const pathPart = qIndex === -1 ? url : url.slice(0, qIndex);
  const queryPart = qIndex === -1 ? '' : url.slice(qIndex);
  if (
    pathPart.includes('/storage/v1/object/public/motu-catalog/') &&
    pathPart.toLowerCase().endsWith('.webp')
  ) {
    return `${pathPart.slice(0, -5)}.jpg${queryPart}`;
  }
  return '';
}

function buildCandidateUrls(
  imageSource: string,
  cacheKey: string | null,
  defaultSrc: string
): string[] {
  const normalizedDefaultSrc =
    defaultSrc && !isMixedContentHttp(defaultSrc) ? defaultSrc : '';
  const supabaseJpgSibling = getSupabaseJpgSibling(normalizedDefaultSrc);
  const cacheUrl = cacheKey ? `${cacheKey}?source=cache` : '';
  const customUrl = cacheKey ? `${cacheKey}?source=custom` : '';

  const rawOrder =
    imageSource === 'custom_path'
      ? [customUrl, cacheUrl, normalizedDefaultSrc, supabaseJpgSibling]
      : imageSource === 'local_cache'
        ? [cacheUrl, normalizedDefaultSrc, supabaseJpgSibling]
        : [normalizedDefaultSrc, supabaseJpgSibling, cacheUrl];

  const seen = new Set<string>();
  const deduped: string[] = [];
  for (const url of rawOrder) {
    if (url && !seen.has(url)) {
      seen.add(url);
      deduped.push(url);
    }
  }
  return deduped;
}

function setBlobCache(key: string, url: string) {
  const existing = globalBlobUrlMap.get(key);
  if (existing) {
    if (existing !== url) {
      try { URL.revokeObjectURL(url); } catch { /* ignore */ }
    }
    return existing;
  }
  if (globalBlobUrlMap.size >= MAX_BLOB_CACHE_SIZE) {
    const oldestKey = globalBlobUrlMap.keys().next().value;
    if (oldestKey) {
      const oldestUrl = globalBlobUrlMap.get(oldestKey);
      if (oldestUrl) {
        try { URL.revokeObjectURL(oldestUrl); } catch { /* ignore */ }
      }
      globalBlobUrlMap.delete(oldestKey);
    }
  }
  globalBlobUrlMap.set(key, url);
  return url;
}

export function clearMOTURAMCache() {
  for (const url of globalBlobUrlMap.values()) {
    try {
      URL.revokeObjectURL(url);
    } catch {
      /* ignore */
    }
  }
  globalBlobUrlMap.clear();
}

const getMotuCache = () => {
  if (!motuCachePromise && typeof window !== 'undefined' && 'caches' in window) {
    motuCachePromise = caches.open('motu-image-cache');
  }
  return motuCachePromise;
};

export function MOTUImage({ productId, fallbackSrc = '', src, className = '', ...props }: MOTUImageProps) {
  const imageSource = typeof window !== 'undefined' ? (localStorage.getItem('image_source') || 'supabase') : 'supabase';
  const defaultSrc = src || fallbackSrc;
  const cacheKey = productId ? `/api/static/images/${productId}` : null;
  const legacyCacheKey = productId ? `/api/static/images/${productId}.webp` : null;

  const candidates = useMemo(
    () => buildCandidateUrls(imageSource, cacheKey, defaultSrc),
    [imageSource, cacheKey, defaultSrc]
  );

  // 1. Synchronous initial state check from in-memory RAM cache or first finite candidate
  const [currentSrc, setCurrentSrc] = useState<string>(() => {
    if (productId && cacheKey && imageSource !== 'supabase') {
      const inMemoryUrl = globalBlobUrlMap.get(cacheKey);
      if (inMemoryUrl) {
        return inMemoryUrl;
      }
    }
    return candidates[0] || '';
  });

  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const triedSourcesRef = useRef<Set<string>>(new Set());

  useEffect(() => {
    let active = true;
    triedSourcesRef.current = new Set();
    setHasError(false);
    setIsLoaded(false);

    const resolveImage = async () => {
      if (!productId || !cacheKey) {
        const first = candidates[0] || '';
        if (active) {
          setCurrentSrc(first);
          if (!first) setHasError(true);
        }
        return;
      }

      if (imageSource !== 'supabase') {
        const cachedInMemory = globalBlobUrlMap.get(cacheKey);
        if (cachedInMemory) {
          if (active) setCurrentSrc(cachedInMemory);
          return;
        }

        try {
          const cachePromise = getMotuCache();
          if (cachePromise) {
            const cache = await cachePromise;
            const cachedResponse =
              (await cache.match(cacheKey)) ||
              (legacyCacheKey ? await cache.match(legacyCacheKey) : undefined);

            if (cachedResponse) {
              const existingBlobUrl = globalBlobUrlMap.get(cacheKey);
              if (existingBlobUrl) {
                if (active) setCurrentSrc(existingBlobUrl);
                return;
              }
              const blob = await cachedResponse.blob();
              const objectUrl = setBlobCache(cacheKey, URL.createObjectURL(blob));
              if (active) setCurrentSrc(objectUrl);
              return;
            }
          }
        } catch (e) {
          console.error("Cache API resolution failed:", e);
        }
      }

      const first = candidates[0] || '';
      if (active) {
        setCurrentSrc(first);
        if (!first) setHasError(true);
      }
    };

    resolveImage();

    return () => {
      active = false;
    };
  }, [src, fallbackSrc, productId, imageSource, cacheKey, legacyCacheKey, candidates]);

  const handleError = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
    if (currentSrc) {
      triedSourcesRef.current.add(currentSrc);
    }

    const nextUrl = candidates.find((candidate) => !triedSourcesRef.current.has(candidate));
    if (nextUrl) {
      setCurrentSrc(nextUrl);
      return;
    }

    setHasError(true);
    if (props.onError) {
      props.onError(e);
    }
  };

  if (hasError || !currentSrc) {
    return (
      <div
        role="img"
        aria-label={props.alt || 'Sin Imagen'}
        className={`flex items-center justify-center bg-black/50 italic text-white/25 text-[10px] sm:text-xs font-black uppercase tracking-widest select-none ${className}`}
      >
        Sin Imagen
      </div>
    );
  }

  return (
    <img
      loading="lazy"
      decoding="async"
      {...props}
      referrerPolicy={props.referrerPolicy ?? 'no-referrer'}
      src={currentSrc}
      onError={handleError}
      onLoad={(e) => {
        setIsLoaded(true);
        setHasError(false);
        if (props.onLoad) props.onLoad(e);
      }}
      className={`transition-opacity duration-300 ${isLoaded ? 'opacity-100' : 'opacity-85'} ${className}`}
    />
  );
}
