import React, { useState, useEffect } from 'react';

interface MOTUImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  productId?: number;
  fallbackSrc?: string;
}

export function MOTUImage({ productId, fallbackSrc = '', src, ...props }: MOTUImageProps) {
  const imageSource = localStorage.getItem('image_source') || 'supabase';
  const defaultSrc = src || fallbackSrc;
  
  let initialSrc = defaultSrc;
  if (productId) {
    if (imageSource === 'local_cache') {
      initialSrc = `/api/static/images/${productId}.webp?source=cache`;
    } else if (imageSource === 'custom_path') {
      initialSrc = `/api/static/images/${productId}.webp?source=custom`;
    }
  }

  const [currentSrc, setCurrentSrc] = useState(initialSrc);

  useEffect(() => {
    let active = true;
    let objectUrl: string | null = null;

    const resolveImage = async () => {
      if (!productId) {
        if (active) setCurrentSrc(defaultSrc);
        return;
      }

      const cacheKey = `/api/static/images/${productId}.webp`;

      if (imageSource !== 'supabase') {
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

          const srcParam = imageSource === 'custom_path' ? 'custom' : 'cache';
          const fetchUrl = `${cacheKey}?source=${srcParam}`;
          if (active) setCurrentSrc(fetchUrl);

          // Asynchronously fetch and cache it from the local static directory
          fetch(fetchUrl)
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
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [src, fallbackSrc, productId, imageSource, defaultSrc]);

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
