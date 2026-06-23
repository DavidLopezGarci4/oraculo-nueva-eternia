import React, { useState, useEffect } from 'react';

interface MOTUImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  productId?: number;
  fallbackSrc?: string;
}

export function MOTUImage({ productId, fallbackSrc = '', src, ...props }: MOTUImageProps) {
  const useLocal = localStorage.getItem('use_local_images') === 'true';
  const defaultSrc = src || fallbackSrc;
  const localSrc = productId ? `/api/static/images/${productId}.webp` : defaultSrc;
  const [currentSrc, setCurrentSrc] = useState(useLocal ? localSrc : defaultSrc);

  useEffect(() => {
    let active = true;
    let objectUrl: string | null = null;

    const resolveImage = async () => {
      if (!productId) {
        if (active) setCurrentSrc(defaultSrc);
        return;
      }

      const cacheKey = `/api/static/images/${productId}.webp`;

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

          // If it's not in the cache, display the local static image first,
          // then download and save it to the cache in the background.
          if (active) setCurrentSrc(cacheKey);

          // Asynchronously fetch and cache it from the local static directory
          fetch(cacheKey)
            .then(async (response) => {
              if (response.ok) {
                const cacheToPut = await caches.open('motu-image-cache');
                await cacheToPut.put(cacheKey, response);
              }
            })
            .catch((err) => {
              console.warn(`Auto-caching failed for product ${productId}:`, err);
            });
        } catch (e) {
          console.error("Cache API resolution failed:", e);
          if (active) setCurrentSrc(cacheKey);
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
    const localStaticUrl = `/api/static/images/${productId}.webp`;
    if (currentSrc !== localStaticUrl && productId) {
      // Intentar primero ver si está en la caché del navegador para máxima rapidez
      caches.open('motu-image-cache')
        .then((cache) => cache.match(localStaticUrl))
        .then((cachedResponse) => {
          if (cachedResponse) {
            cachedResponse.blob().then((blob) => {
              const objectUrl = URL.createObjectURL(blob);
              setCurrentSrc(objectUrl);
            });
          } else {
            // Si no está en la caché del navegador, cargar desde el servidor de estáticos
            setCurrentSrc(localStaticUrl);
          }
        })
        .catch((err) => {
          console.warn("Error recuperando de caché del navegador en handleError:", err);
          setCurrentSrc(localStaticUrl);
        });
    } else if (currentSrc !== defaultSrc) {
      // Si falla el servidor de estáticos local, probar la URL remota por si acaso
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
