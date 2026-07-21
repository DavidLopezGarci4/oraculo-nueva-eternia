import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { AnimatePresence } from 'framer-motion';
import {
    Flame,
    Trash2,
    RefreshCcw,
    Search,
    CheckCircle2,
    X,
    LayoutGrid,
    LayoutList
} from 'lucide-react';
import { getPurgatory, discardItem, discardItemsBulk, matchVintageItem, matchMiscellaneousItem, matchItemsBulk } from '../api/purgatory';

import QuickPreviewModal from '../components/QuickPreviewModal';
import { useModalA11y } from '../hooks/useModalA11y';
import PowerSwordLoader from '../components/ui/PowerSwordLoader';
import SwipeCard from '../components/purgatory/SwipeCard';
import ForensicModal from '../components/purgatory/ForensicModal';
import VintageClassifyModal from '../components/purgatory/VintageClassifyModal';
import PurgatoryListView from '../components/purgatory/PurgatoryListView';
import axios from 'axios';
import { useEffect, useRef, useMemo } from 'react';

const PERSISTENCE_KEY = 'purgatory_offline_actions';

const Purgatory: React.FC = React.memo(() => {
    const queryClient = useQueryClient();
    const [searchTerm, setSearchTerm] = useState('');
    const [manualSearchTerm, setManualSearchTerm] = useState('');
    const [selectedPendingId, setSelectedPendingId] = useState<number | null>(null);
    const [isVintageModalOpen, setIsVintageModalOpen] = useState(false);
    // Fase AAA-3c: foco/Escape/role=dialog accesibles para el modal de clasificacion.
    const vintageModalRef = useRef<HTMLDivElement>(null);
    useModalA11y(isVintageModalOpen, () => setIsVintageModalOpen(false), vintageModalRef);
    const [selectedDivision, setSelectedDivision] = useState<'vintage' | 'modern'>('vintage');
    const [customSubCategory, setCustomSubCategory] = useState('Origins');
    const [showCustomSubCategoryInput, setShowCustomSubCategoryInput] = useState(false);
    const [vintageModalItemId, setVintageModalItemId] = useState<number | null>(null);
    const [vintageModalItemName, setVintageModalItemName] = useState('');
    const [vintageCustomName, setVintageCustomName] = useState('');
    const [selectedVintageProductId, setSelectedVintageProductId] = useState<number | null>(null);
    const [pendingActions, setPendingActions] = useState<any[]>(() => {
        const saved = localStorage.getItem(PERSISTENCE_KEY);
        return saved ? JSON.parse(saved) : [];
    });

    // Locally processed/synced IDs that should remain hidden until the server refetch completes
    const [locallyProcessedIds, setLocallyProcessedIds] = useState<Set<number>>(new Set());

    // UX/UI Custom States
    const [viewLayout, setViewLayout] = useState<'mazo' | 'lista'>('mazo');
    const [sortBy, setSortBy] = useState<'newest' | 'oldest' | 'highest_match' | 'lowest_match'>('highest_match');
    const [shopFilter, setShopFilter] = useState<string>('all');
    const [deckItems, setDeckItems] = useState<any[]>([]);
    const [snoozedIds, setSnoozedIds] = useState<number[]>([]);
    const [associatedProductId, setAssociatedProductId] = useState<number | null>(null);
    const [isSearchingAssociation, setIsSearchingAssociation] = useState(false);

    // Experimental Transit Filter State
    const [enableTransitFilter, setEnableTransitFilter] = useState(false);
    const [transitType, setTransitType] = useState<'all' | 'retail' | 'p2p'>('all');

    // Pagination State
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 15;
    const [showForensic, setShowForensic] = useState(false);
    // Fase AAA-3c: foco/Escape/role=dialog accesibles para el modal forense.
    const forensicModalRef = useRef<HTMLDivElement>(null);
    useModalA11y(showForensic, () => setShowForensic(false), forensicModalRef);

    const [previewUrl, setPreviewUrl] = useState<string | null>(null);

    const [selectedIds, setSelectedIds] = useState<number[]>([]);

    // Persistence Persistence
    useEffect(() => {
        localStorage.setItem(PERSISTENCE_KEY, JSON.stringify(pendingActions));
    }, [pendingActions]);

    const openClassifyModal = (itemId: number, scrapedName: string) => {
        setVintageModalItemId(itemId);
        setVintageModalItemName(scrapedName);
        setVintageCustomName('');
        setSelectedVintageProductId(null);
        setSelectedDivision('vintage');
        setCustomSubCategory('Origins');
        setShowCustomSubCategoryInput(false);
        setIsVintageModalOpen(true);
    };



    // Mutations
    const discardBulkMutation = useMutation({
        mutationFn: async (ids: number[]) => {
            return ids;
        },
        onMutate: async (ids) => {
            // Find names/urls for forensic context
            const affectedItems = queryClient.getQueryData<any[]>(['purgatory'])?.filter(i => ids.includes(i.id)) || [];

            // Persistence: Add to local buffer immediately
            setPendingActions(prev => {
                if (prev.some(a => a.type === 'bulk-discard' && JSON.stringify(a.pendingIds) === JSON.stringify(ids))) {
                    return prev;
                }
                return [...prev, {
                    id: Date.now(),
                    type: 'bulk-discard',
                    pendingIds: ids,
                    items: affectedItems.map(i => ({ id: i.id, name: i.scraped_name, url: i.url })),
                    timestamp: new Date().toISOString()
                }];
            });

            await queryClient.cancelQueries({ queryKey: ['purgatory'] });
            const previousItems = queryClient.getQueryData(['purgatory']);
            // Optimistically update the cache
            queryClient.setQueryData(['purgatory'], (old: any) =>
                (old || []).filter((item: any) => !ids.includes(item.id))
            );
            return { previousItems };
        },
        onError: (err, _variables, context: any) => {
            queryClient.setQueryData(['purgatory'], context.previousItems);
            console.error('Bulk discard enqueue failed:', err);
        },
        onSuccess: () => {
            // Background worker handles syncing
        },
        onSettled: () => {
            setSelectedIds([]);
        }
    });

    // Queries
    const { data: pendingItems, isLoading: isLoadingPending } = useQuery({
        queryKey: ['purgatory'],
        queryFn: getPurgatory,
        refetchInterval: 300000 // 5 min — evita refrescos constantes que estropean la UX
    });

    // Clean up locallyProcessedIds once the server data updates (confirming deletion/archive)
    useEffect(() => {
        if (pendingItems) {
            const currentItemIds = new Set(pendingItems.map((item: any) => item.id));
            setLocallyProcessedIds(prev => {
                const next = new Set<number>();
                prev.forEach((id: number) => {
                    if (currentItemIds.has(id)) {
                        next.add(id);
                    }
                });
                if (next.size !== prev.size) {
                    return next;
                }
                return prev;
            });
        }
    }, [pendingItems]);

    const { data: products } = useQuery({
        queryKey: ['products-purgatory'],
        queryFn: async () => {
            const response = await axios.get('/api/products');
            return response.data;
        }
    });

    const { data: vintageProducts } = useQuery({
        queryKey: ['vintage-unique-products'],
        queryFn: async () => {
            const response = await axios.get('/api/products?is_vintage=true');
            return response.data;
        }
    });

    useEffect(() => {
        if (vintageCustomName.trim()) {
            const list = selectedDivision === 'vintage' ? vintageProducts : products;
            const match = (list || []).find((p: any) => p.name.toLowerCase() === vintageCustomName.trim().toLowerCase());
            if (match) {
                setSelectedVintageProductId(match.id);
            } else {
                setSelectedVintageProductId(null);
            }
        } else {
            setSelectedVintageProductId(null);
        }
    }, [selectedDivision, vintageCustomName, products, vintageProducts]);


    const discardMutation = useMutation({
        mutationFn: async (id: number) => {
            return id;
        },
        onMutate: async (id) => {
            const item = queryClient.getQueryData<any[]>(['purgatory'])?.find(i => i.id === id);

            setPendingActions(prev => {
                if (prev.some(a => a.type === 'discard' && a.pendingIds.includes(id))) {
                    return prev;
                }
                return [...prev, {
                    id: Date.now(),
                    type: 'discard',
                    pendingIds: [id],
                    scrapedName: item?.scraped_name,
                    action_url: item?.url,
                    timestamp: new Date().toISOString()
                }];
            });

            await queryClient.cancelQueries({ queryKey: ['purgatory'] });
            const previousItems = queryClient.getQueryData(['purgatory']);
            queryClient.setQueryData(['purgatory'], (old: any) =>
                (old || []).filter((item: any) => item.id !== id)
            );
            return { previousItems };
        },
        onError: (err, _id, context: any) => {
            queryClient.setQueryData(['purgatory'], context.previousItems);
            console.error('Discard enqueue failed:', err);
        },
        onSuccess: () => {
            // Background worker handles syncing
        }
    });

    const matchMutation = useMutation({
        mutationFn: async ({ pendingId, productId }: { pendingId: number, productId: number }) => {
            return { pendingId, productId };
        },
        onMutate: async ({ pendingId, productId }) => {
            const item = queryClient.getQueryData<any[]>(['purgatory'])?.find(i => i.id === pendingId);

            setPendingActions(prev => {
                if (prev.some(a => a.type === 'match' && a.pendingIds.includes(pendingId))) {
                    return prev;
                }
                return [...prev, {
                    id: Date.now(),
                    type: 'match',
                    pendingIds: [pendingId],
                    productId,
                    scrapedName: item?.scraped_name,
                    action_url: item?.url,
                    timestamp: new Date().toISOString()
                }];
            });

            await queryClient.cancelQueries({ queryKey: ['purgatory'] });
            const previousItems = queryClient.getQueryData(['purgatory']);
            queryClient.setQueryData(['purgatory'], (old: any) =>
                (old || []).filter((item: any) => item.id !== pendingId)
            );
            return { previousItems };
        },
        onError: (err, _variables, context: any) => {
            queryClient.setQueryData(['purgatory'], context.previousItems);
            console.error('Match enqueue failed:', err);
        },
        onSuccess: () => {
            setSelectedPendingId(null);
            setManualSearchTerm('');
        }
    });

    const matchVintageMutation = useMutation({
        mutationFn: async ({ pendingId, customName, productId, isVintage, subCategory }: { pendingId: number, customName?: string, productId?: number, isVintage: boolean, subCategory?: string }) => {
            return { pendingId, customName, productId, isVintage, subCategory };
        },
        onMutate: async ({ pendingId, customName, productId, isVintage, subCategory }) => {
            const item = queryClient.getQueryData<any[]>(['purgatory'])?.find(i => i.id === pendingId);

            setPendingActions(prev => [...prev, {
                id: Date.now(),
                type: 'match-vintage',
                pendingIds: [pendingId],
                customName,
                productId,
                isVintage,
                subCategory,
                scrapedName: item?.scraped_name,
                action_url: item?.url,
                timestamp: new Date().toISOString()
            }]);

            await queryClient.cancelQueries({ queryKey: ['purgatory'] });
            const previousItems = queryClient.getQueryData(['purgatory']);
            queryClient.setQueryData(['purgatory'], (old: any) =>
                (old || []).filter((item: any) => item.id !== pendingId)
            );
            return { previousItems };
        },
        onError: (err, _variables, context: any) => {
            queryClient.setQueryData(['purgatory'], context.previousItems);
            console.error('Vintage match enqueue failed:', err);
        },
        onSuccess: () => {
            setSelectedPendingId(null);
            setIsVintageModalOpen(false);
        }
    });

    const matchMiscMutation = useMutation({
        mutationFn: async (pendingId: number) => {
            return pendingId;
        },
        onMutate: async (pendingId) => {
            const item = queryClient.getQueryData<any[]>(['purgatory'])?.find(i => i.id === pendingId);
            setPendingActions(prev => [...prev, {
                id: Date.now(),
                type: 'match-misc',
                pendingIds: [pendingId],
                scrapedName: item?.scraped_name,
                action_url: item?.url,
                timestamp: new Date().toISOString()
            }]);
            await queryClient.cancelQueries({ queryKey: ['purgatory'] });
            const previousItems = queryClient.getQueryData(['purgatory']);
            queryClient.setQueryData(['purgatory'], (old: any) =>
                (old || []).filter((item: any) => item.id !== pendingId)
            );
            return { previousItems };
        },
        onError: (err, _variables, context: any) => {
            queryClient.setQueryData(['purgatory'], context.previousItems);
            console.error('Miscellaneous match enqueue failed:', err);
        },
        onSuccess: () => {
            setSelectedPendingId(null);
            setIsVintageModalOpen(false);
        }
    });

    // Atajo de teclado 'V' para abrir la modal de vinculación Vintage del item seleccionado
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            const target = e.target as HTMLElement;
            if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA')) {
                return;
            }

            if (selectedPendingId !== null && (e.key === 'v' || e.key === 'V')) {
                e.preventDefault();
                const item = (pendingItems || []).find((i: any) => i.id === selectedPendingId);
                if (item) {
                    openClassifyModal(item.id, item.scraped_name);
                }
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [selectedPendingId, pendingItems]);


    // Forensic Failures State
    const [failedActions, setFailedActions] = useState<any[]>(() => {
        const saved = localStorage.getItem('purgatory_sync_failures');
        return saved ? JSON.parse(saved) : [];
    });

    useEffect(() => {
        localStorage.setItem('purgatory_sync_failures', JSON.stringify(failedActions));
    }, [failedActions]);

    // Background Sync Engine (Refined Phase 31 - Non-blocking & Forensic)
    const isSyncing = useRef(false);

    useEffect(() => {
        if (pendingActions.length === 0 || isSyncing.current) return;

        const syncPending = async () => {
            if (isSyncing.current || pendingActions.length === 0) return;
            isSyncing.current = true;

            const failedIds = new Set(failedActions.map(f => f.action.id));
            const actionsToProcess = [...pendingActions].filter(a => !failedIds.has(a.id));

            if (actionsToProcess.length === 0) {
                isSyncing.current = false;
                return;
            }

            // 1. Group 'match' actions to send in bulk
            const matchActions = actionsToProcess.filter(a => a.type === 'match');
            if (matchActions.length > 0) {
                const batch = matchActions.slice(0, 20);
                const batchIds = batch.map(a => a.id);
                try {
                    const matchesPayload = batch.map(a => ({
                        pending_id: a.pendingIds[0],
                        product_id: a.productId
                    }));
                    await matchItemsBulk(matchesPayload);

                    // Add processed IDs to locallyProcessedIds
                    setLocallyProcessedIds(prev => {
                        const next = new Set(prev);
                        batch.flatMap(a => a.pendingIds).forEach((id: number) => next.add(id));
                        return next;
                    });

                    // Remove from pendingActions
                    setPendingActions(prev => prev.filter(a => !batchIds.includes(a.id)));
                    queryClient.invalidateQueries({ queryKey: ['purgatory'] });
                    queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
                    queryClient.invalidateQueries({ queryKey: ['products'] });
                } catch (err: any) {
                    console.error('Bulk match sync failed:', err);
                    const errorMessage = err.response?.data?.detail || err.message || 'Unknown Error';
                    // Mark all actions in this batch as failed
                    setFailedActions(prev => {
                        const newFailures = [...prev];
                        for (const action of batch) {
                            if (!newFailures.some(f => f.action.id === action.id)) {
                                newFailures.push({
                                    action,
                                    error: errorMessage,
                                    timestamp: new Date().toISOString(),
                                    url: action.action_url || null,
                                    productId: action.productId || null
                                });
                            }
                        }
                        return newFailures;
                    });
                }
                isSyncing.current = false;
                return;
            }

            // 2. Process non-match actions (e.g. discard, vintage, misc) one by one
            const otherAction = actionsToProcess[0];
            try {
                if (otherAction.type === 'discard') {
                    await discardItem(otherAction.pendingIds[0]);
                } else if (otherAction.type === 'bulk-discard') {
                    await discardItemsBulk(otherAction.pendingIds);
                } else if (otherAction.type === 'match-vintage') {
                    const isV = otherAction.isVintage !== false;
                    await matchVintageItem(otherAction.pendingIds[0], otherAction.customName, otherAction.productId, isV, otherAction.subCategory);
                } else if (otherAction.type === 'match-misc') {
                    await matchMiscellaneousItem(otherAction.pendingIds[0]);
                }

                // Add processed IDs to locallyProcessedIds
                setLocallyProcessedIds(prev => {
                    const next = new Set(prev);
                    otherAction.pendingIds.forEach((id: number) => next.add(id));
                    return next;
                });

                // Remove from pendingActions
                setPendingActions(prev => prev.filter(a => a.id !== otherAction.id));
                queryClient.invalidateQueries({ queryKey: ['purgatory'] });
                if (otherAction.type === 'match-vintage' || otherAction.type === 'match-misc') {
                    queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
                    queryClient.invalidateQueries({ queryKey: ['vintage-products'] });
                    queryClient.invalidateQueries({ queryKey: ['vintage-unique-products'] });
                    queryClient.invalidateQueries({ queryKey: ['products'] });
                    queryClient.invalidateQueries({ queryKey: ['products-purgatory'] });
                    queryClient.invalidateQueries({ queryKey: ['vintage-miscellaneous'] });
                }
            } catch (err: any) {
                console.error(`Sync failed for action type ${otherAction.type}:`, otherAction.id, err);
                const errorMessage = err.response?.data?.detail || err.message || 'Unknown Error';
                setFailedActions(prev => {
                    if (prev.some(f => f.action.id === otherAction.id)) return prev;
                    return [...prev, {
                        action: otherAction,
                        error: errorMessage,
                        timestamp: new Date().toISOString(),
                        url: otherAction.action_url || null,
                        productId: otherAction.productId || null
                    }];
                });
            }

            isSyncing.current = false;
        };

        const interval = setInterval(syncPending, 4000); // Process queue every 4 seconds
        const initialTimeout = setTimeout(syncPending, 1000); // Fast initial run

        return () => {
            clearInterval(interval);
            clearTimeout(initialTimeout);
        };
    }, [pendingActions.length, failedActions.length]); // Re-run mainly to ensure the check continues


    const filteredProducts = (products || [])?.filter((p: any) =>
        !p.is_vintage && (
            (p.name || "").toLowerCase().includes((manualSearchTerm || "").toLowerCase()) ||
            (p.figure_id || "").toLowerCase().includes((manualSearchTerm || "").toLowerCase())
        )
    ).slice(0, 20);

    const handleInputChange = (val: string) => {
        setVintageCustomName(val);
        const list = selectedDivision === 'vintage' ? vintageProducts : products;
        const match = (list || []).find((p: any) => p.name.toLowerCase() === val.trim().toLowerCase());
        if (match) {
            setSelectedVintageProductId(match.id);
        } else {
            setSelectedVintageProductId(null);
        }
    };

    const selectedVintagePendingItem = (pendingItems || []).find((i: any) => i.id === vintageModalItemId);
    const vintageOracleSuggestions = selectedVintagePendingItem?.suggestions?.filter((sug: any) => 
        selectedDivision === 'vintage' ? sug.is_vintage === true : sug.is_vintage !== true
    ) || [];

    const vintageModalSuggestionsToDisplay = vintageCustomName.trim()
        ? (selectedDivision === 'vintage' ? vintageProducts || [] : products || [])
            .filter((p: any) => p.name.toLowerCase().includes(vintageCustomName.toLowerCase()))
            .slice(0, 5)
        : (vintageOracleSuggestions.length > 0
            ? vintageOracleSuggestions.map((sug: any) => ({
                id: sug.product_id,
                name: sug.name,
                figure_id: sug.figure_id,
                sub_category: sug.sub_category,
                reason: sug.reason,
                match_score: sug.match_score
            }))
            : (selectedDivision === 'vintage' ? vintageProducts || [] : products || []).slice(0, 5)
        );

    // Dynamic Filter for Pending Items (Main List)
    const pendingIdsToHide = new Set([
        ...pendingActions.flatMap(a => a.pendingIds),
        ...Array.from(locallyProcessedIds)
    ]);

    const filteredPendingItems = (pendingItems || []).filter((item: any) => {
        // Persistence Ghost Mode: Filter out locally hidden items
        if (pendingIdsToHide.has(item.id)) return false;

        const term = (searchTerm || "").toLowerCase();
        const matchesSearch = !searchTerm || (
            (item.scraped_name || "").toLowerCase().includes(term) ||
            (item.shop_name || "").toLowerCase().includes(term) ||
            (item.ean || "").toLowerCase().includes(term) ||
            item.id.toString().includes(term)
        );

        // ALWAYS keep the selected item visible so they don't lose context while matching
        if (item.id === selectedPendingId) return true;

        let matchesTransit = true;
        if (enableTransitFilter) {
            if (transitType === 'retail') {
                matchesTransit = item.source_type === 'Retail';
            } else if (transitType === 'p2p') {
                matchesTransit = item.source_type === 'Peer-to-Peer';
            }
        }

        return matchesSearch && matchesTransit;
    });

    // --- SORTING AND FILTERING FOR DECK & LIST ---
    const sortedAndFilteredItems = useMemo(() => {
        let items = [...filteredPendingItems];

        // 1. Filtrar por Tienda
        if (shopFilter !== 'all') {
            items = items.filter(i => i.shop_name?.toLowerCase() === shopFilter.toLowerCase());
        }

        // 2. Ordenación
        items.sort((a, b) => {
            const getBestScore = (item: any) => {
                if (!item.suggestions || item.suggestions.length === 0) return 0;
                const scores = item.suggestions.filter((s: any) => !s.is_vintage).map((s: any) => s.match_score || 0);
                return scores.length > 0 ? Math.max(...scores) : 0;
            };

            if (sortBy === 'newest') {
                return new Date(b.found_at).getTime() - new Date(a.found_at).getTime();
            } else if (sortBy === 'oldest') {
                return new Date(a.found_at).getTime() - new Date(b.found_at).getTime();
            } else if (sortBy === 'highest_match') {
                return getBestScore(b) - getBestScore(a);
            } else if (sortBy === 'lowest_match') {
                return getBestScore(a) - getBestScore(b);
            }
            return 0;
        });

        return items;
    }, [filteredPendingItems, sortBy, shopFilter]);

    // Sincronizar deckItems localmente de forma que conserve re-encolados
    const filteredHash = sortedAndFilteredItems.map(i => i.id).join(',');

    useEffect(() => {
        // Ordenar sortedAndFilteredItems de tal manera que los IDs en snoozedIds vayan al final
        const reordered = [...sortedAndFilteredItems].sort((a, b) => {
            const indexA = snoozedIds.indexOf(a.id);
            const indexB = snoozedIds.indexOf(b.id);
            
            if (indexA !== -1 && indexB !== -1) {
                return indexA - indexB; // Ambos snoozed, conservar orden de snooze
            }
            if (indexA !== -1) return 1; // a va al final
            if (indexB !== -1) return -1; // b va al final
            return 0; // Conservar orden relativo original
        });
        setDeckItems(reordered);
    }, [filteredHash, snoozedIds]);

    // Sincronizar la asociación por defecto con el primer item de la pila
    useEffect(() => {
        if (deckItems.length > 0) {
            const currentItem = deckItems[0];
            const firstSug = currentItem.suggestions?.filter((s: any) => !s.is_vintage)?.[0];
            setAssociatedProductId(firstSug ? firstSug.product_id : null);
        } else {
            setAssociatedProductId(null);
        }
        setIsSearchingAssociation(false);
        setManualSearchTerm('');
    }, [deckItems[0]?.id]);

    // Handlers para las Acciones del Mazo
    const handleApproveCard = (item: any) => {
        let prodId = associatedProductId;
        if (!prodId) {
            const sug = item.suggestions?.filter((s: any) => !s.is_vintage)?.[0];
            if (sug) prodId = sug.product_id;
        }

        if (!prodId) {
            alert('Vincule un producto del catálogo antes de aprobar.');
            setIsSearchingAssociation(true);
            setTimeout(() => {
                document.getElementById(`assoc-search-${item.id}`)?.focus();
            }, 50);
            return;
        }

        matchMutation.mutate({ pendingId: item.id, productId: prodId });
        setSnoozedIds(prev => prev.filter(id => id !== item.id));
        setDeckItems(prev => prev.filter(i => i.id !== item.id));
        setAssociatedProductId(null);
        setIsSearchingAssociation(false);
    };

    const handleDiscardCard = (item: any) => {
        discardMutation.mutate(item.id);
        setSnoozedIds(prev => prev.filter(id => id !== item.id));
        setDeckItems(prev => prev.filter(i => i.id !== item.id));
        setAssociatedProductId(null);
        setIsSearchingAssociation(false);
    };

    const handleSwipeDown = (item: any) => {
        setSnoozedIds(prev => {
            const filtered = prev.filter(id => id !== item.id);
            return [...filtered, item.id];
        });
        setAssociatedProductId(null);
        setIsSearchingAssociation(false);
    };

    // Keyboard controls listener for deck curating
    useEffect(() => {
        if (viewLayout !== 'mazo' || deckItems.length === 0) return;
        const currentItem = deckItems[0];

        const handleKeyDown = (e: KeyboardEvent) => {
            const target = e.target as HTMLElement;
            if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA')) {
                if (e.key === 'Escape') {
                    setIsSearchingAssociation(false);
                    target.blur();
                }
                return;
            }

            if (e.key === 'd' || e.key === 'D' || e.key === 'ArrowRight') {
                e.preventDefault();
                handleApproveCard(currentItem);
            } else if (e.key === 'a' || e.key === 'A' || e.key === 'ArrowLeft') {
                e.preventDefault();
                handleDiscardCard(currentItem);
            } else if (e.key === 's' || e.key === 'S' || e.key === 'ArrowDown') {
                e.preventDefault();
                handleSwipeDown(currentItem);
            } else if (e.key === 'n' || e.key === 'N' || e.key === 'ArrowUp') {
                e.preventDefault();
                openClassifyModal(currentItem.id, currentItem.scraped_name);
            } else if (e.key === 'e' || e.key === 'E') {
                e.preventDefault();
                setIsSearchingAssociation(true);
                setTimeout(() => {
                    document.getElementById(`assoc-search-${currentItem.id}`)?.focus();
                }, 50);
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [viewLayout, deckItems, associatedProductId]);

    // Dynamic list of unique shops in pending items for filter pills
    const uniqueShopsInPending = useMemo(() => {
        return Array.from(new Set((pendingItems || []).map((i: any) => i.shop_name).filter(Boolean))) as string[];
    }, [pendingItems]);

    // Pagination Logic (Lista tradicional)
    const totalItems = sortedAndFilteredItems.length;
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const paginatedItems = sortedAndFilteredItems.slice(startIndex, startIndex + itemsPerPage);

    // Ensure we don't stay on an empty page after items are matched/discarded
    if (currentPage > 1 && paginatedItems.length === 0 && totalItems > 0) {
        setCurrentPage(Math.max(1, totalPages));
    }

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-2 md:space-y-3 animate-in fade-in duration-700">
            {/* Header / Purgatory Status */}
            <div className="relative overflow-hidden rounded-2xl md:rounded-3xl border border-white/5 bg-black/25 p-4 md:p-6 backdrop-blur-2xl shadow-2xl">
                <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-brand-primary/10 blur-[100px] pointer-events-none"></div>

                <div className="relative flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                    <div className="relative z-10 flex flex-col gap-1">
                        <div className="flex items-center gap-2 text-brand-primary">
                            <Flame className="h-3 w-3 md:h-4 md:w-4" />
                            <h2 className="text-sm md:text-base font-black uppercase tracking-[0.2em] text-white">
                                <span className="text-brand-primary">Purgatorio</span>
                            </h2>
                            {!isLoadingPending && pendingItems && pendingItems.length > 0 && (
                                <div className="ml-2 flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-brand-primary/10 border border-brand-primary/20 animate-in zoom-in-95 duration-500">
                                    <div className="h-1.5 w-1.5 rounded-full bg-brand-primary animate-pulse"></div>
                                    <span className="text-[10px] font-black uppercase tracking-widest text-brand-primary">
                                        {pendingItems.length}
                                    </span>
                                </div>
                            )}
                        </div>
                        <p className="max-w-xl text-[11px] md:text-sm text-white/65 font-medium uppercase tracking-[0.1em]">
                            Purifica las reliquias para manifestarlas en el catálogo
                        </p>
                    </div>

                    {/* Persistence Sync Indicator (Condensed) */}
                    {pendingActions.length > 0 && (
                        <div className="flex items-center gap-6 px-6 py-4 rounded-3xl bg-brand-primary/10 border border-brand-primary/20 animate-in slide-in-from-right-4 duration-500 backdrop-blur-md">
                            <div className="space-y-1">
                                <p className="text-[10px] font-black uppercase tracking-widest text-brand-primary leading-none">
                                    Sincronización {isSyncing.current ? 'Activa' : 'Pendiente'}
                                </p>
                                <p className="text-[11px] font-bold text-white/50">{pendingActions.length} acciones restantes</p>
                                <div className="flex items-center gap-4">
                                    <button onClick={() => setShowForensic(true)} className="text-[9px] font-black uppercase tracking-widest text-brand-primary hover:text-white transition-colors">Forensics</button>
                                    <button
                                        onClick={() => {
                                            if (confirm('¿Limpiar el búfer local? Esto cancelará las acciones no sincronizadas.')) {
                                                setPendingActions([]);
                                                setLocallyProcessedIds(new Set());
                                                setFailedActions([]);
                                                localStorage.removeItem(PERSISTENCE_KEY);
                                                localStorage.removeItem('purgatory_sync_failures');
                                            }
                                        }}
                                        className="text-[9px] font-black uppercase tracking-widest text-red-500/40 hover:text-red-400 transition-colors"
                                    >
                                        Limpiar
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>




            {/* Global Search Bar */}
            <div className={`space-y-6 transition-all duration-500 ${selectedPendingId ? 'opacity-20 grayscale pointer-events-none' : 'opacity-100'}`}>

                {/* Search Bar */}
                <div className="relative group">
                    <div className="absolute inset-y-0 left-6 flex items-center pointer-events-none">
                        <Search className={`h-5 w-5 transition-colors ${searchTerm ? 'text-brand-primary' : 'text-white/20'}`} />
                    </div>
                    <input
                        type="text"
                        placeholder="Buscar reliquia en el abismo por nombre, tienda, EAN o ID..."
                        value={searchTerm}
                        onChange={(e) => {
                            setSearchTerm(e.target.value);
                            setCurrentPage(1);
                        }}
                        className="w-full bg-white/[0.02] border border-white/5 hover:border-white/10 focus:border-brand-primary/50 focus:bg-white/[0.04] rounded-3xl py-6 pl-16 pr-16 text-white placeholder:text-white/20 outline-none transition-all text-sm font-bold shadow-2xl"
                    />
                    {searchTerm && (
                        <button
                            onClick={() => setSearchTerm('')}
                            className="absolute inset-y-0 right-6 flex items-center text-white/20 hover:text-white transition-colors"
                        >
                            <X className="h-5 w-5" />
                        </button>
                    )}
                </div>
                {searchTerm && !selectedPendingId && (
                    <div className="absolute -bottom-6 left-6 animate-in slide-in-from-top-1 flex items-center gap-4">
                        <span className="text-[10px] font-black uppercase tracking-widest text-brand-primary bg-brand-primary/10 px-3 py-1 rounded-full border border-brand-primary/20">
                            Filtrando: {filteredPendingItems.length} resultados
                        </span>
                        {filteredPendingItems.length > 0 && (
                            <button
                                onClick={() => {
                                    const allIds = filteredPendingItems.map(i => i.id);
                                    setSelectedIds(prev => Array.from(new Set([...prev, ...allIds])));
                                }}
                                className="text-[10px] font-black uppercase tracking-widest text-white/65 hover:text-brand-primary transition-colors flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/5 hover:border-brand-primary/20"
                            >
                                <CheckCircle2 className="h-3 w-3" /> Seleccionar Todos los Resultados
                            </button>
                        )}
                    </div>
                )}
            </div>

            {/* Controles y Filtros del Purgatorio */}
            <div className={`space-y-4 bg-white/[0.01] border border-white/5 p-5 rounded-3xl backdrop-blur-md transition-all duration-500 ${selectedPendingId ? 'opacity-20 grayscale pointer-events-none' : 'opacity-100'}`}>
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    {/* 1. Selector de Diseño / Layout Toggle */}
                    <div className="flex items-center gap-2">
                        <span className="text-[10px] font-black uppercase tracking-widest text-white/50 mr-2">Diseño:</span>
                        <button
                            onClick={() => setViewLayout('mazo')}
                            className={`px-3 py-1.5 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all flex items-center gap-1.5 ${viewLayout === 'mazo' ? 'bg-brand-primary text-white shadow-lg shadow-brand-primary/20' : 'bg-white/5 text-white/60 hover:text-white hover:bg-white/10'}`}
                        >
                            <LayoutGrid className="h-3 w-3" />
                            Modo Mazo
                        </button>
                        <button
                            onClick={() => setViewLayout('lista')}
                            className={`px-3 py-1.5 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all flex items-center gap-1.5 ${viewLayout === 'lista' ? 'bg-brand-primary text-white shadow-lg shadow-brand-primary/20' : 'bg-white/5 text-white/60 hover:text-white hover:bg-white/10'}`}
                        >
                            <LayoutList className="h-3 w-3" />
                            Modo Listado
                        </button>
                    </div>

                    {/* 2. Ordenación del Mazo */}
                    <div className="flex items-center gap-2">
                        <span id="purgatory-sort-label" className="text-[10px] font-black uppercase tracking-widest text-white/50 mr-2">Ordenar por:</span>
                        <select
                            value={sortBy}
                            onChange={(e: any) => setSortBy(e.target.value)}
                            aria-labelledby="purgatory-sort-label"
                            className="bg-black/60 border border-white/10 rounded-xl px-3 py-1.5 text-[10px] font-black uppercase tracking-widest text-white outline-none focus:border-brand-primary/50 transition-all cursor-pointer"
                        >
                            <option value="highest_match">Mayor Probabilidad</option>
                            <option value="lowest_match">Menor Probabilidad</option>
                            <option value="newest">Más Nuevas Primero</option>
                            <option value="oldest">Más Antiguas Primero</option>
                        </select>
                    </div>
                </div>

                <div className="h-px bg-white/5 my-2"></div>

                <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
                    {/* 3. Filtro de Tiendas (Chips Dinámicos) */}
                    <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-[10px] font-black uppercase tracking-widest text-white/50 mr-2">Tienda:</span>
                        <button
                            onClick={() => setShopFilter('all')}
                            className={`px-2.5 py-1 rounded-lg text-[9px] font-black uppercase tracking-widest transition-all ${shopFilter === 'all' ? 'bg-brand-secondary/20 text-brand-secondary border border-brand-secondary/30' : 'text-white/40 hover:text-white bg-white/5 border border-transparent'}`}
                        >
                            Todas
                        </button>
                        {uniqueShopsInPending.map(shop => (
                            <button
                                key={shop}
                                onClick={() => setShopFilter(shop)}
                                className={`px-2.5 py-1 rounded-lg text-[9px] font-black uppercase tracking-widest transition-all ${shopFilter === shop ? 'bg-brand-secondary/20 text-brand-secondary border border-brand-secondary/30' : 'text-white/40 hover:text-white bg-white/5 border border-transparent'}`}
                            >
                                {shop}
                            </button>
                        ))}
                    </div>

                    <div className="hidden md:block h-4 w-px bg-white/10"></div>

                    {/* 4. Filtro de Tránsito */}
                    <div className="flex items-center gap-3">
                        <label className="flex items-center gap-2 cursor-pointer select-none">
                            <input
                                type="checkbox"
                                checked={enableTransitFilter}
                                onChange={(e) => {
                                    setEnableTransitFilter(e.target.checked);
                                    setCurrentPage(1);
                                }}
                                className="h-4 w-4 rounded border-white/10 bg-white/5 text-brand-primary focus:ring-brand-primary"
                            />
                            <span className="text-[9px] font-black uppercase tracking-widest text-white/65 flex items-center gap-1">
                                <span className="h-1 w-1 rounded-full bg-orange-500 animate-pulse"></span>
                                Tránsito (Expr.)
                            </span>
                        </label>

                        {enableTransitFilter && (
                            <div className="flex items-center gap-1.5 animate-in slide-in-from-left-4 duration-300">
                                <button
                                    onClick={() => { setTransitType('all'); setCurrentPage(1); }}
                                    className={`px-2 py-0.5 rounded-md text-[8px] font-black uppercase tracking-widest transition-all ${transitType === 'all' ? 'bg-brand-primary/20 text-white border border-brand-primary/30' : 'text-white/55 hover:text-white bg-white/5 border border-transparent'}`}
                                >
                                    Todos
                                </button>
                                <button
                                    onClick={() => { setTransitType('retail'); setCurrentPage(1); }}
                                    className={`px-2 py-0.5 rounded-md text-[8px] font-black uppercase tracking-widest transition-all ${transitType === 'retail' ? 'bg-brand-primary/20 text-white border border-brand-primary/30' : 'text-white/55 hover:text-white bg-white/5 border border-transparent'}`}
                                >
                                    Retail
                                </button>
                                <button
                                    onClick={() => { setTransitType('p2p'); setCurrentPage(1); }}
                                    className={`px-2 py-0.5 rounded-md text-[8px] font-black uppercase tracking-widest transition-all ${transitType === 'p2p' ? 'bg-brand-primary/20 text-white border border-brand-primary/30' : 'text-white/55 hover:text-white bg-white/5 border border-transparent'}`}
                                >
                                    P2P
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>


            {/* Purgatory List */}
            <div className="grid grid-cols-1 gap-6">
                {isLoadingPending ? (
                    <PowerSwordLoader variant="fullScreen" text="Escaneando el abismo..." />
                ) : pendingItems?.length === 0 ? (
                    <div className="flex min-h-[300px] flex-col items-center justify-center gap-6 rounded-3xl border-2 border-dashed border-white/5 bg-white/[0.02] text-center">
                        <CheckCircle2 className="h-12 w-12 text-green-500/40" />
                        <div className="max-w-xs space-y-1">
                            <p className="text-lg font-bold text-white/60">Purgatorio Vacío</p>
                            <p className="text-sm text-white/60">Todas las reliquias han sido purificadas o descartadas.</p>
                        </div>
                    </div>
                                ) : viewLayout === 'mazo' ? (
                    <div className="flex flex-col items-center justify-center py-6 min-h-[600px] relative w-full">
                        {deckItems.length === 0 ? (
                            <div className="flex flex-col items-center justify-center gap-4 text-center py-12 rounded-3xl border border-dashed border-white/10 bg-white/[0.01] w-full max-w-xl">
                                <CheckCircle2 className="h-12 w-12 text-green-500/40 animate-bounce" />
                                <div className="space-y-1">
                                    <p className="text-lg font-black text-white/60 uppercase tracking-widest">Fin del Mazo</p>
                                    <p className="text-xs text-white/65">Has procesado todas las cartas filtradas en esta ronda.</p>
                                </div>
                            </div>
                        ) : (
                            <div className="relative w-full max-w-xl flex flex-col items-center">
                                {/* Instrucciones rápidas en cabecera */}
                                <div className="flex flex-wrap items-center justify-center gap-x-4 gap-y-2 mb-6 text-[9px] font-black uppercase tracking-widest text-white/40 bg-white/[0.02] border border-white/5 px-4 py-2 rounded-full backdrop-blur-md select-none">
                                    <span>⬅️ [A] Descartar</span>
                                    <span>➡️ [D] Vincular</span>
                                    <span>⬇️ [S] Re-encolar</span>
                                    <span>⬆️ [N] Vintage</span>
                                    <span>🔍 [E] Buscar</span>
                                </div>

                                <div className="relative w-full h-[540px] flex items-center justify-center">
                                    <AnimatePresence>
                                        {deckItems.slice(0, 3).reverse().map((item) => {
                                            const originalIndex = deckItems.slice(0, 3).indexOf(item);
                                            const isTop = originalIndex === 0;
                                            return (
                                                <SwipeCard
                                                    key={item.id}
                                                    item={item}
                                                    isTop={isTop}
                                                    originalIndex={originalIndex}
                                                    handleApproveCard={handleApproveCard}
                                                    handleDiscardCard={handleDiscardCard}
                                                    handleSwipeDown={handleSwipeDown}
                                                    openClassifyModal={openClassifyModal}
                                                    isSearchingAssociation={isSearchingAssociation}
                                                    setIsSearchingAssociation={setIsSearchingAssociation}
                                                    associatedProductId={associatedProductId}
                                                    setAssociatedProductId={setAssociatedProductId}
                                                    manualSearchTerm={manualSearchTerm}
                                                    setManualSearchTerm={setManualSearchTerm}
                                                    filteredProducts={filteredProducts}
                                                    allProducts={products || []}
                                                />
                                            );
                                        })}
                                    </AnimatePresence>
                                </div>
                            </div>
                        )}
                    </div>
                ) : (
                    <PurgatoryListView
                        paginatedItems={paginatedItems}
                        selectedIds={selectedIds}
                        setSelectedIds={setSelectedIds}
                        currentPage={currentPage}
                        setCurrentPage={setCurrentPage}
                        totalPages={totalPages}
                        startIndex={startIndex}
                        totalItems={totalItems}
                        itemsPerPage={itemsPerPage}
                        discardMutation={discardMutation}
                        selectedPendingId={selectedPendingId}
                        setSelectedPendingId={setSelectedPendingId}
                        manualSearchTerm={manualSearchTerm}
                        setManualSearchTerm={setManualSearchTerm}
                        filteredProducts={filteredProducts}
                        matchMutation={matchMutation}
                        openClassifyModal={openClassifyModal}
                        matchVintageMutation={matchVintageMutation}
                    />
                )}
            </div>

            {/* Bulk Action Bar */}
            {
                selectedIds.length > 0 && (
                    <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 animate-in slide-in-from-bottom-8 duration-500">
                        <div className="bg-black/80 backdrop-blur-2xl border border-brand-primary/30 rounded-full px-8 py-4 flex items-center gap-8 shadow-[0_0_50px_rgba(14,165,233,0.3)]">
                            <div className="flex flex-col">
                                <span className="text-[10px] font-black text-brand-primary uppercase tracking-widest">Seleccionados</span>
                                <span className="text-xl font-black text-white">{selectedIds.length} <span className="text-sm text-white/65">ITEMS</span></span>
                            </div>
                            <div className="h-8 w-px bg-white/10"></div>
                            <div className="flex items-center gap-4">
                                <button
                                    onClick={() => setSelectedIds([])}
                                    className="text-xs font-black text-white/65 hover:text-white uppercase tracking-widest transition-all"
                                >
                                    Cancelar
                                </button>
                                <button
                                    onClick={() => discardBulkMutation.mutate(selectedIds)}
                                    disabled={discardBulkMutation.isPending}
                                    className="bg-red-500 hover:bg-red-600 text-white px-8 py-3 rounded-full text-xs font-black uppercase tracking-widest transition-all shadow-lg shadow-red-500/20 flex items-center gap-2 disabled:opacity-50"
                                >
                                    {discardBulkMutation.isPending ? <RefreshCcw className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
                                    Descartar Seleccionados
                                </button>
                            </div>
                        </div>
                    </div>
                )
            }

            {/* Forensic Inspection Modal */}
            <ForensicModal
                showForensic={showForensic}
                forensicModalRef={forensicModalRef}
                failedActions={failedActions}
                setFailedActions={setFailedActions}
                setShowForensic={setShowForensic}
                setPendingActions={setPendingActions}
                setLocallyProcessedIds={setLocallyProcessedIds}
            />

            {/* Modal de Clasificación Vintage / Nueva Eternia con Nombre Personalizado */}
            <VintageClassifyModal
                isVintageModalOpen={isVintageModalOpen}
                vintageModalRef={vintageModalRef}
                setIsVintageModalOpen={setIsVintageModalOpen}
                selectedDivision={selectedDivision}
                setSelectedDivision={setSelectedDivision}
                vintageModalItemName={vintageModalItemName}
                vintageCustomName={vintageCustomName}
                setVintageCustomName={setVintageCustomName}
                handleInputChange={handleInputChange}
                showCustomSubCategoryInput={showCustomSubCategoryInput}
                setShowCustomSubCategoryInput={setShowCustomSubCategoryInput}
                customSubCategory={customSubCategory}
                setCustomSubCategory={setCustomSubCategory}
                matchMiscMutation={matchMiscMutation}
                vintageModalItemId={vintageModalItemId}
                vintageModalSuggestionsToDisplay={vintageModalSuggestionsToDisplay}
                selectedVintageProductId={selectedVintageProductId}
                setSelectedVintageProductId={setSelectedVintageProductId}
                matchVintageMutation={matchVintageMutation}
            />

            {/* Phase 40: Wallapop Oracle Bridge - Quick Preview */}
            {
                previewUrl && (
                    <QuickPreviewModal
                        url={previewUrl}
                        onClose={() => setPreviewUrl(null)}
                    />
                )
            }
        </div >
    );
});

export default Purgatory;
