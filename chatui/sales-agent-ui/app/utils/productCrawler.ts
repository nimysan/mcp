import axios from 'axios';
import * as cheerio from 'cheerio';

// 调试日志函数
function debug(message: string, data?: unknown) {
  console.log(`[ProductCrawler] ${message}`, data ? JSON.stringify(data, null, 2) : '');
}

interface ProductDetail {
  price: number;
  Currency: string;
  title?: string;
  description?: string;
  specifications?: Record<string, string>;
}

export async function crawlProductDetail(productUrl: string): Promise<ProductDetail> {
  debug('开始爬取产品信息', { url: productUrl });
  
  try {
    // 发送HTTP请求获取页面内容
    debug('发送HTTP请求');
    const response = await axios.get(productUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      }
    });
    const html = response.data as string;
    const $ = cheerio.load(html) as cheerio.CheerioAPI;
    debug('成功加载HTML');

    // 提取产品信息
    debug('开始提取产品信息');
    const price = extractPrice($);
    const currency = extractCurrency($);
    const title = $('.product__title').text().trim();
    const description = $('.product__description').text().trim();
    
    debug('提取到的基本信息', { price, currency, title });
    
    // 提取规格信息
    const specifications: Record<string, string> = {};
    $('div.product-specifications li').each((index: number, elem: cheerio.Element) => {
      const key = $(elem).find('.spec-key').text().trim();
      const value = $(elem).find('.spec-value').text().trim();
      if (key && value) {
        specifications[key] = value;
      }
    });

    const result = {
      price: price || 0,
      Currency: currency || 'USD',
      title,
      description,
      specifications
    };
    
    debug('爬取完成，返回结果', result);
    return result;
    
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '未知错误';
    debug('爬取过程中发生错误', { error: errorMessage });
    console.error('Error crawling product details:', {
      url: productUrl,
      error: errorMessage,
      stack: error instanceof Error ? error.stack : undefined
    });
    // 返回默认值
    return {
      price: 0,
      Currency: 'USD'
    };
  }
}

function extractPrice($: cheerio.CheerioAPI): number {
  type PriceSelector = {
    selector: string;
    regex?: RegExp;
  };
  debug('开始提取价格');
  // 尝试不同的选择器来找到价格
  const priceSelectors: PriceSelector[] = [
    { selector: '.product__price' },
    { selector: '[data-product-price]' },
    { selector: '.price-item--regular' },
    { selector: '.price', regex: /[\d,.]+/ }
  ];

  for (const { selector, regex } of priceSelectors) {
    const element = $(selector).first();
    if (!element.length) continue;
    
    const priceText = element.text().trim();
    debug('尝试价格选择器', { selector, foundText: priceText });
    
    if (priceText) {
      // 提取数字
      const price = parseFloat(
        regex 
          ? priceText.match(regex)?.[0]?.replace(/[^0-9.]/g, '') || '0'
          : priceText.replace(/[^0-9.]/g, '')
      );
      if (!isNaN(price)) {
        debug('成功提取价格', { price });
        return price;
      }
    }
  }

  debug('未找到有效价格，返回默认值0');
  return 0;
}

function extractCurrency($: cheerio.CheerioAPI): string {
  debug('开始提取货币信息');
  // 尝试从价格文本中提取货币符号
  const currencySymbol = $('.product__price').first().text().trim().replace(/[0-9.]/g, '').trim();
  debug('提取到的货币符号', { symbol: currencySymbol });
  
  // 货币符号映射
  const currencyMap: Record<string, string> = {
    '$': 'USD',
    '€': 'EUR',
    '£': 'GBP',
    '¥': 'JPY',
  };

  const currency = currencyMap[currencySymbol] || 'USD';
  debug('确定的货币类型', { currency });
  return currency;
}
