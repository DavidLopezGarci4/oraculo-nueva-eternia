import React, { useState, useEffect } from 'react';

interface MOTUImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  productId?: number;
  fallbackSrc?: string;
}

const MAX_BLOB_CACHE_SIZE = 150;
const globalBlobUrlMap = new Map<string, string>();
let motuCachePromise: Promise<Cache> | null = null;

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
  const cacheKey = productId ? `/api/static/images/${productId}.webp` : null;

  // 1. Synchronous initial state check from in-memory RAM cache or direct static endpoint
  const [currentSrc, setCurrentSrc] = useState<string>(() => {
    if (productId && cacheKey && imageSource !== 'supabase') {
      const inMemoryUrl = globalBlobUrlMap.get(cacheKey);
      if (inMemoryUrl) {
        return inMemoryUrl;
      }
      if (imageSource === 'local_cache') {
        return `${cacheKey}?source=cache`;
      } else if (imageSource === 'custom_path') {
        return `${cacheKey}?source=custom`;
      }
    }
    return defaultSrc;
  });

  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    let active = true;

    const resolveImage = async () => {
      if (!productId || !cacheKey) {
        if (active) setCurrentSrc(defaultSrc);
        return;
      }

      if (imageSource !== 'supabase') {
        const cachedInMemory = globalBlobUrlMap.get(cacheKey);
        if (cachedInMemory) {
          if (active) setCurrentSrc(cachedInMemory);
          return;
        }

        const srcParam = imageSource === 'custom_path' ? 'custom' : 'cache';
        const fetchUrl = `${cacheKey}?source=${srcParam}`;

        try {
          const cachePromise = getMotuCache();
          if (cachePromise) {
            const cache = await cachePromise;
            const cachedResponse = await cache.match(cacheKey);

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

        // Rely on native browser HTTP cache (Cache-Control: max-age=604800) with a single <img> request
        if (active) setCurrentSrc(fetchUrl);
      } else {
        if (active) setCurrentSrc(defaultSrc);
      }
    };

    resolveImage();

    return () => {
      active = false;
    };
  }, [src, fallbackSrc, productId, imageSource, defaultSrc, cacheKey]);

  const handleError = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
    if (!productId || !cacheKey) {
      if (props.onError) props.onError(e);
      return;
    }

    const cacheFallbackUrl = `${cacheKey}?source=cache`;
    if (currentSrc !== cacheFallbackUrl && currentSrc !== cacheKey) {
      setCurrentSrc(cacheFallbackUrl);
    } else if (currentSrc !== defaultSrc) {
      setCurrentSrc(defaultSrc);
    } else if (props.onError) {
      props.onError(e);
    }
  };

  return (
    <img
      loading="lazy"
      decoding="async"
      {...props}
      src={currentSrc}
      onError={handleError}
      onLoad={(e) => {
        setIsLoaded(true);
        if (props.onLoad) props.onLoad(e);
      }}
      className={`transition-opacity duration-300 ${isLoaded ? 'opacity-100' : 'opacity-85'} ${className}`}
    />
  );
}
