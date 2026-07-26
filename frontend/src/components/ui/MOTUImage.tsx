import React, { useState, useEffect } from 'react';

interface MOTUImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  productId?: number;
  fallbackSrc?: string;
}

const globalBlobUrlMap = new Map<string, string>();
let motuCachePromise: Promise<Cache> | null = null;

export function clearMOTURAMCache() {
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

  // 1. Synchronous initial state check from in-memory RAM cache for 0ms instant loading
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
        // If already cached in RAM, use it immediately
        const cachedInMemory = globalBlobUrlMap.get(cacheKey);
        if (cachedInMemory) {
          if (active) setCurrentSrc(cachedInMemory);
          return;
        }

        try {
          const cachePromise = getMotuCache();
          if (cachePromise) {
            const cache = await cachePromise;
            const cachedResponse = await cache.match(cacheKey);

            if (cachedResponse) {
              const blob = await cachedResponse.blob();
              const objectUrl = URL.createObjectURL(blob);
              globalBlobUrlMap.set(cacheKey, objectUrl);
              if (active) setCurrentSrc(objectUrl);
              return;
            }
          }

          const srcParam = imageSource === 'custom_path' ? 'custom' : 'cache';
          const fetchUrl = `${cacheKey}?source=${srcParam}`;
          if (active) setCurrentSrc(fetchUrl);

          // Asynchronously fetch and cache it from local backend
          fetch(fetchUrl)
            .then(async (response) => {
              if (response.ok) {
                const cache = await getMotuCache();
                if (cache) {
                  await cache.put(cacheKey, response.clone());
                  const blob = await response.blob();
                  const objectUrl = URL.createObjectURL(blob);
                  globalBlobUrlMap.set(cacheKey, objectUrl);
                  if (active) setCurrentSrc(objectUrl);
                }
              }
            })
            .catch((err) => {
              console.warn(`Auto-caching failed for product ${productId}:`, err);
            });
        } catch (e) {
          console.error("Cache API resolution failed:", e);
          const srcParam = imageSource === 'custom_path' ? 'custom' : 'cache';
          if (active) setCurrentSrc(`${cacheKey}?source=${srcParam}`);
        }
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

    if (currentSrc !== cacheKey) {
      // Retry via static backend route
      setCurrentSrc(cacheKey);
    } else if (currentSrc !== defaultSrc) {
      // Fallback to default remote URL
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
