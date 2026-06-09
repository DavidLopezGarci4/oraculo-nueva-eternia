import React, { useState, useEffect } from 'react';

interface MOTUImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  productId?: number;
  fallbackSrc?: string;
}

export function MOTUImage({ productId, fallbackSrc = '', src, ...props }: MOTUImageProps) {
  const useLocal = localStorage.getItem('use_local_images') === 'true';
  const defaultSrc = src || fallbackSrc;
  const [currentSrc, setCurrentSrc] = useState(defaultSrc);

  useEffect(() => {
    let active = true;
    let objectUrl: string | null = null;

    const resolveImage = async () => {
      if (!productId) {
        if (active) setCurrentSrc(defaultSrc);
        return;
      }

      const cacheKey = `/api/static/images/${productId}.jpg`;

      if (useLocal) {
        try {
          const cache = await caches.open('motu-image-cache');
          const cachedResponse = await cache.match(cacheKey);
          
          if (cachedResponse) {
            const blob = await cachedResponse.blob();
            if (active) {
              objectUrl = URL.createObjectURL(blob);
              setCurrentSrc(objectUrl);
            }
            return;
          }

          // If it's not in the cache, display the remote image first,
          // then download and save it to the cache in the background.
          if (active) setCurrentSrc(defaultSrc);

          if (defaultSrc) {
            // Asynchronously fetch and cache it
            fetch(defaultSrc)
              .then(async (response) => {
                if (response.ok) {
                  const cacheToPut = await caches.open('motu-image-cache');
                  await cacheToPut.put(cacheKey, response);
                }
              })
              .catch((err) => {
                console.warn(`Auto-caching failed for product ${productId}:`, err);
              });
          }
        } catch (e) {
          console.error("Cache API resolution failed:", e);
          if (active) setCurrentSrc(defaultSrc);
        }
      } else {
        if (active) setCurrentSrc(defaultSrc);
      }
    };

    resolveImage();

    return () => {
      active = false;
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [src, fallbackSrc, productId, useLocal, defaultSrc]);

  const handleError = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
    // Si falla al cargar la imagen local, cambiar a la remota
    if (currentSrc !== defaultSrc) {
      setCurrentSrc(defaultSrc);
    } else if (props.onError) {
      props.onError(e);
    }
  };

  return (
    <img
      {...props}
      src={currentSrc}
      onError={handleError}
    />
  );
}
