import React, { createContext, useContext, useState, useCallback } from 'react';
import { GrayskullRitualOverlay } from '../components/ui/GrayskullRitualOverlay';

export interface RitualPayload {
    type: 'claim' | 'burn';
    product: {
        id: number;
        name: string;
        image_url?: string;
        sub_category?: string;
        is_vintage?: boolean;
        retail_price?: number;
    };
    onComplete?: () => void;
}

interface GrayskullRitualContextType {
    triggerRitual: (payload: RitualPayload) => void;
}

const GrayskullRitualContext = createContext<GrayskullRitualContextType | null>(null);

export const GrayskullRitualProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [currentRitual, setCurrentRitual] = useState<RitualPayload | null>(null);

    const triggerRitual = useCallback((payload: RitualPayload) => {
        setCurrentRitual(payload);
    }, []);

    const handleFinish = useCallback(() => {
        if (currentRitual?.onComplete) {
            currentRitual.onComplete();
        }
        setCurrentRitual(null);
    }, [currentRitual]);

    return (
        <GrayskullRitualContext.Provider value={{ triggerRitual }}>
            {children}
            {currentRitual && (
                <GrayskullRitualOverlay
                    ritual={currentRitual}
                    onFinish={handleFinish}
                />
            )}
        </GrayskullRitualContext.Provider>
    );
};

export const useGrayskullRitual = () => {
    const context = useContext(GrayskullRitualContext);
    if (!context) {
        throw new Error('useGrayskullRitual debe usarse dentro de un GrayskullRitualProvider');
    }
    return context;
};
