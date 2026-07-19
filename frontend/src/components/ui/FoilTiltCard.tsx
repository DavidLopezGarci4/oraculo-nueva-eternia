import React, { useRef, useState } from 'react';

interface FoilTiltCardProps {
    children: React.ReactNode;
    className?: string;
    isSpecial: boolean;
}

export const FoilTiltCard: React.FC<FoilTiltCardProps> = ({ children, className = '', isSpecial }) => {
    const cardRef = useRef<HTMLDivElement>(null);
    const [rotateX, setRotateX] = useState(0);
    const [rotateY, setRotateY] = useState(0);
    const [foilX, setFoilX] = useState(50);
    const [foilY, setFoilY] = useState(50);
    const [isHovered, setIsHovered] = useState(false);

    const premiumEffects = localStorage.getItem('motu_premium_effects') !== 'false';

    const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
        if (!premiumEffects) return;
        if (!cardRef.current) return;
        const card = cardRef.current;
        const rect = card.getBoundingClientRect();
        
        // Local coordinates relative to the card dimensions (-0.5 to 0.5)
        const x = (e.clientX - rect.left) / rect.width - 0.5;
        const y = (e.clientY - rect.top) / rect.height - 0.5;
        
        // Max tilt of 12 degrees for visual comfort
        setRotateX(-y * 24);
        setRotateY(x * 24);

        // Foil gradient position (0% to 100%)
        setFoilX((e.clientX - rect.left) / rect.width * 100);
        setFoilY((e.clientY - rect.top) / rect.height * 100);
    };

    const handleMouseEnter = () => {
        setIsHovered(true);
    };

    const handleMouseLeave = () => {
        setIsHovered(false);
        setRotateX(0);
        setRotateY(0);
    };

    // 3D Tilt perspective transform style
    const transformStyle = premiumEffects ? {
        transform: isHovered 
            ? `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)` 
            : 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)',
        transition: isHovered ? 'none' : 'transform 0.5s cubic-bezier(0.25, 1, 0.5, 1), box-shadow 0.5s ease',
    } : {};

    return (
        <div
            ref={cardRef}
            onMouseMove={handleMouseMove}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            style={transformStyle}
            className={`relative overflow-hidden ${className}`}
        >
            {children}
            
            {/* Holographic shimmer effect layer */}
            {isSpecial && isHovered && premiumEffects && (
                <div 
                    className="absolute inset-0 pointer-events-none mix-blend-color-dodge z-30 opacity-30 transition-opacity duration-300"
                    style={{
                        background: `radial-gradient(circle at ${foilX}% ${foilY}%, rgba(255, 255, 255, 0.4) 0%, rgba(234, 179, 8, 0.15) 30%, rgba(14, 165, 233, 0.1) 60%, transparent 100%), linear-gradient(${rotateX + rotateY * 2}deg, rgba(234, 179, 8, 0.3) 0%, rgba(139, 92, 246, 0.2) 50%, rgba(14, 165, 233, 0.3) 100%)`,
                    }}
                />
            )}
        </div>
    );
};
