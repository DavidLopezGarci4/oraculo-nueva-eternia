import React, { useRef, useState } from 'react';

interface FoilTiltCardProps {
    children: React.ReactNode;
    className?: string;
    isSpecial: boolean;
}

export const FoilTiltCard: React.FC<FoilTiltCardProps> = ({ children, className = '', isSpecial }) => {
    const cardRef = useRef<HTMLDivElement>(null);
    const [isHovered, setIsHovered] = useState(false);

    const premiumEffects = localStorage.getItem('motu_premium_effects') !== 'false';

    const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
        if (!premiumEffects || !cardRef.current) return;
        const card = cardRef.current;
        const rect = card.getBoundingClientRect();
        
        // Local coordinates relative to the card dimensions (-0.5 to 0.5)
        const x = (e.clientX - rect.left) / rect.width - 0.5;
        const y = (e.clientY - rect.top) / rect.height - 0.5;
        
        // Max tilt of 12 degrees for visual comfort
        const rotX = -y * 24;
        const rotY = x * 24;
        const foilX = ((e.clientX - rect.left) / rect.width) * 100;
        const foilY = ((e.clientY - rect.top) / rect.height) * 100;

        card.style.setProperty('--rx', `${rotX.toFixed(2)}deg`);
        card.style.setProperty('--ry', `${rotY.toFixed(2)}deg`);
        card.style.setProperty('--fx', `${foilX.toFixed(1)}%`);
        card.style.setProperty('--fy', `${foilY.toFixed(1)}%`);
        card.style.setProperty('--foil-angle', `${(rotX + rotY * 2).toFixed(1)}deg`);
    };

    const handleMouseEnter = () => {
        setIsHovered(true);
        if (cardRef.current) {
            cardRef.current.style.setProperty('--scale', '1.02');
            cardRef.current.style.transition = 'none';
        }
    };

    const handleMouseLeave = () => {
        setIsHovered(false);
        if (cardRef.current) {
            cardRef.current.style.transition = 'transform 0.5s cubic-bezier(0.25, 1, 0.5, 1), box-shadow 0.5s ease';
            cardRef.current.style.setProperty('--rx', '0deg');
            cardRef.current.style.setProperty('--ry', '0deg');
            cardRef.current.style.setProperty('--scale', '1');
            cardRef.current.style.setProperty('--fx', '50%');
            cardRef.current.style.setProperty('--fy', '50%');
            cardRef.current.style.setProperty('--foil-angle', '0deg');
        }
    };

    // 3D Tilt perspective transform style using hardware-accelerated CSS variables
    const transformStyle: React.CSSProperties = premiumEffects ? {
        transform: 'perspective(1000px) rotateX(var(--rx, 0deg)) rotateY(var(--ry, 0deg)) scale3d(var(--scale, 1), var(--scale, 1), var(--scale, 1))',
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
                        background: 'radial-gradient(circle at var(--fx, 50%) var(--fy, 50%), rgba(255, 255, 255, 0.4) 0%, rgba(234, 179, 8, 0.15) 30%, rgba(14, 165, 233, 0.1) 60%, transparent 100%), linear-gradient(var(--foil-angle, 0deg), rgba(234, 179, 8, 0.3) 0%, rgba(139, 92, 246, 0.2) 50%, rgba(14, 165, 233, 0.3) 100%)',
                    }}
                />
            )}
        </div>
    );
};
