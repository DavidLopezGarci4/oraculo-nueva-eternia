import type { Product } from '../../api/collection';

export const buildSearchQuery = (product: Product, isVintageOnly: boolean): string => {
    const identifiers: string[] = [];
    if (product.ean) identifiers.push(product.ean);
    else if (product.upc) identifiers.push(product.upc);

    if (product.figure_id) {
        identifiers.push(product.figure_id);
    }

    let baseName = product.name;
    const parenthesisRegex = /\(([^)]+)\)/g;
    const matches = [...baseName.matchAll(parenthesisRegex)].map(m => m[1]);
    baseName = baseName.replace(parenthesisRegex, '').trim();

    let lineContext = "";
    if (isVintageOnly || product.is_vintage) {
        lineContext = '"masters of the universe" "vintage" (80s OR retro)';
    } else {
        const subCat = product.sub_category?.toLowerCase() || "";
        if (subCat.includes("turtles")) {
            lineContext = '"turtles of grayskull"';
        } else if (subCat.includes("origins")) {
            lineContext = '"motu origins" OR "masters of the universe origins"';
        } else {
            lineContext = '"masters of the universe origins"';
        }
    }

    let variantContext = "";
    if (product.variant_name && product.variant_name.toLowerCase() !== "standard") {
        variantContext = `"${product.variant_name}"`;
    }

    const parts: string[] = [`"${baseName}"`];
    const contextTerms: string[] = [];

    if (identifiers.length > 0) {
        contextTerms.push(...identifiers.map(id => `"${id}"`));
    }
    if (matches.length > 0) {
        contextTerms.push(...matches.map(m => `"${m}"`));
    }

    let query = "";
    if (contextTerms.length > 0) {
        query = `(${parts[0]} OR ${contextTerms.join(" OR ")})`;
    } else {
        query = parts[0];
    }

    query += ` AND (${lineContext})`;

    if (variantContext) {
        query += ` AND ${variantContext}`;
    }

    query += ` AND "Mattel"`;

    return `https://www.google.com/search?q=${encodeURIComponent(query)}`;
};
