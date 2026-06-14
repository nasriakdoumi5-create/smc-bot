const BASE = 'https://api.printful.com';

async function apiFetch(path, options = {}) {
  const key = process.env.PRINTFUL_API_KEY;
  if (!key) throw new Error('PRINTFUL_API_KEY not set');

  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${key}`,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  const data = await res.json();
  if (!res.ok) throw new Error(`Printful ${res.status}: ${JSON.stringify(data)}`);
  return data.result;
}

// In-memory cache (resets per cold start — acceptable for serverless)
let variantCache = null;

export async function getSyncProducts() {
  return apiFetch('/store/products?limit=100');
}

export async function getSyncProductDetail(id) {
  return apiFetch(`/store/products/${id}`);
}

export async function buildVariantMap() {
  if (variantCache) return variantCache;

  const products = await getSyncProducts();
  const map = {}; // lowercase variant name → sync_variant_id

  for (const prod of products) {
    const detail = await getSyncProductDetail(prod.id);
    for (const v of detail.sync_variants || []) {
      map[v.name.toLowerCase()] = v.id;
    }
  }

  variantCache = map;
  return map;
}

export function findVariantId(variantMap, modelName) {
  const model = modelName.toLowerCase();

  // Exact substring match
  for (const [name, id] of Object.entries(variantMap)) {
    if (name.includes(model)) return id;
  }

  // Keyword match (e.g. "S24" matches "samsung galaxy s24")
  const keywords = model.split(/\s+/).filter((w) => w.length > 1);
  for (const [name, id] of Object.entries(variantMap)) {
    if (keywords.every((kw) => name.includes(kw))) return id;
  }

  return null;
}

const COUNTRY_CODES = {
  Germany: 'DE',
  France: 'FR',
  Netherlands: 'NL',
  Spain: 'ES',
  Italy: 'IT',
  Austria: 'AT',
  Belgium: 'BE',
  Sweden: 'SE',
  Denmark: 'DK',
  Poland: 'PL',
  Portugal: 'PT',
  Finland: 'FI',
  Ireland: 'IE',
  'Czech Republic': 'CZ',
  'United Kingdom': 'GB',
  UK: 'GB',
  Switzerland: 'CH',
  Norway: 'NO',
  'Other EU': 'DE',
};

export function toCountryCode(name) {
  return COUNTRY_CODES[name] || name;
}

/**
 * Create a Printful order.
 * recipient: { name, email, address, city, country, zip }
 * items: [{ id, model, qty, price }]
 * orderNum: string (PW...)
 */
export async function createPrintfulOrder({ recipient, items, orderNum }) {
  const variantMap = await buildVariantMap();

  const printfulItems = items.map((item) => {
    const variantId = findVariantId(variantMap, item.model);
    if (!variantId) {
      throw new Error(`No Printful variant found for model: "${item.model}". Available: ${Object.keys(variantMap).join(', ')}`);
    }
    return {
      sync_variant_id: variantId,
      quantity: item.qty,
      retail_price: Number(item.price).toFixed(2),
    };
  });

  return apiFetch('/orders', {
    method: 'POST',
    body: JSON.stringify({
      external_id: orderNum,
      recipient: {
        name: recipient.name,
        email: recipient.email,
        address1: recipient.address,
        city: recipient.city,
        country_code: toCountryCode(recipient.country),
        zip: recipient.zip,
      },
      items: printfulItems,
    }),
  });
}
