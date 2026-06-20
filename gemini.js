/**
 * Gemini AI — فلتر الإشارات
 * يُستخدم فقط للإشارات الضعيفة (score 3/5)
 * Gemini Flash مجاني: 15 طلب/دقيقة، 1M token/يوم
 */

const API_KEY = process.env.GEMINI_API_KEY;
const URL     = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${API_KEY}`;

/**
 * يسأل Gemini إذا كانت الإشارة تستحق الدخول
 * يُعيد: { confirm: true/false, reason: string }
 */
export async function validateSignal(signal, symbolName) {
  if (!API_KEY) return { confirm: true, reason: 'Gemini غير مُفعَّل' };

  const conds = Object.entries(signal.conditions)
    .map(([k, v]) => `${v ? '✅' : '❌'} ${k}`)
    .join('\n');

  const prompt =
`أنت محلل تقني متخصص في العقود الآجلة (Futures).
بناءً على هذه البيانات الفنية، هل توصي بالدخول في الصفقة؟

الرمز: ${symbolName}
الإشارة: ${signal.type}
السعر: ${signal.price}
الاتجاه العام (1H): ${signal.type === 'LONG' ? 'صاعد (EMA50 > EMA200)' : 'هابط (EMA50 < EMA200)'}
EMA21 (5M): ${signal.e21_5m}
EMA21 (15M): ${signal.e21_15m || 'غير متاح'}
RSI: ${signal.rsi}
ATR: ${signal.atr}
النقاط: ${signal.score}/5
SL: ${signal.sl} | TP1: ${signal.tp1} | R:R 1:2

الشروط:
${conds}

أجب بالتنسيق التالي فقط (سطرين):
DECISION: تأكيد أو تجاهل
REASON: سبب مختصر جداً (10 كلمات كحد أقصى)`;

  try {
    const res = await fetch(URL, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }],
        generationConfig: { maxOutputTokens: 80, temperature: 0.1 },
      }),
    });

    const data = await res.json();
    const text = data?.candidates?.[0]?.content?.parts?.[0]?.text?.trim() || '';

    const decisionMatch = text.match(/DECISION:\s*(تأكيد|تجاهل)/i);
    const reasonMatch   = text.match(/REASON:\s*(.+)/i);

    const confirm = decisionMatch ? decisionMatch[1].includes('تأكيد') : true;
    const reason  = reasonMatch   ? reasonMatch[1].trim() : text.slice(0, 60);

    console.log(`[Gemini] ${symbolName} ${signal.type} → ${confirm ? '✅ تأكيد' : '❌ تجاهل'} | ${reason}`);
    return { confirm, reason };

  } catch (err) {
    console.error('[Gemini] خطأ:', err.message);
    return { confirm: true, reason: 'خطأ في Gemini — تم التجاهل' };
  }
}
