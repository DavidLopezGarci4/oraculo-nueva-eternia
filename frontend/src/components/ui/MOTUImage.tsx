import React, { useState, useEffect } from 'react';

interface MOTUImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  productId?: number;
  fallbackSrc?: string;
}

export function MOTUImage({ productId, fallbackSrc = '', src, ...props }: MOTUImageProps) {
  const useLocal = localStorage.getItem('use_local_images') === 'true';
  const localUrl = productId ? `/api/static/images/${productId}.jpg` : '';
  
  const defaultSrc = src || fallbackSrc;
  const [currentSrc, setCurrentSrc] = useState(useLocal && localUrl ? localUrl : defaultSrc);

  useEffect(() => {
    setCurrentSrc(useLocal && localUrl ? localUrl : defaultSrc);
  }, [src, fallbackSrc, productId, useLocal]);

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
