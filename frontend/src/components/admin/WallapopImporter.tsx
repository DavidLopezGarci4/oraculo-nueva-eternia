import React, { useState } from 'react';
import { Upload, CheckCircle, AlertCircle, Loader2, ExternalLink } from 'lucide-react';
import { motion } from 'framer-motion';
import { importWallapopProducts, parseWallapopText } from '../../api/wallapop';
import type { WallapopProduct } from '../../api/wallapop';

const WallapopImporter: React.FC = () => {
    const [inputText, setInputText] = useState('');
    const [parsedProducts, setParsedProducts] = useState<WallapopProduct[]>([]);
    const [isImporting, setIsImporting] = useState(false);
    const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

    const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const text = e.target.value;
        setInputText(text);
        setResult(null);

        // Parsear en tiempo real
        const products = parseWallapopText(text);
        setParsedProducts(products);
    };

    const handleImport = async () => {
        if (parsedProducts.length === 0) {
            setResult({ success: false, message: 'No se detectaron productos válidos' });
            return;
        }

        setIsImporting(true);
        setResult(null);

        try {
            const response = await importWallapopProducts(parsedProducts);
            setResult({
                success: true,
                message: `✅ ${response.imported} productos importados al Purgatorio`
            });
            setInputText('');
            setParsedProducts([]);
        } catch (error) {
            setResult({
                success: false,
                message: '❌ Error al importar. Verifica la conexión con el servidor.'
            });
        } finally {
            setIsImporting(false);
        }
    };

    return (
        <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6">
            <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-green-500/20 rounded-lg">
                    <Upload className="w-5 h-5 text-green-400" />
                </div>
                <div>
                    <h3 className="text-lg font-semibold text-white">Importador de Wallapop</h3>
                    <p className="text-sm text-slate-400">Pega los datos de productos de Wallapop</p>
                </div>
            </div>

            {/* Instrucciones */}
            <div className="bg-slate-900/50 rounded-lg p-4 mb-4 text-sm">
                <p className="text-amber-400 font-medium mb-2">📋 Formato aceptado:</p>
                <code className="text-slate-300 block mb-2">
                    Nombre del producto | Precio | URL
                </code>
                <p className="text-slate-500 text-xs">
                    También puedes pegar solo URLs de Wallapop (una por línea)
                </p>
            </div>

            {/* Área de texto */}
            <textarea
                value={inputText}
                onChange={handleTextChange}
                placeholder="He-Man Origins | 25.00 | https://es.wallapop.com/item/he-man-123&#10;Skeletor | 18.50 | https://es.wallapop.com/item/skeletor-456"
                className="w-full h-40 bg-slate-900 border border-slate-600 rounded-lg p-4 text-white placeholder-slate-500 text-sm font-mono resize-none focus:outline-none focus:border-amber-500"
            />

            {/* Preview de productos detectados */}
            {parsedProducts.length > 0 && (
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-4 p-4 bg-slate-900/50 rounded-lg border border-slate-600"
                >
                    <p className="text-sm text-slate-400 mb-3">
                        <span className="text-amber-400 font-bold">{parsedProducts.length}</span> productos detectados:
                    </p>
                    <div className="max-h-32 overflow-y-auto space-y-2">
                        {parsedProducts.slice(0, 5).map((p, i) => (
                            <div key={i} className="flex items-center justify-between text-sm">
                                <span className="text-white truncate max-w-[60%]">{p.title}</span>
                                <span className="text-green-400">{p.price > 0 ? `${p.price}€` : '—'}</span>
                            </div>
                        ))}
                        {parsedProducts.length > 5 && (
                            <p className="text-slate-500 text-xs">...y {parsedProducts.length - 5} más</p>
                        )}
                    </div>
                </motion.div>
            )}

            {/* Resultado */}
            {result && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className={`mt-4 p-4 rounded-lg flex items-center gap-3 ${result.success
                        ? 'bg-green-500/10 border border-green-500/30'
                        : 'bg-red-500/10 border border-red-500/30'
                        }`}
                >
                    {result.success ? (
                        <CheckCircle className="w-5 h-5 text-green-400" />
                    ) : (
                        <AlertCircle className="w-5 h-5 text-red-400" />
                    )}
                    <span className={result.success ? 'text-green-400' : 'text-red-400'}>
                        {result.message}
                    </span>
                </motion.div>
            )}

            {/* Botón de importar */}
            <button
                onClick={handleImport}
                disabled={parsedProducts.length === 0 || isImporting}
                className={`mt-4 w-full py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all ${parsedProducts.length === 0 || isImporting
                    ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-amber-500 to-orange-500 text-white hover:from-amber-400 hover:to-orange-400'
                    }`}
            >
                {isImporting ? (
                    <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Importando...
                    </>
                ) : (
                    <>
                        <Upload className="w-5 h-5" />
                        Importar {parsedProducts.length > 0 ? `(${parsedProducts.length})` : ''} al Purgatorio
                    </>
                )}
            </button>

            {/* Link a Wallapop */}
            <a
                href="https://es.wallapop.com/app/search?keywords=motu%20origins"
                target="_blank"
                rel="noopener noreferrer"
                className="mt-3 flex items-center justify-center gap-2 text-sm text-slate-400 hover:text-amber-400 transition-colors"
            >
                <ExternalLink className="w-4 h-4" />
                Abrir Wallapop en nueva pestaña
            </a>
        </div>
    );
};

export default WallapopImporter;
